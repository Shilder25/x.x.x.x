import os
import json
from typing import Dict, Optional
from datetime import datetime
from openai import OpenAI
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def is_rate_limit_error(exception: BaseException) -> bool:
    error_msg = str(exception)
    return (
        "429" in error_msg
        or "RATELIMIT_EXCEEDED" in error_msg
        or "quota" in error_msg.lower()
        or "rate limit" in error_msg.lower()
        or (hasattr(exception, "status_code") and exception.status_code == 429)
        or (hasattr(exception, 'status') and exception.status == 429)
    )


def validate_and_normalize_prediction(prediction: Dict, firm_name: str) -> Dict:
    """
    Valida y normaliza la predicción del LLM, aplicando defaults para campos faltantes.
    
    Args:
        prediction: Dict con la respuesta JSON del LLM
        firm_name: Nombre de la firma para logging
    
    Returns:
        Dict con todos los campos requeridos (con defaults si faltan)
    """
    normalized = prediction.copy()
    
    required_fields = {
        'probabilidad_final_prediccion': 0.5,
        'postura_riesgo': 'NEUTRAL',
        'nivel_confianza': 50,
        'direccion_preliminar': 'NEUTRAL'
    }
    
    for field, default in required_fields.items():
        if field not in normalized or normalized[field] is None:
            print(f"[{firm_name}] WARNING: Campo '{field}' faltante, usando default: {default}")
            normalized[field] = default
    
    five_area_scores = {
        'sentiment_score': (0, 5, 'No sentiment analysis provided'),
        'news_score': (0, 5, 'No news analysis provided'),
        'technical_score': (0, 5, 'No technical analysis provided'),
        'fundamental_score': (0, 5, 'No fundamental analysis provided'),
        'volatility_score': (0, 5, 'No volatility analysis provided')
    }
    
    for score_field, (min_val, default_val, default_text) in five_area_scores.items():
        analysis_field = score_field.replace('_score', '_analysis')
        
        if score_field not in normalized or normalized[score_field] is None:
            print(f"[{firm_name}] WARNING: Campo '{score_field}' faltante, usando default: {default_val}")
            normalized[score_field] = default_val
        else:
            score = normalized[score_field]
            if not isinstance(score, (int, float)) or score < 0 or score > 10:
                print(f"[{firm_name}] WARNING: '{score_field}' inválido ({score}), corrigiendo a {default_val}")
                normalized[score_field] = default_val
        
        if analysis_field not in normalized or not normalized[analysis_field]:
            normalized[analysis_field] = default_text
    
    prob = normalized.get('probabilidad_final_prediccion', 0.5)
    if not isinstance(prob, (int, float)) or prob < 0.0 or prob > 1.0:
        print(f"[{firm_name}] WARNING: probabilidad_final_prediccion inválida ({prob}), corrigiendo a 0.5")
        normalized['probabilidad_final_prediccion'] = 0.5
    
    confidence = normalized.get('nivel_confianza', 50)
    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
        print(f"[{firm_name}] WARNING: nivel_confianza inválido ({confidence}), corrigiendo a 50")
        normalized['nivel_confianza'] = 50
    
    return normalized


class TradingFirm:
    def __init__(self, firm_name: str):
        self.firm_name = firm_name
        self.total_tokens = 0
        self.estimated_cost = 0.0
    
    def generate_prediction(self, prompt: str) -> Dict:
        raise NotImplementedError("Subclasses must implement generate_prediction")
    
    def _estimate_cost(self, tokens: int, input_cost_per_1k: float = 0.01, output_cost_per_1k: float = 0.03) -> float:
        input_tokens = int(tokens * 0.6)
        output_tokens = int(tokens * 0.4)
        return (input_tokens / 1000 * input_cost_per_1k) + (output_tokens / 1000 * output_cost_per_1k)


class ChatGPTFirm(TradingFirm):
    def __init__(self):
        super().__init__("ChatGPT")
        # Use direct OpenAI API (works on both Replit and Railway)
        api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")  # None if not on Replit
        
        if base_url:
            # On Replit with AI Integrations
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            # On Railway or standalone (uses standard OpenAI API)
            self.client = OpenAI(api_key=api_key)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def generate_prediction(self, prompt: str) -> Dict:
        try:
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst. Respond in valid JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            
            self.total_tokens += tokens
            self.estimated_cost += self._estimate_cost(tokens, 0.005, 0.015)
            
            prediction = json.loads(content)
            prediction = validate_and_normalize_prediction(prediction, self.firm_name)
            prediction['tokens_used'] = tokens
            prediction['estimated_cost'] = self._estimate_cost(tokens, 0.005, 0.015)
            
            return prediction
        except Exception as e:
            return {
                'error': str(e),
                'firm_name': self.firm_name,
                'timestamp': datetime.now().isoformat()
            }


