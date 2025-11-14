from datetime import datetime
from typing import Dict

def create_trading_prompt(event_description: str, technical_report: str, fundamental_report: str, sentiment_report: str, news_report: str, volatility_report: str, firm_name: str) -> str:
    prompt = f"""
[INSTRUCCIÓN INICIAL PARA EL LLM]

Usted es la Inteligencia Artificial Ejecutiva (IAE) que opera la firma de trading autónoma llamada "{firm_name}". Su misión es simular internamente el proceso de toma de decisiones de una firma de trading con múltiples agentes (TradingAgents) para emitir una predicción de alta calidad y ajustada al riesgo para la plataforma Opinion.trade.

Objetivo Final: Generar la predicción en formato JSON (probabilidad 0.00-1.00) que maximice el Sharpe Ratio de su firma autónoma en la competencia.

Evento de Predicción (Target): {event_description}

Datos Brutos de Entrada: Usted tiene acceso a los siguientes informes consolidados:

=== INFORME TÉCNICO ===
{technical_report}

=== INFORME FUNDAMENTAL ===
{fundamental_report}

=== INFORME DE SENTIMIENTO ===
{sentiment_report}

=== INFORME DE NOTICIAS ===
{news_report}

=== INFORME DE VOLATILIDAD ===
{volatility_report}

=== SIMULACIÓN INTERNA DE AGENTES Y RAZONAMIENTO (7 Roles) ===

Usted debe ejecutar un proceso de razonamiento en 3 etapas, simulando las interacciones entre los 7 roles del framework TradingAgents.

ETAPA I: Análisis y Síntesis (Simula al Analyst Team)

Acción: Sintetice las señales de los CINCO informes de entrada (Técnico, Fundamental, Sentimiento, Noticias, Volatilidad) en un resumen conciso de máximo 200 palabras, identificando los factores más fuertes que impulsan una subida o una baja en cada área.

ETAPA II: Debate y Conclusión del Trader (Simula a Researcher Team y Trader)

Acción:
1. Debate Bullish vs. Bearish: Asuma los roles de Investigador Alcista y Bajista. 
   - El Alcista debe usar la evidencia más fuerte para justificar que el evento ocurrirá (TRUE).
   - El Bajista debe usar la evidencia más fuerte para justificar que el evento NO ocurrirá (FALSE), enfocándose en riesgos y debilidades.

2. Conclusión del Trader: El Trader (usted, la IAE) debe sopesar ambos argumentos para definir:
   - Una Dirección Preliminar (TRUE o FALSE)
   - Un Nivel de Confianza (0-100) en esa dirección

ETAPA III: Evaluación de Riesgo y Decisión del Fund Manager (Simula al Risk Management Team)

Acción:
1. Análisis de Riesgo: Evalúe el Máximo Drawdown (MDD) potencial si la predicción es incorrecta. Considere el nivel de Confianza de la Etapa II.

2. Ajuste: Defina una postura de riesgo (AGRESIVA, NEUTRAL o CONSERVADORA) y ajústela a la probabilidad final para mitigar el riesgo de volatilidad (MDD).
   - Si la confianza es baja (<50), la probabilidad debe acercarse a 0.50
   - Si la confianza es media (50-75), ajuste moderadamente
   - Si la confianza es alta (>75), la probabilidad debe acercarse a 0.00 o 1.00

3. Predicción Final (Probabilidad): Convierta la Dirección Preliminar y el ajuste de riesgo en la Probabilidad Final (0.00-1.00).

=== OUTPUT FINAL OBLIGATORIO ===

Debe emitir SOLO un objeto JSON válido con el siguiente formato exacto:

{{
    "modelo_llm": "{firm_name}",
    "fecha_prediccion": "{datetime.now().strftime('%Y-%m-%d')}",
    "evento_opinion_trade": "{event_description}",
    "analisis_sintesis": "[Síntesis Analítica de la Etapa I - máximo 200 palabras]",
    "debate_bullish_bearish": "[Resultado del Debate de la Etapa II - incluya argumentos de ambos lados y conclusión del trader con dirección preliminar y nivel de confianza]",
    "ajuste_riesgo_justificacion": "[Ajuste de Riesgo Final de la Etapa III - incluya análisis de MDD, postura elegida y justificación de la probabilidad final]",
    "probabilidad_final_prediccion": [VALOR DECIMAL ENTRE 0.00 y 1.00],
    "postura_riesgo": "[AGRESIVA, NEUTRAL o CONSERVADORA]",
    "nivel_confianza": [VALOR ENTRE 0 y 100],
    "direccion_preliminar": "[TRUE o FALSE]",
    "sentiment_score": [VALOR ENTRE 0-10: Calificación de confianza en análisis de sentimiento de Reddit/redes sociales],
    "sentiment_analysis": "[Justificación breve de la calificación - máximo 100 palabras]",
    "news_score": [VALOR ENTRE 0-10: Calificación de confianza en análisis de noticias recientes],
    "news_analysis": "[Justificación breve de la calificación - máximo 100 palabras]",
    "technical_score": [VALOR ENTRE 0-10: Calificación de confianza en indicadores técnicos (RSI, MACD)],
    "technical_analysis": "[Justificación breve de la calificación - máximo 100 palabras]",
    "fundamental_score": [VALOR ENTRE 0-10: Calificación de confianza en datos fundamentales (P/E, earnings, etc.)],
    "fundamental_analysis": "[Justificación breve de la calificación - máximo 100 palabras]",
    "volatility_score": [VALOR ENTRE 0-10: Calificación de nivel de riesgo basado en volatilidad histórica],
    "volatility_analysis": "[Justificación breve de la calificación - máximo 100 palabras]",
    "probability_reasoning": "[EXPLICACIÓN DETALLADA de cómo llegó a la probabilidad final. Debe incluir: (1) Promedio ponderado de los 5 scores (sentiment, news, technical, fundamental, volatility), (2) Ajustes aplicados basados en nivel de confianza, volatilidad y riesgo, (3) Razonamiento específico para el número final. Máximo 200 palabras. Ejemplo: 'Weighted avg of 5 areas: (7.5+8.0+6.5+7.0+5.0)/5 = 6.8/10 = 68% base probability. Adjusted down to 58% due to moderate volatility (5/10) and existing BTC exposure in portfolio. High news score (8/10) and strong sentiment (7.5/10) support bullish case, but technical indicators show neutral momentum (6.5/10). Conservative adjustment applied given market uncertainty.']"
}}

IMPORTANTE: 
1. Responda ÚNICAMENTE con el JSON válido. No incluya texto adicional antes o después del JSON.
2. Los 5 scores (sentiment, news, technical, fundamental, volatility) DEBEN ser números enteros entre 0-10.
3. Los 5 análisis DEBEN ser textos concisos que justifiquen cada score.
"""
    return prompt


