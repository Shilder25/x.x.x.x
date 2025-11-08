from typing import Dict, List, Optional
import pandas as pd
from database import TradingDatabase

class RecommendationEngine:
    def __init__(self, db: TradingDatabase):
        self.db = db
    
    def get_best_firm_recommendation(self, event_type: Optional[str] = None) -> Dict:
        """
        Recommend the best firm to use based on historical performance.
        
        Args:
            event_type: Optional event type classifier (future enhancement)
        
        Returns:
            Dictionary with recommendation and reasoning
        """
        performances = self.db.get_all_firm_performances()
        
        if not performances or all(p['total_predictions'] == 0 for p in performances):
            return {
                'recommended_firm': 'ChatGPT',
                'reason': 'No historical data available. ChatGPT recommended as default.',
                'confidence': 'Low',
                'alternatives': ['Gemini', 'Qwen']
            }
        
        firms_with_data = [p for p in performances if p['total_predictions'] > 0]
        
        if not firms_with_data:
            return {
                'recommended_firm': 'ChatGPT',
                'reason': 'No resolved predictions yet. ChatGPT recommended as default.',
                'confidence': 'Low',
                'alternatives': ['Gemini', 'Qwen']
            }
        
        df = pd.DataFrame(firms_with_data)
        
        df['cost_per_prediction'] = df.apply(
            lambda row: row['total_cost'] / row['total_predictions'] if row['total_predictions'] > 0 else 0,
            axis=1
        )
        
        df['roi'] = df.apply(
            lambda row: (row['total_profit'] / (row['total_cost'] * 100)) * 100 if row['total_cost'] > 0 else 0,
            axis=1
        )
        
        resolved_df = df[df['correct_predictions'] > 0].copy()
        
        if len(resolved_df) == 0:
            best_firm = df.sort_values('total_predictions', ascending=False).iloc[0]
            return {
                'recommended_firm': best_firm['firm_name'],
                'reason': f"Most active firm with {best_firm['total_predictions']} predictions, but no resolved results yet.",
                'confidence': 'Low',
                'alternatives': list(df.sort_values('total_predictions', ascending=False)['firm_name'].iloc[1:3])
            }
        
        resolved_df['score'] = (
            resolved_df['accuracy'] * 0.4 +
            resolved_df['sharpe_ratio'].clip(lower=-5, upper=5) * 10 * 0.3 +
            (resolved_df['total_profit'] / resolved_df['total_profit'].max() * 100 if resolved_df['total_profit'].max() > 0 else 0) * 0.3
        )
        
        best_firm = resolved_df.sort_values('score', ascending=False).iloc[0]
        
        reasons = []
        if best_firm['accuracy'] > 60:
            reasons.append(f"Alta precisión ({best_firm['accuracy']:.1f}%)")
        if best_firm['sharpe_ratio'] > 0:
            reasons.append(f"Sharpe Ratio positivo ({best_firm['sharpe_ratio']:.2f})")
        if best_firm['total_profit'] > 0:
            reasons.append(f"Ganancia neta de ${best_firm['total_profit']:.2f}")
        
        reason_text = " | ".join(reasons) if reasons else "Mejor puntuación general"
        
        confidence = 'High' if best_firm['total_predictions'] >= 10 else 'Medium' if best_firm['total_predictions'] >= 5 else 'Low'
        
        alternatives = list(resolved_df.sort_values('score', ascending=False)['firm_name'].iloc[1:3])
        
        return {
            'recommended_firm': best_firm['firm_name'],
            'reason': reason_text,
            'confidence': confidence,
            'accuracy': best_firm['accuracy'],
            'sharpe_ratio': best_firm['sharpe_ratio'],
            'total_profit': best_firm['total_profit'],
            'predictions_count': best_firm['total_predictions'],
            'alternatives': alternatives
        }
    
    def calculate_consensus_prediction(self, predictions: Dict) -> Dict:
        """
        Calculate a weighted consensus prediction based on firm performance.
        
        Args:
            predictions: Dictionary of {firm_name: prediction_data}
        
        Returns:
            Consensus prediction with weighted probability
        """
        if not predictions:
            return {
                'consensus_probability': 0.5,
                'confidence': 0,
                'participating_firms': [],
                'weights': {}
            }
        
        performances = self.db.get_all_firm_performances()
        perf_dict = {p['firm_name']: p for p in performances}
        
        valid_predictions = {
            firm: pred for firm, pred in predictions.items()
            if 'error' not in pred and 'probabilidad_final_prediccion' in pred
        }
        
        if not valid_predictions:
            return {
                'consensus_probability': 0.5,
                'confidence': 0,
                'participating_firms': [],
                'weights': {}
            }
        
        weights = {}
        for firm in valid_predictions.keys():
            perf = perf_dict.get(firm, {})
            
            if perf.get('total_predictions', 0) == 0:
                weights[firm] = 1.0
            else:
                accuracy_weight = perf.get('accuracy', 50) / 100
                sharpe_weight = max(0, min(1, (perf.get('sharpe_ratio', 0) + 2) / 4))
                
                weights[firm] = (accuracy_weight * 0.6 + sharpe_weight * 0.4)
        
        total_weight = sum(weights.values())
        if total_weight == 0:
            weights = {firm: 1.0 for firm in valid_predictions.keys()}
            total_weight = len(weights)
        
        normalized_weights = {firm: w / total_weight for firm, w in weights.items()}
        
        consensus_prob = sum(
            valid_predictions[firm].get('probabilidad_final_prediccion', 0.5) * normalized_weights[firm]
            for firm in valid_predictions.keys()
        )
        
        probabilities = [pred.get('probabilidad_final_prediccion', 0.5) for pred in valid_predictions.values()]
        std_dev = pd.Series(probabilities).std() if len(probabilities) > 1 else 0
        
        confidence = max(0, min(100, 100 - (std_dev * 200)))
        
        return {
            'consensus_probability': consensus_prob,
            'confidence': confidence,
            'participating_firms': list(valid_predictions.keys()),
            'weights': normalized_weights,
            'individual_probabilities': {
                firm: pred.get('probabilidad_final_prediccion', 0.5)
                for firm, pred in valid_predictions.items()
            },
            'standard_deviation': std_dev
        }
    
    def get_firm_attribution_report(self) -> List[Dict]:
        """
        Generate detailed attribution report showing which firms were responsible for wins/losses.
        
        Returns:
            List of attribution records for each resolved prediction
        """
        all_predictions = self.db.get_recent_predictions(limit=1000)
        
        resolved = [p for p in all_predictions if p['actual_result'] is not None]
        
        if not resolved:
            return []
        
        attribution_data = []
        
        for pred in resolved:
            was_correct = (
                (pred['probability'] >= 0.5 and pred['actual_result'] == 1) or
                (pred['probability'] < 0.5 and pred['actual_result'] == 0)
            )
            
            attribution_data.append({
                'prediction_id': pred['id'],
                'firm_name': pred['firm_name'],
                'event_description': pred['event_description'],
                'predicted_probability': pred['probability'],
                'actual_result': 'TRUE' if pred['actual_result'] == 1 else 'FALSE',
                'correct': was_correct,
                'profit_loss': pred['profit_loss'] or 0,
                'prediction_date': pred['prediction_date'],
                'impact': 'Win' if was_correct else 'Loss'
            })
        
        return attribution_data
    
    def analyze_reasoning_patterns(self, firm_name: Optional[str] = None) -> Dict:
        """
        Analyze which reasoning patterns correlate with successful predictions.
        
        Args:
            firm_name: Optional filter for specific firm
        
        Returns:
            Analysis of reasoning patterns and their success rates
        """
        all_predictions = self.db.get_recent_predictions(firm_name=firm_name, limit=1000)
        
        resolved = [p for p in all_predictions if p['actual_result'] is not None]
        
        if not resolved:
            return {
                'total_analyzed': 0,
                'patterns': [],
                'message': 'No resolved predictions to analyze'
            }
        
        risk_posture_analysis = {}
        
        for pred in resolved:
            posture = pred.get('postura_riesgo', 'UNKNOWN')
            
            if posture not in risk_posture_analysis:
                risk_posture_analysis[posture] = {
                    'count': 0,
                    'correct': 0,
                    'total_profit': 0
                }
            
            risk_posture_analysis[posture]['count'] += 1
            
            was_correct = (
                (pred['probability'] >= 0.5 and pred['actual_result'] == 1) or
                (pred['probability'] < 0.5 and pred['actual_result'] == 0)
            )
            
            if was_correct:
                risk_posture_analysis[posture]['correct'] += 1
            
            risk_posture_analysis[posture]['total_profit'] += pred.get('profit_loss', 0)
        
        patterns = []
        for posture, data in risk_posture_analysis.items():
            accuracy = (data['correct'] / data['count'] * 100) if data['count'] > 0 else 0
            patterns.append({
                'pattern_type': 'risk_posture',
                'pattern_value': posture,
                'occurrences': data['count'],
                'accuracy': accuracy,
                'total_profit': data['total_profit'],
                'avg_profit': data['total_profit'] / data['count'] if data['count'] > 0 else 0
            })
        
        patterns.sort(key=lambda x: x['accuracy'], reverse=True)
        
        return {
            'total_analyzed': len(resolved),
            'firm_name': firm_name or 'All Firms',
            'patterns': patterns
        }
