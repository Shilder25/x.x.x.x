from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from opinion_trade_api import OpinionTradeAPI
from risk_management import RiskManager, RiskLevel
from bankroll_manager import BankrollManager, BettingStrategy, assign_strategy_to_firm
from llm_clients import FirmOrchestrator
from data_collectors import AlphaVantageCollector, YFinanceCollector, RedditSentimentCollector, NewsCollector, VolatilityCollector
from prompt_system import create_trading_prompt, format_technical_report, format_fundamental_report, format_sentiment_report, format_news_report, format_volatility_report
from database import TradingDatabase
from learning_system import LearningSystem
import os

class AutonomousEngine:
    """
    Motor de decisión autónoma que analiza múltiples eventos de Opinion.trade
    y ejecuta apuestas automáticas para cada IA respetando límites de riesgo.
    """
    
    def __init__(self, database: TradingDatabase, initial_bankroll_per_firm: float = 1000.0, simulation_mode: bool = True):
        """
        Args:
            database: Instancia de TradingDatabase para persistencia
            initial_bankroll_per_firm: Presupuesto inicial por cada IA
            simulation_mode: Si True, no ejecuta apuestas reales (solo tracking virtual)
        """
        system_enabled = os.environ.get('SYSTEM_ENABLED', 'false').lower() == 'true'
        self.simulation_mode = simulation_mode if system_enabled else True
        self.system_enabled = system_enabled
        self.initial_bankroll = initial_bankroll_per_firm
        
        self.db = database
        self.learning_system = LearningSystem(database)
        
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
        self.last_learning_analysis = None
        
        self._data_cache = {}
    
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
        Ejecuta el ciclo diario completo con análisis multi-categoría:
        1. Obtener eventos disponibles de Opinion.trade por categorías
        2. Para cada IA, analizar eventos en TODAS las categorías disponibles
        3. Decidir la mejor oportunidad entre todas las categorías
        4. Ejecutar apuestas respetando límites de riesgo
        5. Registrar todo en base de datos
        
        Note: System can be disabled via SYSTEM_ENABLED=false in Replit Secrets
        
        Returns:
            Resumen de la ejecución diaria
        """
        if not self.system_enabled:
            return {
                'status': 'disabled',
                'message': 'System disabled via SYSTEM_ENABLED environment variable',
                'timestamp': datetime.now().isoformat()
            }
        cycle_start = datetime.now()
        
        self._data_cache.clear()
        print(f"[CACHE] Cleared data cache at start of cycle {cycle_start.isoformat()}")
        
        results = {
            'timestamp': cycle_start.isoformat(),
            'simulation_mode': self.simulation_mode,
            'firms_results': {},
            'total_bets_placed': 0,
            'total_bets_skipped': 0,
            'categories_analyzed': [],
            'errors': []
        }
        
        # Obtener eventos agrupados por categoría
        events_by_category = self._fetch_events_by_category()
        
        if not events_by_category:
            results['errors'].append("No events available in any category")
            return results
        
        results['categories_analyzed'] = list(events_by_category.keys())
        results['total_events_analyzed'] = sum(len(events) for events in events_by_category.values())
        
        # Cada IA analiza eventos en TODAS las categorías antes de decidir
        for firm_name in self.orchestrator.get_all_firms().keys():
            firm_result = self._process_firm_multi_category_cycle(firm_name, events_by_category)
            results['firms_results'][firm_name] = firm_result
            results['total_bets_placed'] += firm_result.get('bets_placed', 0)
            results['total_bets_skipped'] += firm_result.get('bets_skipped', 0)
        
        self.db.save_autonomous_cycle(results)
        
        self.execution_log.append(results)
        self.daily_analysis_count += 1
        
        self._check_weekly_learning()
        
        # Reconciliar apuestas activas que ya fueron resueltas
        reconciliation_stats = self.reconcile_bets()
        results['reconciliation'] = reconciliation_stats
        
        return results
    
    def _fetch_events_by_category(self) -> Dict[str, List[Dict]]:
        """
        Obtiene eventos disponibles organizados por categoría.
        
        Returns:
            Dict con categorías como keys y listas de eventos como values
        """
        events_by_category = {}
        
        # Primero obtener todos los eventos para ver qué categorías hay
        all_events_response = self.opinion_api.get_available_events(limit=100)
        
        if not all_events_response.get('success'):
            return events_by_category
        
        all_events = all_events_response.get('events', [])
        
        # Agrupar por categoría
        for event in all_events:
            category = event.get('category', 'general')
            if category not in events_by_category:
                events_by_category[category] = []
            events_by_category[category].append(event)
        
        return events_by_category
    
    def _process_firm_multi_category_cycle(self, firm_name: str, events_by_category: Dict[str, List[Dict]]) -> Dict:
        """
        Procesa el ciclo completo para una IA con análisis multi-categoría.
        
        La IA analiza eventos en TODAS las categorías disponibles PRIMERO,
        luego ejecuta solo las mejores oportunidades globales.
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
            'category_analysis': {},
            'decisions': []
        }
        
        risk_status = risk_manager.get_status_report()
        if risk_status.get('in_cooldown'):
            firm_result['skipped_reason'] = f"In cooldown until {risk_status.get('cooldown_until')}"
            return firm_result
        
        active_positions_response = self.opinion_api.get_active_positions()
        active_positions = active_positions_response.get('positions', []) if active_positions_response.get('success') else []
        
        # Fase 1: EVALUAR (sin ejecutar) oportunidades en cada categoría
        all_opportunities = []
        
        for category, events in events_by_category.items():
            category_result = {
                'category': category,
                'events_analyzed': 0,
                'opportunities_found': 0,
                'best_opportunity': None,
                'avg_expected_value': 0
            }
            
            category_opportunities = []
            
            # Evaluar top 3 eventos de cada categoría (sin ejecutar)
            for event in events[:3]:
                evaluation = self._evaluate_event_opportunity(
                    firm_name=firm_name,
                    event=event,
                    risk_manager=risk_manager,
                    bankroll_manager=bankroll_manager,
                    active_positions=active_positions
                )
                
                firm_result['events_analyzed'] += 1
                category_result['events_analyzed'] += 1
                
                if evaluation.get('is_opportunity'):
                    category_opportunities.append(evaluation)
                    all_opportunities.append(evaluation)
                    category_result['opportunities_found'] += 1
                else:
                    firm_result['bets_skipped'] += 1
            
            # Registrar mejor oportunidad de esta categoría
            if category_opportunities:
                best_in_category = max(category_opportunities, key=lambda x: x.get('expected_value', 0))
                category_result['best_opportunity'] = {
                    'event_id': best_in_category.get('event_id'),
                    'expected_value': best_in_category.get('expected_value'),
                    'probability': best_in_category.get('probability')
                }
                category_result['avg_expected_value'] = sum(o.get('expected_value', 0) for o in category_opportunities) / len(category_opportunities)
            
            firm_result['category_analysis'][category] = category_result
        
        # Fase 2: Ejecutar solo las MEJORES oportunidades globales
        if all_opportunities:
            # Ordenar todas las oportunidades por expected value
            all_opportunities.sort(key=lambda x: x.get('expected_value', 0), reverse=True)
            
            # Ejecutar solo hasta alcanzar el límite de apuestas concurrentes
            max_bets = min(risk_manager.max_concurrent_bets, len(all_opportunities))
            
            for i, opportunity in enumerate(all_opportunities):
                if i < max_bets:
                    # Ejecutar esta oportunidad
                    executed_decision = self._execute_opportunity(
                        firm_name=firm_name,
                        opportunity=opportunity,
                        risk_manager=risk_manager,
                        bankroll_manager=bankroll_manager
                    )
                    firm_result['decisions'].append(executed_decision)
                    
                    # Solo incrementar si la ejecución fue exitosa
                    if executed_decision.get('action') == 'BET':
                        firm_result['bets_placed'] += 1
                        firm_result['total_bet_amount'] += executed_decision.get('bet_size', 0)
                    else:
                        firm_result['bets_skipped'] += 1
                else:
                    # Oportunidad no seleccionada para ejecución
                    firm_result['bets_skipped'] += 1
        
        return firm_result
    
    def _process_firm_cycle(self, firm_name: str, events: List[Dict]) -> Dict:
        """
        Procesa el ciclo completo para una IA específica (método legacy).
        Mantenido para compatibilidad.
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
    
    def _evaluate_event_opportunity(self, firm_name: str, event: Dict,
                                    risk_manager: RiskManager, 
                                    bankroll_manager: BankrollManager,
                                    active_positions: List[Dict]) -> Dict:
        """
        Evalúa un evento SIN EJECUTAR la apuesta.
        Solo determina si es una buena oportunidad y calcula métricas.
        
        Returns:
            Dict con is_opportunity, expected_value, bet_size, etc.
        """
        event_id = event.get('id', 'unknown')
        event_description = event.get('description', event.get('title', 'Unknown event'))
        category = event.get('category', 'general')
        
        evaluation = {
            'event': event,
            'event_id': event_id,
            'event_description': event_description,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'is_opportunity': False,
            'reason': '',
            'bet_size': 0,
            'probability': 0,
            'confidence': 0,
            'expected_value': 0
        }
        
        symbol = self._extract_symbol_from_event(event)
        
        try:
            prediction = self._get_firm_prediction(firm_name, event_description, symbol or '')
            
            if 'error' in prediction:
                evaluation['reason'] = f"Prediction error: {prediction.get('error')}"
                return evaluation
            
            probability = prediction.get('probabilidad_final_prediccion', 0.5)
            confidence = prediction.get('nivel_confianza', 50)
            
            expected_value = self._calculate_expected_value(probability)
            
            evaluation['probability'] = probability
            evaluation['confidence'] = confidence
            evaluation['expected_value'] = expected_value
            evaluation['prediction'] = prediction
            
            should_bet, bet_reason = bankroll_manager.should_bet(probability, confidence, expected_value)
            
            if not should_bet:
                evaluation['reason'] = bet_reason
                return evaluation
            
            bet_calculation = bankroll_manager.calculate_bet_size(probability, confidence, expected_value)
            
            if bet_calculation.get('bet_size', 0) == 0:
                evaluation['reason'] = bet_calculation.get('reason', 'Bet size calculation returned 0')
                return evaluation
            
            bet_size = bet_calculation['bet_size']
            
            risk_check = risk_manager.can_place_bet(
                bet_amount=bet_size,
                category=category,
                current_positions=active_positions
            )
            
            if not risk_check.get('allowed'):
                evaluation['reason'] = risk_check.get('reason', 'Risk check failed')
                evaluation['risk_check'] = risk_check
                return evaluation
            
            evaluation['is_opportunity'] = True
            evaluation['bet_size'] = bet_size
            evaluation['bet_calculation'] = bet_calculation
            evaluation['risk_check'] = risk_check
            evaluation['reason'] = f"Approved: EV={expected_value:.2f}, Prob={probability:.2%}, Conf={confidence}%"
            
        except Exception as e:
            evaluation['reason'] = f"Exception during evaluation: {str(e)}"
            evaluation['error'] = str(e)
        
        return evaluation
    
    def _execute_opportunity(self, firm_name: str, opportunity: Dict,
                            risk_manager: RiskManager,
                            bankroll_manager: BankrollManager) -> Dict:
        """
        Ejecuta una oportunidad previamente evaluada.
        RE-VALIDA tanto risk check como bankroll constraints con estado fresco.
        Guarda en DB y envía a Opinion.trade si no es simulación.
        Actualiza estado de managers después de ejecutar.
        """
        event_id = opportunity.get('event_id', '')
        event_description = opportunity.get('event_description', '')
        category = opportunity.get('category', 'general')
        probability = opportunity.get('probability', 0.5)
        confidence = opportunity.get('confidence', 50)
        expected_value = opportunity.get('expected_value', 0.0)
        prediction = opportunity.get('prediction', {})
        
        decision = {
            'event_id': event_id,
            'event_description': event_description,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'action': 'BET',
            'probability': probability,
            'confidence': confidence,
            'expected_value': expected_value,
            'reason': opportunity.get('reason', '')
        }
        
        # RE-VALIDAR bankroll constraints con estado ACTUAL (puede haber cambiado)
        should_bet, bet_reason = bankroll_manager.should_bet(probability, confidence, expected_value)
        
        if not should_bet:
            decision['action'] = 'SKIP'
            decision['reason'] = f"Bankroll check failed at execution: {bet_reason}"
            decision['bankroll_check_failed'] = True
            return decision
        
        # RE-CALCULAR bet size con bankroll ACTUAL (reducido por apuestas anteriores)
        bet_calculation = bankroll_manager.calculate_bet_size(probability, confidence, expected_value)
        
        if bet_calculation.get('bet_size', 0) == 0:
            decision['action'] = 'SKIP'
            decision['reason'] = f"Bet size recalculation returned 0: {bet_calculation.get('reason', 'Unknown')}"
            decision['bet_size_recalc_failed'] = True
            return decision
        
        # Usar el bet_size RE-CALCULADO (puede ser menor que el original)
        bet_size = bet_calculation['bet_size']
        decision['bet_size'] = bet_size
        decision['bet_calculation'] = bet_calculation
        
        # RE-VALIDAR risk check con posiciones activas FRESCAS
        active_positions_response = self.opinion_api.get_active_positions()
        active_positions = active_positions_response.get('positions', []) if active_positions_response.get('success') else []
        
        risk_check = risk_manager.can_place_bet(
            bet_amount=bet_size,
            category=category,
            current_positions=active_positions
        )
        
        if not risk_check.get('allowed'):
            decision['action'] = 'SKIP'
            decision['reason'] = f"Risk check failed at execution: {risk_check.get('reason', 'Unknown')}"
            decision['risk_check_failed'] = True
            return decision
        
        # ACTUALIZAR bankroll ANTES de persistir/ejecutar
        # Esto garantiza que siguientes oportunidades vean el bankroll reducido
        bankroll_manager.record_bet(bet_size, probability, event_id, event_description)
        
        bet_data = {
            'firm_name': firm_name,
            'event_id': event_id,
            'event_description': event_description,
            'category': category,
            'bet_size': bet_size,
            'probability': probability,
            'confidence': confidence,
            'expected_value': expected_value,
            'risk_level': risk_manager.get_risk_level().value,
            'adaptation_level': risk_manager.adaptation_level.value,
            'betting_strategy': bankroll_manager.strategy.value,
            'reasoning': decision.get('reason'),
            'execution_timestamp': datetime.now().isoformat(),
            'simulation_mode': 1 if self.simulation_mode else 0,
            'sentiment_score': prediction.get('sentiment_score', 5),
            'sentiment_analysis': prediction.get('sentiment_analysis', ''),
            'news_score': prediction.get('news_score', 5),
            'news_analysis': prediction.get('news_analysis', ''),
            'technical_score': prediction.get('technical_score', 5),
            'technical_analysis': prediction.get('technical_analysis', ''),
            'fundamental_score': prediction.get('fundamental_score', 5),
            'fundamental_analysis': prediction.get('fundamental_analysis', ''),
            'volatility_score': prediction.get('volatility_score', 5),
            'volatility_analysis': prediction.get('volatility_analysis', '')
        }
        
        bet_id = self.db.save_autonomous_bet(bet_data)
        decision['bet_id'] = bet_id
        
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
        
        return decision
    
    def _analyze_event_for_firm(self, firm_name: str, event: Dict,
                                risk_manager: RiskManager, 
                                bankroll_manager: BankrollManager,
                                active_positions: List[Dict]) -> Dict:
        """
        Analiza un evento específico y decide si apostar (método legacy con ejecución inmediata).
        Usado por el flujo single-category antiguo.
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
            prediction = self._get_firm_prediction(firm_name, event_description, symbol or '')
            
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
            
            bet_data = {
                'firm_name': firm_name,
                'event_id': event_id,
                'event_description': event_description,
                'category': category,
                'bet_size': bet_size,
                'probability': probability,
                'confidence': confidence,
                'expected_value': expected_value,
                'risk_level': risk_manager.get_risk_level().value,
                'adaptation_level': risk_manager.adaptation_level.value,
                'betting_strategy': bankroll_manager.strategy.value,
                'reasoning': decision.get('reason'),
                'execution_timestamp': datetime.now().isoformat(),
                'simulation_mode': 1 if self.simulation_mode else 0,
                'sentiment_score': prediction.get('sentiment_score', 5),
                'sentiment_analysis': prediction.get('sentiment_analysis', ''),
                'news_score': prediction.get('news_score', 5),
                'news_analysis': prediction.get('news_analysis', ''),
                'technical_score': prediction.get('technical_score', 5),
                'technical_analysis': prediction.get('technical_analysis', ''),
                'fundamental_score': prediction.get('fundamental_score', 5),
                'fundamental_analysis': prediction.get('fundamental_analysis', ''),
                'volatility_score': prediction.get('volatility_score', 5),
                'volatility_analysis': prediction.get('volatility_analysis', '')
            }
            
            bet_id = self.db.save_autonomous_bet(bet_data)
            decision['bet_id'] = bet_id
            
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
        Obtiene predicción de una IA para un evento específico, recolectando datos de 5 áreas.
        Usa caché compartido para reducir llamadas a APIs externas cuando múltiples firmas analizan el mismo símbolo.
        """
        technical_report = "Not available"
        fundamental_report = "Not available"
        sentiment_report = "Not available"
        news_report = "Not available"
        volatility_report = "Not available"
        
        if symbol and self.alpha_vantage_key:
            cache_key_tech = f"tech_{symbol}"
            cache_key_news = f"news_{symbol}"
            cache_key_vol = f"vol_{symbol}"
            
            if cache_key_tech in self._data_cache:
                tech_data = self._data_cache[cache_key_tech]
                technical_report = format_technical_report(tech_data)
                print(f"[CACHE HIT] Technical data for {symbol}")
            else:
                try:
                    collector = AlphaVantageCollector(self.alpha_vantage_key)
                    tech_data = collector.get_technical_indicators(symbol)
                    if 'error' not in tech_data:
                        self._data_cache[cache_key_tech] = tech_data
                        print(f"[CACHE MISS] Fetched & cached technical data for {symbol}")
                    else:
                        print(f"[CACHE SKIP] Technical data error for {symbol}, not caching")
                    technical_report = format_technical_report(tech_data)
                except Exception as e:
                    print(f"[CACHE ERROR] Failed to fetch technical data for {symbol}: {e}")
                    pass
            
            if cache_key_news in self._data_cache:
                news_data = self._data_cache[cache_key_news]
                news_report = format_news_report(news_data)
                print(f"[CACHE HIT] News data for {symbol}")
            else:
                try:
                    news_collector = NewsCollector(alpha_vantage_key=self.alpha_vantage_key)
                    news_data = news_collector.get_news_analysis(symbol, event_description)
                    if 'error' not in news_data:
                        self._data_cache[cache_key_news] = news_data
                        print(f"[CACHE MISS] Fetched & cached news data for {symbol}")
                    else:
                        print(f"[CACHE SKIP] News data error for {symbol}, not caching")
                    news_report = format_news_report(news_data)
                except Exception as e:
                    print(f"[CACHE ERROR] Failed to fetch news data for {symbol}: {e}")
                    pass
            
            if cache_key_vol in self._data_cache:
                volatility_data = self._data_cache[cache_key_vol]
                volatility_report = format_volatility_report(volatility_data)
                print(f"[CACHE HIT] Volatility data for {symbol}")
            else:
                try:
                    volatility_collector = VolatilityCollector()
                    
                    if symbol in ['BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 'XRP']:
                        crypto_symbol = f"{symbol}-USD"
                    else:
                        crypto_symbol = symbol
                    
                    volatility_data = volatility_collector.get_volatility_metrics(crypto_symbol)
                    if 'error' not in volatility_data:
                        self._data_cache[cache_key_vol] = volatility_data
                        print(f"[CACHE MISS] Fetched & cached volatility data for {crypto_symbol}")
                    else:
                        print(f"[CACHE SKIP] Volatility data error for {crypto_symbol}, not caching")
                    volatility_report = format_volatility_report(volatility_data)
                except Exception as e:
                    print(f"[CACHE ERROR] Failed to fetch volatility data for {symbol}: {e}")
                    pass
        
        try:
            firm = self.orchestrator.get_all_firms()[firm_name]
            
            prompt = create_trading_prompt(
                event_description=event_description,
                technical_report=technical_report,
                fundamental_report=fundamental_report,
                sentiment_report=sentiment_report,
                news_report=news_report,
                volatility_report=volatility_report,
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
    
    def _check_weekly_learning(self):
        """
        Verifica si es tiempo de ejecutar análisis semanal de aprendizaje.
        """
        if self.last_learning_analysis is None:
            self.last_learning_analysis = datetime.now()
            return
        
        days_since_last = (datetime.now() - self.last_learning_analysis).days
        
        if days_since_last >= 7:
            self._run_weekly_learning_analysis()
            self.last_learning_analysis = datetime.now()
    
    def _run_weekly_learning_analysis(self):
        """
        Ejecuta análisis de aprendizaje semanal para todas las IAs.
        """
        cross_insights = self.learning_system.generate_cross_learning_insights()
        
        for firm_name in self.orchestrator.get_all_firms().keys():
            analysis = self.learning_system.analyze_weekly_performance(firm_name)
            
            if analysis.get('status') not in ['insufficient_data', 'no_recent_activity']:
                recommendations = analysis.get('recommendations', [])
                
                pass
    
    def reconcile_bets(self) -> Dict:
        """
        Sistema de reconciliación que consulta Opinion.trade para actualizar
        resultados de apuestas activas que ya fueron resueltas.
        
        Returns:
            Dictionary con estadísticas de reconciliación
        """
        stats = {
            'total_active': 0,
            'checked': 0,
            'resolved': 0,
            'updated': 0,
            'errors': 0,
            'by_firm': {}
        }
        
        # Obtener todas las apuestas activas (sin resultado)
        all_active_bets = self.db.get_autonomous_bets(firm_name=None, limit=1000)
        active_bets = [bet for bet in all_active_bets if bet.get('actual_result') is None]
        
        stats['total_active'] = len(active_bets)
        
        for bet in active_bets:
            firm_name = bet.get('firm_name')
            bet_id = bet.get('id')
            opinion_trade_id = bet.get('opinion_trade_id')
            bet_size = bet.get('bet_size', 0)
            
            if firm_name not in stats['by_firm']:
                stats['by_firm'][firm_name] = {
                    'checked': 0,
                    'resolved': 0,
                    'errors': 0
                }
            
            # Si no hay opinion_trade_id (modo simulación), skip
            if not opinion_trade_id:
                continue
            
            stats['checked'] += 1
            stats['by_firm'][firm_name]['checked'] += 1
            
            # Consultar Opinion.trade para ver si fue resuelta
            try:
                result = self.opinion_api.get_prediction_result(opinion_trade_id)
                
                if not result.get('success'):
                    # Log cuando Opinion.trade devuelve error
                    self.execution_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'reconciliation_api_error',
                        'firm_name': firm_name,
                        'bet_id': bet_id,
                        'error': result.get('error', 'Unknown API error'),
                        'message': result.get('message', '')
                    })
                    continue
                
                if result.get('resolved'):
                    # La apuesta fue resuelta
                    outcome = result.get('outcome')  # 1 (ganó) o 0 (perdió)
                    profit_loss = result.get('profit_loss', 0)
                    
                    # Actualizar en la base de datos
                    self.db.update_autonomous_bet_result(
                        bet_id=bet_id,
                        actual_result=outcome,
                        profit_loss=profit_loss
                    )
                    
                    # Actualizar bankroll manager
                    if firm_name in self.bankroll_managers:
                        bankroll_manager = self.bankroll_managers[firm_name]
                        bankroll_manager.record_result(
                            bet_id=bet_id,
                            won=(outcome == 1),
                            profit_loss=profit_loss
                        )
                    
                    stats['resolved'] += 1
                    stats['updated'] += 1
                    stats['by_firm'][firm_name]['resolved'] += 1
                    
                    self.execution_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'reconciliation',
                        'firm_name': firm_name,
                        'bet_id': bet_id,
                        'outcome': 'won' if outcome == 1 else 'lost',
                        'profit_loss': profit_loss
                    })
                    
            except Exception as e:
                stats['errors'] += 1
                stats['by_firm'][firm_name]['errors'] += 1
                self.execution_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'reconciliation_error',
                    'firm_name': firm_name,
                    'bet_id': bet_id,
                    'error': str(e)
                })
        
        return stats
    
    def apply_risk_adaptation(self, firm_name: str, adaptation_level):
        """
        Aplica adaptación de riesgo y la persiste en la base de datos.
        """
        risk_manager = self.risk_managers[firm_name]
        bankroll_manager = self.bankroll_managers[firm_name]
        
        total_loss_pct = (risk_manager.initial_bankroll - risk_manager.current_bankroll) / risk_manager.initial_bankroll
        
        learning_analysis = self.learning_system.analyze_weekly_performance(firm_name)
        analysis_data = None
        
        if learning_analysis.get('status') not in ['insufficient_data', 'no_recent_activity']:
            analysis_data = {
                'successful_patterns': learning_analysis.get('category_performance', {})
            }
        
        adaptation_details = risk_manager.apply_adaptation(adaptation_level, analysis_data)
        
        adaptation_db_data = {
            'firm_name': firm_name,
            'level': adaptation_level.value,
            'description': adaptation_details.get('description'),
            'previous_params': adaptation_details.get('previous_params'),
            'new_params': adaptation_details.get('new_params'),
            'changes': adaptation_details.get('changes'),
            'bankroll_at_adaptation': risk_manager.current_bankroll,
            'loss_percentage': total_loss_pct * 100,
            'timestamp': adaptation_details.get('timestamp')
        }
        
        self.db.save_strategy_adaptation(adaptation_db_data)
        
        return adaptation_details