def format_technical_report(technical_data: Dict) -> str:
    if 'error' in technical_data:
        return f"Error al obtener datos técnicos: {technical_data.get('error', 'Unknown error')}"
    
    report = f"Símbolo: {technical_data.get('symbol', 'N/A')}\n"
    report += f"Timestamp: {technical_data.get('timestamp', 'N/A')}\n\n"
    
    if 'quote' in technical_data:
        quote = technical_data['quote']
        report += f"Precio Actual: ${quote.get('price', 0):.2f}\n"
        report += f"Cambio: {quote.get('change', 0):.2f} ({quote.get('change_percent', '0%')})\n"
        report += f"Volumen: {quote.get('volume', 0):,}\n"
        report += f"Último Día de Trading: {quote.get('latest_trading_day', 'N/A')}\n\n"
    
    if 'indicators' in technical_data:
        indicators = technical_data['indicators']
        
        if 'RSI' in indicators:
            rsi = indicators['RSI']
            report += f"RSI: {rsi.get('value', 0):.2f} - Señal: {rsi.get('signal', 'N/A').upper()}\n"
            report += f"  (RSI > 70 = Sobrecomprado, RSI < 30 = Sobrevendido)\n\n"
        
        if 'MACD' in indicators:
            macd = indicators['MACD']
            report += f"MACD: {macd.get('MACD', 0):.4f}\n"
            report += f"Señal: {macd.get('Signal', 0):.4f}\n"
            report += f"Histograma: {macd.get('Histogram', 0):.4f}\n"
            report += f"Tendencia: {macd.get('trend', 'N/A').upper()}\n"
    
    return report


