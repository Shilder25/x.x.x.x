from typing import Dict, List, Optional
from datetime import datetime
import json

from opinion_trade_api import OpinionTradeAPI
from risk_management import RiskManager, RiskLevel
from bankroll_manager import BankrollManager, BettingStrategy, assign_strategy_to_firm
from llm_clients import FirmOrchestrator
from data_collectors import AlphaVantageCollector, YFinanceCollector, RedditSentimentCollector
from prompt_system import create_trading_prompt, format_technical_report, format_fundamental_report, format_sentiment_report
import os

class AutonomousEngine:
    """
    Motor de decisión autónoma que analiza múltiples eventos de Opinion.trade
    y ejecuta apuestas automáticas para cada IA respetando límites de riesgo.
    """
    
    def __init__(self, initial_bankroll_per_firm: float = 1000.0, simulation_mode: bool = True):
        """
        Args:
            initial_bankroll_per_firm: Presupuesto inicial por cada IA
            simulation_mode: Si True, no ejecuta apuestas reales (solo tracking virtual)
        """
        self.simulation_mode = simulation_mode
        self.initial_bankroll = initial_bankroll_per_firm
        
        self.opinion_api = OpinionTradeAPI()
        self.orchestrator = FirmOrchestrator()
        
        self.alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
        self.reddit_client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        
        self.risk_managers = {}
        self.bankroll_managers = {}
        
        self._initialize_firms()
        
        self.execution_log = []
        self.daily_analysis_count = 0
    
    def _initialize_firms(self):
        """
        Inicializa gestores de riesgo y bankroll para cada IA.
        """
        firms = self.orchestrator.get_all_firms()
        
        for firm_name in firms.keys():
            self.risk_managers[firm_name] = RiskManager(
                firm_name=firm_name,
                initial_bankroll=self.initial_bankroll
            )
            
            strategy = assign_strategy_to_firm(firm_name)
            self.bankroll_managers[firm_name] = BankrollManager(
                firm_name=firm_name,
                strategy=strategy,
                initial_bankroll=self.initial_bankroll
            )
    
    def run_daily_cycle(self) -> Dict:
        """
        Ejecuta el ciclo diario completo:
        1. Obtener eventos disponibles de Opinion.trade
        2. Para cada IA, analizar eventos y decidir apuestas
        3. Ejecutar apuestas respetando límites de riesgo
        4. Registrar todo en base de datos
        
        Returns:
            Resumen de la ejecución diaria
        """
        cycle_start = datetime.now()
        
        results = {
            'timestamp': cycle_start.isoformat(),
            'simulation_mode': self.simulation_mode,
            'firms_results': {},
            'total_bets_placed': 0,
            'total_bets_skipped': 0,
            'errors': []
        }
        
        events_response = self.opinion_api.get_available_events(limit=50)
        
        if not events_response.get('success'):
            results['errors'].append(f"Failed to fetch events: {events_response.get('error')}")
            return results
        
        available_events = events_response.get('events', [])
        
        if not available_events:
            results['errors'].append("No events available")
            return results
        
        results['total_events_analyzed'] = len(available_events)
        
        for firm_name in self.orchestrator.get_all_firms().keys():
            firm_result = self._process_firm_cycle(firm_name, available_events)
            results['firms_results'][firm_name] = firm_result
            results['total_bets_placed'] += firm_result.get('bets_placed', 0)
            results['total_bets_skipped'] += firm_result.get('bets_skipped', 0)
        
        self.execution_log.append(results)
        self.daily_analysis_count += 1
        
        return results
    
    def _process_firm_cycle(self, firm_name: str, events: List[Dict]) -> Dict:
        """
        Procesa el ciclo completo para una IA específica.
        """
        risk_manager = self.risk_managers[firm_name]
        bankroll_manager = self.bankroll_managers[firm_name]
        
        firm_result = {
            'firm_name': firm_name,
            'events_analyzed': 0,
            'bets_placed': 0,
            'bets_skipped': 0,
            'total_bet_amount': 0,
            'risk_level': risk_manager.get_risk_level().value,
            'adaptation_level': risk_manager.adaptation_level.value,
            'decisions': []
        }
        
        risk_status = risk_manager.get_status_report()
        if risk_status.get('in_cooldown'):
            firm_result['skipped_reason'] = f"In cooldown until {risk_status.get('cooldown_until')}"
            return firm_result
        
        active_positions_response = self.opinion_api.get_active_positions()
        active_positions = active_positions_response.get('positions', []) if active_positions_response.get('success') else []
        
        for event in events[:10]:
            decision = self._analyze_event_for_firm(
                firm_name=firm_name,
                event=event,
                risk_manager=risk_manager,
                bankroll_manager=bankroll_manager,
                active_positions=active_positions
            )
            
            firm_result['events_analyzed'] += 1
            firm_result['decisions'].append(decision)
            
            if decision.get('action') == 'BET':
                firm_result['bets_placed'] += 1
                firm_result['total_bet_amount'] += decision.get('bet_size', 0)
            else:
                firm_result['bets_skipped'] += 1
            
            if firm_result['bets_placed'] >= risk_manager.max_concurrent_bets:
                break
        
        return firm_result
    
    def _analyze_event_for_firm(self, firm_name: str, event: Dict,
                                risk_manager: RiskManager, 
                                bankroll_manager: BankrollManager,
                                active_positions: List[Dict]) -> Dict:
        """
        Analiza un evento específico y decide si apostar.
        """
        event_id = event.get('id', 'unknown')
        event_description = event.get('description', event.get('title', 'Unknown event'))
        category = event.get('category', 'general')
        
        decision = {
            'event_id': event_id,
            'event_description': event_description,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'action': 'SKIP',
            'reason': '',
            'bet_size': 0,
            'probability': 0
        }
        
        symbol = self._extract_symbol_from_event(event)
        
        try:
            prediction = self._get_firm_prediction(firm_name, event_description, symbol)
            
            if 'error' in prediction:
                decision['reason'] = f"Prediction error: {prediction.get('error')}"
                return decision
            
            probability = prediction.get('probabilidad_final_prediccion', 0.5)
            confidence = prediction.get('nivel_confianza', 50)
            
            expected_value = self._calculate_expected_value(probability)
            
            decision['probability'] = probability
            decision['confidence'] = confidence
            decision['expected_value'] = expected_value
            
            should_bet, bet_reason = bankroll_manager.should_bet(probability, confidence, expected_value)
            
            if not should_bet:
                decision['reason'] = bet_reason
                return decision
            
            bet_calculation = bankroll_manager.calculate_bet_size(probability, confidence, expected_value)
            
            if bet_calculation.get('bet_size', 0) == 0:
                decision['reason'] = bet_calculation.get('reason', 'Bet size calculation returned 0')
                return decision
            
            bet_size = bet_calculation['bet_size']
            
            risk_check = risk_manager.can_place_bet(
                bet_amount=bet_size,
                category=category,
                current_positions=active_positions
            )
            
            if not risk_check.get('allowed'):
                decision['reason'] = risk_check.get('reason', 'Risk check failed')
                decision['risk_check'] = risk_check
                return decision
            
            decision['action'] = 'BET'
            decision['bet_size'] = bet_size
            decision['bet_calculation'] = bet_calculation
            decision['risk_check'] = risk_check
            decision['reason'] = f"Approved: EV={expected_value:.2f}, Prob={probability:.2%}, Conf={confidence}%"
            
            if not self.simulation_mode:
                execution_result = self._execute_bet(
                    firm_name=firm_name,
                    event_id=event_id,
                    event_description=event_description,
                    bet_size=bet_size,
                    probability=probability,
                    prediction=prediction
                )
                decision['execution'] = execution_result
            else:
                decision['execution'] = {'status': 'simulated', 'message': 'Simulation mode active'}
            
            bankroll_manager.record_bet(bet_size, probability, event_id, event_description)
            
        except Exception as e:
            decision['reason'] = f"Exception during analysis: {str(e)}"
            decision['error'] = str(e)
        
        return decision
    
    def _get_firm_prediction(self, firm_name: str, event_description: str, symbol: str) -> Dict:
        """
        Obtiene predicción de una IA para un evento específico.
        """
        technical_report = "Not available"
        fundamental_report = "Not available"
        sentiment_report = "Not available"
        
        if symbol and self.alpha_vantage_key:
            try:
                collector = AlphaVantageCollector(self.alpha_vantage_key)
                tech_data = collector.get_technical_indicators(symbol)
                if 'error' not in tech_data:
                    technical_report = format_technical_report(tech_data)
            except:
                pass
        
        try:
            firm = self.orchestrator.get_all_firms()[firm_name]
            
            prompt = create_trading_prompt(
                event_description=event_description,
                technical_report=technical_report,
                fundamental_report=fundamental_report,
                sentiment_report=sentiment_report,
                firm_name=firm_name
            )
            
            prediction = firm.generate_prediction(prompt)
            return prediction
            
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_symbol_from_event(self, event: Dict) -> Optional[str]:
        """
        Intenta extraer un símbolo de ticker del evento.
        """
        description = event.get('description', '') + ' ' + event.get('title', '')
        
        common_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BTC', 'ETH']
        
        description_upper = description.upper()
        for symbol in common_symbols:
            if symbol in description_upper:
                return symbol
        
        return None
    
    def _calculate_expected_value(self, probability: float, odds: float = 2.0) -> float:
        """
        Calcula el valor esperado de una apuesta.
        EV = (probability * win_amount) - ((1 - probability) * loss_amount)
        """
        win_amount = odds - 1
        loss_amount = 1
        
        ev = (probability * win_amount) - ((1 - probability) * loss_amount)
        return ev
    
    def _execute_bet(self, firm_name: str, event_id: str, event_description: str,
                    bet_size: float, probability: float, prediction: Dict) -> Dict:
        """
        Ejecuta una apuesta real en Opinion.trade.
        """
        prediction_data = {
            'event_id': event_id,
            'probability': probability,
            'amount': bet_size,
            'firm_name': firm_name,
            'reasoning': prediction.get('analisis_sintesis', ''),
            'risk_posture': prediction.get('postura_riesgo', 'NEUTRAL')
        }
        
        result = self.opinion_api.submit_prediction(prediction_data)
        
        return result
    
    def get_competition_status(self) -> Dict:
        """
        Obtiene el estado actual de la competencia para todas las IAs.
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'simulation_mode': self.simulation_mode,
            'daily_cycles_completed': self.daily_analysis_count,
            'firms': {}
        }
        
        for firm_name in self.orchestrator.get_all_firms().keys():
            risk_manager = self.risk_managers[firm_name]
            bankroll_manager = self.bankroll_managers[firm_name]
            
            firm_status = {
                'risk': risk_manager.get_status_report(),
                'bankroll': bankroll_manager.get_statistics(),
                'ranking_score': self._calculate_ranking_score(bankroll_manager, risk_manager)
            }
            
            status['firms'][firm_name] = firm_status
        
        status['leaderboard'] = self._generate_leaderboard()
        
        return status
    
    def _calculate_ranking_score(self, bankroll_manager: BankrollManager, 
                                  risk_manager: RiskManager) -> float:
        """
        Calcula un score de ranking combinando ROI, Sharpe y win rate.
        """
        stats = bankroll_manager.get_statistics()
        
        roi = stats.get('total_return_pct', 0)
        win_rate = stats.get('win_rate', 0)
        
        total_bets = stats.get('total_bets', 0)
        if total_bets < 5:
            return 0
        
        score = (roi * 0.5) + (win_rate * 0.3) + (total_bets * 0.2)
        
        return score
    
    def _generate_leaderboard(self) -> List[Dict]:
        """
        Genera tabla de posiciones ordenada por performance.
        """
        leaderboard = []
        
        for firm_name in self.orchestrator.get_all_firms().keys():
            bankroll_manager = self.bankroll_managers[firm_name]
            risk_manager = self.risk_managers[firm_name]
            
            stats = bankroll_manager.get_statistics()
            
            leaderboard.append({
                'firm_name': firm_name,
                'current_bankroll': stats['current_bankroll'],
                'total_profit': stats['total_profit'],
                'return_pct': stats['total_return_pct'],
                'win_rate': stats['win_rate'],
                'total_bets': stats['total_bets'],
                'risk_level': risk_manager.get_risk_level().value,
                'ranking_score': self._calculate_ranking_score(bankroll_manager, risk_manager)
            })
        
        leaderboard.sort(key=lambda x: x['ranking_score'], reverse=True)
        
        for i, entry in enumerate(leaderboard):
            entry['position'] = i + 1
        
        return leaderboard