class GeminiFirm(TradingFirm):
    def __init__(self):
        super().__init__("Gemini")
        # Use direct Google Gemini API (works on both Replit and Railway)
        api_key = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        base_url = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")
        
        if base_url:
            # On Replit with AI Integrations
            self.client = genai.Client(
                api_key=api_key,
                http_options={'api_version': '', 'base_url': base_url}
            )
        else:
            # On Railway or standalone (uses standard Google API)
            self.client = genai.Client(api_key=api_key)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def generate_prediction(self, prompt: str) -> Dict:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            content = response.text or "{}"
            tokens = 1000
            
            self.total_tokens += tokens
            self.estimated_cost += self._estimate_cost(tokens, 0.002, 0.006)
            
            prediction = json.loads(content)
            prediction = validate_and_normalize_prediction(prediction, self.firm_name)
            prediction['tokens_used'] = tokens
            prediction['estimated_cost'] = self._estimate_cost(tokens, 0.002, 0.006)
            
            return prediction
        except Exception as e:
            return {
                'error': str(e),
                'firm_name': self.firm_name,
                'timestamp': datetime.now().isoformat()
            }


class QwenFirm(TradingFirm):
    def __init__(self):
        super().__init__("Qwen")
        api_key = os.environ.get("QWEN_API_KEY")
        if not api_key:
            print(f"[{self.firm_name}] WARNING: QWEN_API_KEY not configured")
        self.client = OpenAI(
            api_key=api_key or "not-configured",
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def generate_prediction(self, prompt: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="qwen-max-2025-01-25",
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst. Respond in valid JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            
            self.total_tokens += tokens
            self.estimated_cost += self._estimate_cost(tokens, 0.003, 0.009)
            
            prediction = json.loads(content)
            prediction = validate_and_normalize_prediction(prediction, self.firm_name)
            prediction['tokens_used'] = tokens
            prediction['estimated_cost'] = self._estimate_cost(tokens, 0.003, 0.009)
            
            return prediction
        except Exception as e:
            return {
                'error': str(e),
                'firm_name': self.firm_name,
                'timestamp': datetime.now().isoformat(),
                'note': 'Qwen API key may not be configured'
            }


class DeepseekFirm(TradingFirm):
    def __init__(self):
        super().__init__("Deepseek")
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print(f"[{self.firm_name}] WARNING: DEEPSEEK_API_KEY not configured")
        self.client = OpenAI(
            api_key=api_key or "not-configured",
            base_url="https://api.deepseek.com"
        )
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def generate_prediction(self, prompt: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst. Respond in valid JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            
            self.total_tokens += tokens
            self.estimated_cost += self._estimate_cost(tokens, 0.001, 0.002)
            
            prediction = json.loads(content)
            prediction = validate_and_normalize_prediction(prediction, self.firm_name)
            prediction['tokens_used'] = tokens
            prediction['estimated_cost'] = self._estimate_cost(tokens, 0.001, 0.002)
            
            return prediction
        except Exception as e:
            return {
                'error': str(e),
                'firm_name': self.firm_name,
                'timestamp': datetime.now().isoformat(),
                'note': 'Deepseek API key may not be configured'
            }


class GrokFirm(TradingFirm):
    def __init__(self):
        super().__init__("Grok")
        # Using xAI API endpoint as per blueprint
        api_key = os.environ.get("XAI_API_KEY")
        if not api_key:
            print(f"[{self.firm_name}] WARNING: XAI_API_KEY not configured")
        self.client = OpenAI(
            base_url="https://api.x.ai/v1",
            api_key=api_key or "not-configured"
        )
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def generate_prediction(self, prompt: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="grok-2-1212",
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst. Respond in valid JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if response.usage else 0
            
            self.total_tokens += tokens
            self.estimated_cost += self._estimate_cost(tokens, 0.002, 0.01)
            
            prediction = json.loads(content)
            prediction = validate_and_normalize_prediction(prediction, self.firm_name)
            prediction['tokens_used'] = tokens
            prediction['estimated_cost'] = self._estimate_cost(tokens, 0.002, 0.01)
            
            return prediction
        except Exception as e:
            return {
                'error': str(e),
                'firm_name': self.firm_name,
                'timestamp': datetime.now().isoformat(),
                'note': 'Grok (xAI) API key may not be configured'
            }


class FirmOrchestrator:
    def __init__(self):
        self.firms = {
            'ChatGPT': ChatGPTFirm(),
            'Gemini': GeminiFirm(),
            'Qwen': QwenFirm(),
            'Deepseek': DeepseekFirm(),
            'Grok': GrokFirm()
        }
    
    def get_firm(self, firm_name: str) -> Optional[TradingFirm]:
        return self.firms.get(firm_name)
    
    def get_all_firms(self) -> Dict[str, TradingFirm]:
        return self.firms