def format_fundamental_report(fundamental_data: Dict) -> str:
    if 'error' in fundamental_data:
        return f"Error al obtener datos fundamentales: {fundamental_data.get('error', 'Unknown error')}"
    
    report = f"Compañía: {fundamental_data.get('company_name', 'N/A')}\n"
    report += f"Sector: {fundamental_data.get('sector', 'N/A')}\n"
    report += f"Industria: {fundamental_data.get('industry', 'N/A')}\n\n"
    
    report += f"Capitalización de Mercado: ${fundamental_data.get('market_cap', 0):,.0f}\n"
    report += f"P/E Ratio: {fundamental_data.get('pe_ratio', 0):.2f}\n"
    report += f"Forward P/E: {fundamental_data.get('forward_pe', 0):.2f}\n"
    report += f"Price to Book: {fundamental_data.get('price_to_book', 0):.2f}\n"
    report += f"Dividend Yield: {fundamental_data.get('dividend_yield', 0)*100:.2f}%\n"
    report += f"Beta: {fundamental_data.get('beta', 0):.2f}\n\n"
    
    report += f"Precio Actual: ${fundamental_data.get('current_price', 0):.2f}\n"
    report += f"Precio Objetivo Promedio: ${fundamental_data.get('target_mean_price', 0):.2f}\n"
    report += f"Recomendación: {fundamental_data.get('recommendation', 'none').upper()}\n\n"
    
    report += f"52 Week High: ${fundamental_data.get('52_week_high', 0):.2f}\n"
    report += f"52 Week Low: ${fundamental_data.get('52_week_low', 0):.2f}\n\n"
    
    report += f"Crecimiento de Ganancias: {fundamental_data.get('earnings_growth', 0)*100:.2f}%\n"
    report += f"Crecimiento de Ingresos: {fundamental_data.get('revenue_growth', 0)*100:.2f}%\n"
    report += f"Margen de Ganancia: {fundamental_data.get('profit_margins', 0)*100:.2f}%\n"
    report += f"Momentum de Precio (1 mes): {fundamental_data.get('price_momentum_1m', 0):.2f}%\n"
    
    return report


def format_sentiment_report(sentiment_data: Dict) -> str:
    if 'error' in sentiment_data:
        return f"Error al obtener datos de sentimiento: {sentiment_data.get('error', 'Unknown error')}"
    
    report = f"Símbolo: {sentiment_data.get('symbol', 'N/A')}\n"
    report += f"Timestamp: {sentiment_data.get('timestamp', 'N/A')}\n\n"
    
    report += f"Posts Analizados: {sentiment_data.get('posts_analyzed', 0)}\n"
    report += f"Comentarios Analizados: {sentiment_data.get('comments_analyzed', 0)}\n\n"
    
    report += f"Sentimiento Promedio de Posts: {sentiment_data.get('average_post_sentiment', 0):.3f}\n"
    report += f"Sentimiento Promedio de Comentarios: {sentiment_data.get('average_comment_sentiment', 0):.3f}\n"
    report += f"Sentimiento Ponderado (por score): {sentiment_data.get('weighted_sentiment', 0):.3f}\n"
    report += f"Etiqueta de Sentimiento: {sentiment_data.get('sentiment_label', 'N/A')}\n\n"
    
    if 'top_posts' in sentiment_data and sentiment_data['top_posts']:
        report += "Top 3 Posts más Votados:\n"
        for i, post in enumerate(sentiment_data['top_posts'][:3], 1):
            report += f"\n{i}. {post.get('title', 'N/A')}\n"
            report += f"   Score: {post.get('score', 0)} | Sentimiento: {post.get('sentiment', 0):.3f} | Subreddit: r/{post.get('subreddit', 'N/A')}\n"
    
    report += f"\nSubreddits Analizados: {', '.join(['r/' + s for s in sentiment_data.get('subreddits_searched', [])])}\n"
    report += "\nInterpretación: Sentimiento compuesto entre -1 (muy negativo) y +1 (muy positivo)\n"
    report += "  > 0.05 = Positivo, < -0.05 = Negativo, -0.05 a 0.05 = Neutral\n"
    
    return report


