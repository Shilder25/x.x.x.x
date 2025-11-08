from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class LearningSystem:
    """
    Sistema de aprendizaje continuo que analiza performance histórica
    y genera insights para que las IAs mejoren sus estrategias.
    """
    
    def __init__(self, database):
        self.database = database
    
    def analyze_weekly_performance(self, firm_name: str) -> Dict:
        """
        Analiza la performance de una IA durante la última semana
        y genera insights accionables.
        
        Returns:
            Dictionary con análisis detallado y recomendaciones
        """
        autonomous_bets = self.database.get_autonomous_bets(firm_name=firm_name, limit=100)
        
        if not autonomous_bets:
            return {
                'firm_name': firm_name,
                'status': 'insufficient_data',
                'message': 'No hay datos suficientes para análisis'
            }
        
        cutoff_time = datetime.now() - timedelta(days=7)
        recent_bets = [
            bet for bet in autonomous_bets
            if bet.get('execution_timestamp') and
            datetime.fromisoformat(bet['execution_timestamp']) > cutoff_time
        ]
        
        if not recent_bets:
            return {
                'firm_name': firm_name,
                'status': 'no_recent_activity',
                'message': 'No hay actividad en los últimos 7 días'
            }
        
        analysis = {
            'firm_name': firm_name,
            'period': '7_days',
            'total_bets': len(recent_bets),
            'patterns': self._identify_patterns(recent_bets),
            'category_performance': self._analyze_by_category(recent_bets),
            'confidence_analysis': self._analyze_confidence_correlation(recent_bets),
            'ev_analysis': self._analyze_expected_value_accuracy(recent_bets),
            'recommendations': [],
            'key_insights': []
        }
        
        analysis['recommendations'] = self._generate_recommendations(analysis)
        analysis['key_insights'] = self._extract_key_insights(analysis)
        
        return analysis
    
    def _identify_patterns(self, bets: List[Dict]) -> Dict:
        """
        Identifica patrones en las apuestas y resultados.
        """
        patterns = {
            'win_streaks': [],
            'loss_streaks': [],
            'time_of_day_performance': {},
            'bet_size_correlation': {}
        }
        
        current_streak = {'type': None, 'count': 0}
        
        for bet in sorted(bets, key=lambda x: x.get('execution_timestamp', '')):
            if bet.get('actual_result') is None:
                continue
            
            won = bet['actual_result'] == 1
            
            if current_streak['type'] == ('win' if won else 'loss'):
                current_streak['count'] += 1
            else:
                if current_streak['count'] > 0:
                    if current_streak['type'] == 'win':
                        patterns['win_streaks'].append(current_streak['count'])
                    else:
                        patterns['loss_streaks'].append(current_streak['count'])
                
                current_streak = {'type': 'win' if won else 'loss', 'count': 1}
        
        patterns['max_win_streak'] = max(patterns['win_streaks']) if patterns['win_streaks'] else 0
        patterns['max_loss_streak'] = max(patterns['loss_streaks']) if patterns['loss_streaks'] else 0
        patterns['avg_win_streak'] = statistics.mean(patterns['win_streaks']) if patterns['win_streaks'] else 0
        patterns['avg_loss_streak'] = statistics.mean(patterns['loss_streaks']) if patterns['loss_streaks'] else 0
        
        return patterns
    
    def _analyze_by_category(self, bets: List[Dict]) -> Dict:
        """
        Analiza performance por categoría de evento.
        """
        category_stats = defaultdict(lambda: {
            'total': 0,
            'wins': 0,
            'losses': 0,
            'profit': 0,
            'avg_probability': []
        })
        
        for bet in bets:
            category = bet.get('category', 'unknown')
            category_stats[category]['total'] += 1
            
            if bet.get('actual_result') is not None:
                if bet['actual_result'] == 1:
                    category_stats[category]['wins'] += 1
                else:
                    category_stats[category]['losses'] += 1
                
                if bet.get('profit_loss'):
                    category_stats[category]['profit'] += bet['profit_loss']
            
            category_stats[category]['avg_probability'].append(bet.get('probability', 0))
        
        results = {}
        for category, stats in category_stats.items():
            total_resolved = stats['wins'] + stats['losses']
            win_rate = (stats['wins'] / total_resolved * 100) if total_resolved > 0 else 0
            avg_prob = statistics.mean(stats['avg_probability']) if stats['avg_probability'] else 0
            
            results[category] = {
                'total_bets': stats['total'],
                'win_rate': round(win_rate, 2),
                'profit': round(stats['profit'], 2),
                'avg_probability': round(avg_prob, 3),
                'roi': round((stats['profit'] / stats['total']) * 100, 2) if stats['total'] > 0 else 0
            }
        
        return results
    
    def _analyze_confidence_correlation(self, bets: List[Dict]) -> Dict:
        """
        Analiza la correlación entre nivel de confianza y éxito real.
        """
        confidence_buckets = {
            'low (50-60%)': {'wins': 0, 'total': 0},
            'medium (60-70%)': {'wins': 0, 'total': 0},
            'high (70-80%)': {'wins': 0, 'total': 0},
            'very_high (80%+)': {'wins': 0, 'total': 0}
        }
        
        for bet in bets:
            if bet.get('actual_result') is None:
                continue
            
            confidence = bet.get('confidence', 50)
            
            if confidence < 60:
                bucket = 'low (50-60%)'
            elif confidence < 70:
                bucket = 'medium (60-70%)'
            elif confidence < 80:
                bucket = 'high (70-80%)'
            else:
                bucket = 'very_high (80%+)'
            
            confidence_buckets[bucket]['total'] += 1
            if bet['actual_result'] == 1:
                confidence_buckets[bucket]['wins'] += 1
        
        results = {}
        for bucket, stats in confidence_buckets.items():
            if stats['total'] > 0:
                win_rate = (stats['wins'] / stats['total']) * 100
                results[bucket] = {
                    'win_rate': round(win_rate, 2),
                    'sample_size': stats['total'],
                    'calibration': 'good' if abs(win_rate - float(bucket.split('(')[1].split('-')[0])) < 15 else 'poor'
                }
        
        return results
    
    def _analyze_expected_value_accuracy(self, bets: List[Dict]) -> Dict:
        """
        Analiza qué tan precisas son las estimaciones de valor esperado.
        """
        ev_positive = {'wins': 0, 'total': 0, 'profit': 0}
        ev_negative = {'wins': 0, 'total': 0, 'profit': 0}
        
        for bet in bets:
            if bet.get('actual_result') is None or bet.get('expected_value') is None:
                continue
            
            ev = bet['expected_value']
            
            if ev > 0:
                ev_positive['total'] += 1
                if bet['actual_result'] == 1:
                    ev_positive['wins'] += 1
                if bet.get('profit_loss'):
                    ev_positive['profit'] += bet['profit_loss']
            else:
                ev_negative['total'] += 1
                if bet['actual_result'] == 1:
                    ev_negative['wins'] += 1
                if bet.get('profit_loss'):
                    ev_negative['profit'] += bet['profit_loss']
        
        return {
            'ev_positive': {
                'win_rate': round((ev_positive['wins'] / ev_positive['total'] * 100), 2) if ev_positive['total'] > 0 else 0,
                'total_bets': ev_positive['total'],
                'total_profit': round(ev_positive['profit'], 2),
                'accuracy': 'good' if ev_positive['total'] > 0 and ev_positive['wins'] / ev_positive['total'] > 0.5 else 'poor'
            },
            'ev_negative': {
                'win_rate': round((ev_negative['wins'] / ev_negative['total'] * 100), 2) if ev_negative['total'] > 0 else 0,
                'total_bets': ev_negative['total'],
                'total_profit': round(ev_negative['profit'], 2)
            }
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """
        Genera recomendaciones específicas basadas en el análisis.
        """
        recommendations = []
        
        category_perf = analysis.get('category_performance', {})
        best_category = max(category_perf.items(), key=lambda x: x[1].get('win_rate', 0)) if category_perf else None
        worst_category = min(category_perf.items(), key=lambda x: x[1].get('win_rate', 0)) if category_perf else None
        
        if best_category and best_category[1]['win_rate'] > 60:
            recommendations.append(
                f"✅ Incrementar apuestas en categoría '{best_category[0]}' (win rate: {best_category[1]['win_rate']:.1f}%)"
            )
        
        if worst_category and worst_category[1]['win_rate'] < 40 and worst_category[1]['total_bets'] > 3:
            recommendations.append(
                f"⚠️ Evitar categoría '{worst_category[0]}' (win rate: {worst_category[1]['win_rate']:.1f}%)"
            )
        
        patterns = analysis.get('patterns', {})
        if patterns.get('max_loss_streak', 0) > 4:
            recommendations.append(
                f"🛑 Reducir tamaño de apuesta después de 3 pérdidas consecutivas (máx racha: {patterns['max_loss_streak']})"
            )
        
        confidence_analysis = analysis.get('confidence_analysis', {})
        for bucket, stats in confidence_analysis.items():
            if stats.get('calibration') == 'poor' and stats.get('sample_size', 0) > 5:
                recommendations.append(
                    f"🎯 Recalibrar confianza en rango {bucket} (actual: {stats['win_rate']:.1f}%)"
                )
        
        ev_analysis = analysis.get('ev_analysis', {})
        ev_positive_stats = ev_analysis.get('ev_positive', {})
        if ev_positive_stats.get('accuracy') == 'poor' and ev_positive_stats.get('total_bets', 0) > 5:
            recommendations.append(
                "📊 Revisar modelo de cálculo de EV - predicciones positivas no se cumplen"
            )
        
        if not recommendations:
            recommendations.append("✨ Performance estable - mantener estrategia actual")
        
        return recommendations
    
    def _extract_key_insights(self, analysis: Dict) -> List[str]:
        """
        Extrae insights clave del análisis.
        """
        insights = []
        
        total_bets = analysis.get('total_bets', 0)
        insights.append(f"Total de apuestas analizadas: {total_bets}")
        
        category_perf = analysis.get('category_performance', {})
        if category_perf:
            profitable_categories = [cat for cat, stats in category_perf.items() if stats.get('profit', 0) > 0]
            if profitable_categories:
                insights.append(f"Categorías rentables: {', '.join(profitable_categories)}")
        
        patterns = analysis.get('patterns', {})
        if patterns.get('max_win_streak', 0) > 3:
            insights.append(f"Mejor racha ganadora: {patterns['max_win_streak']} apuestas")
        
        if patterns.get('max_loss_streak', 0) > 3:
            insights.append(f"⚠️ Racha perdedora máxima: {patterns['max_loss_streak']} apuestas")
        
        return insights
    
    def compare_firms_performance(self) -> Dict:
        """
        Compara performance entre todas las firmas para identificar
        qué estrategias funcionan mejor.
        """
        firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
        comparison = {}
        
        for firm in firms:
            analysis = self.analyze_weekly_performance(firm)
            
            if analysis.get('status') in ['insufficient_data', 'no_recent_activity']:
                continue
            
            comparison[firm] = {
                'total_bets': analysis.get('total_bets', 0),
                'best_category': self._get_best_category(analysis),
                'top_recommendations': analysis.get('recommendations', [])[:3],
                'key_insights': analysis.get('key_insights', [])
            }
        
        return comparison
    
    def _get_best_category(self, analysis: Dict) -> Optional[str]:
        """
        Obtiene la categoría con mejor performance.
        """
        category_perf = analysis.get('category_performance', {})
        
        if not category_perf:
            return None
        
        best = max(category_perf.items(), key=lambda x: x[1].get('win_rate', 0))
        return f"{best[0]} ({best[1]['win_rate']:.1f}% win rate)"
    
    def generate_cross_learning_insights(self) -> List[str]:
        """
        Genera insights que todas las IAs pueden aprender entre sí.
        """
        comparison = self.compare_firms_performance()
        
        if not comparison:
            return ["Datos insuficientes para análisis comparativo"]
        
        insights = []
        
        best_categories = {}
        for firm, data in comparison.items():
            if data.get('best_category'):
                category = data['best_category'].split(' (')[0]
                if category not in best_categories:
                    best_categories[category] = []
                best_categories[category].append(firm)
        
        for category, firms in best_categories.items():
            if len(firms) >= 2:
                insights.append(
                    f"📈 Categoría '{category}' funciona bien para {', '.join(firms)}"
                )
        
        all_recommendations = []
        for firm, data in comparison.items():
            all_recommendations.extend(data.get('top_recommendations', []))
        
        recommendation_counts = {}
        for rec in all_recommendations:
            rec_key = rec.split(':')[0] if ':' in rec else rec[:30]
            recommendation_counts[rec_key] = recommendation_counts.get(rec_key, 0) + 1
        
        common_recommendations = [rec for rec, count in recommendation_counts.items() if count >= 2]
        
        for rec in common_recommendations[:3]:
            insights.append(f"💡 Recomendación común: {rec}")
        
        return insights if insights else ["Sistema en fase de aprendizaje inicial"]