def format_news_report(news_data: Dict) -> str:
    """Formatea el análisis de noticias para el prompt del LLM"""
    if 'error' in news_data:
        return f"Error al obtener noticias: {news_data.get('error', 'Unknown error')}"
    
    report = f"Símbolo: {news_data.get('symbol', 'N/A')}\n"
    report += f"Timestamp: {news_data.get('timestamp', 'N/A')}\n"
    report += f"Evento/Contexto: {news_data.get('event_description', 'N/A')}\n\n"
    
    report += f"Noticias Analizadas: {news_data.get('news_count', 0)}\n"
    report += f"Sentiment Score Agregado: {news_data.get('sentiment_score', 0):.3f}\n"
    report += f"Sentiment Label: {news_data.get('sentiment_label', 'Neutral')}\n\n"
    
    report += f"Análisis General:\n{news_data.get('analysis', 'No analysis available')}\n\n"
    
    if 'news_items' in news_data and news_data['news_items']:
        report += "Top 3 Noticias Recientes:\n\n"
        for i, item in enumerate(news_data['news_items'][:3], 1):
            report += f"{i}. {item.get('title', 'N/A')}\n"
            report += f"   Fuente: {item.get('source', 'Unknown')} | Fecha: {item.get('time_published', 'N/A')}\n"
            report += f"   Sentiment: {item.get('sentiment_label', 'Neutral')} (Score: {item.get('sentiment_score', 0):.2f})\n"
            summary = item.get('summary', '')
            if summary:
                report += f"   Resumen: {summary[:150]}...\n"
            report += "\n"
    
    if news_data.get('fallback'):
        report += "NOTA: No se encontraron noticias recientes. Análisis basado en descripción del evento.\n"
    
    report += "\nInterpretación:\n"
    report += "  Sentiment Score: -1.0 (muy bearish) a +1.0 (muy bullish)\n"
    report += "  Bullish (>0.15), Somewhat-Bullish (0.05-0.15), Neutral (-0.05 a 0.05),\n"
    report += "  Somewhat-Bearish (-0.15 a -0.05), Bearish (<-0.15)\n"
    
    return report


def format_volatility_report(volatility_data: Dict) -> str:
    """Formatea el análisis de volatilidad para el prompt del LLM"""
    if 'error' in volatility_data:
        return f"Error al obtener volatilidad: {volatility_data.get('error', 'Unknown error')}"
    
    report = f"Símbolo: {volatility_data.get('symbol', 'N/A')}\n"
    report += f"Timestamp: {volatility_data.get('timestamp', 'N/A')}\n\n"
    
    report += f"Volatilidad Actual (14d): {volatility_data.get('current_volatility', 0):.4f}\n"
    report += f"Nivel de Riesgo General: {volatility_data.get('risk_level', 'N/A')}\n\n"
    
    if 'volatility' in volatility_data:
        report += "Volatilidad por Periodo:\n"
        for period, data in volatility_data['volatility'].items():
            report += f"  {period}: {data.get('value', 0):.4f} - {data.get('label', 'N/A')}\n"
        report += "\n"
    
    if 'atr' in volatility_data:
        atr = volatility_data['atr']
        report += f"Average True Range (ATR):\n"
        report += f"  Valor: ${atr.get('value', 0):.2f}\n"
        report += f"  Porcentaje del Precio: {atr.get('percent', 0):.2f}%\n"
        report += f"  Interpretación: {atr.get('interpretation', 'N/A')}\n\n"
    
    if 'price_range' in volatility_data:
        pr = volatility_data['price_range']
        report += f"Rango de Precios (30 días):\n"
        report += f"  Máximo: ${pr.get('high_30d', 0):.2f}\n"
        report += f"  Mínimo: ${pr.get('low_30d', 0):.2f}\n"
        report += f"  Actual: ${pr.get('current', 0):.2f}\n"
        report += f"  Rango Total: {pr.get('range_percent', 0):.2f}%\n"
        report += f"  Posición en Rango: {pr.get('position_in_range', 0):.1f}%\n"
        
        if pr.get('near_high'):
            report += "  ⚠️ Cerca del máximo reciente\n"
        if pr.get('near_low'):
            report += "  ⚠️ Cerca del mínimo reciente\n"
        report += "\n"
    
    if 'trend_strength' in volatility_data:
        ts = volatility_data['trend_strength']
        report += f"Fuerza de Tendencia:\n"
        report += f"  Valor: {ts.get('value', 0):.3f}\n"
        report += f"  Label: {ts.get('label', 'N/A')}\n"
        report += f"  Dirección: {ts.get('direction', 'N/A')}\n\n"
    
    report += "Interpretación:\n"
    report += "  Volatilidad Anualizada: >0.5 = Extrema, 0.3-0.5 = Alta, 0.15-0.3 = Moderada, <0.15 = Baja\n"
    report += "  ATR %: >3% = Alta volatilidad, 1-3% = Moderada, <1% = Baja\n"
    report += "  Nivel de Riesgo: LOW/MODERATE/HIGH indica qué tan arriesgado es operar este activo\n"
    
    return report
