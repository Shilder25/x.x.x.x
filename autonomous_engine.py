from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from opinion_trade_api import OpinionTradeAPI
from tier_risk_guard import TierRiskGuard
from risk_tiers import risk_config
from bankroll_manager import BankrollManager, BettingStrategy, assign_strategy_to_firm
from llm_clients import FirmOrchestrator
from data_collectors import AlphaVantageCollector, YFinanceCollector, RedditSentimentCollector, NewsCollector, VolatilityCollector
from prompt_system import create_trading_prompt, format_technical_report, format_fundamental_report, format_sentiment_report, format_news_report, format_volatility_report
from database import TradingDatabase
from learning_system import LearningSystem
from logger import autonomous_logger as logger
import os

class AutonomousEngine:
    """
    Motor de decisión autónoma que analiza múltiples eventos de Opinion.trade
    y ejecuta apuestas automáticas para cada IA respetando límites de riesgo.
    """
    
    def __init__(self, database: TradingDatabase, initial_bankroll_per_firm: float = 1000.0):
        """
        Args:
            database: Instancia de TradingDatabase para persistencia
            initial_bankroll_per_firm: Presupuesto inicial por cada IA (ignorado si BANKROLL_MODE está configurado)
        
        Note: Sistema siempre opera en modo real (no simulation). 
        BANKROLL_MODE env var controla cantidades:
        - TEST: $50 inicial, máximo $5 por día (protección para pruebas)
        - PRODUCTION: $5000 inicial, sin límite diario
        """
        system_enabled = os.environ.get('SYSTEM_ENABLED', 'false').lower() == 'true'
        self.system_enabled = system_enabled
        
        # Configurar bankroll según BANKROLL_MODE
        bankroll_mode = os.environ.get('BANKROLL_MODE', 'TEST').upper()
        if bankroll_mode == 'PRODUCTION':
            self.initial_bankroll = 5000.0
            self.daily_bet_limit = None  # Sin límite
            self.bankroll_mode = 'PRODUCTION'
        else:  # TEST mode (default)
            self.initial_bankroll = 50.0
            self.daily_bet_limit = 5.0  # Máximo $5 por día
            self.bankroll_mode = 'TEST'
        
        logger.bankroll(f"{self.bankroll_mode} - Initial: ${self.initial_bankroll}, Daily limit: ${self.daily_bet_limit if self.daily_bet_limit else 'None'}")
        
        self.db = database
        self.learning_system = LearningSystem(database)
        
        self.opinion_api = OpinionTradeAPI()
        self.orchestrator = FirmOrchestrator()
        
        self.alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
        self.reddit_client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        self.reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        
        self.risk_guard = TierRiskGuard(database, risk_config)
        self.bankroll_managers = {}
        
        self._initialize_firms()
        
        self.execution_log = []
        self.daily_analysis_count = 0
        self.last_learning_analysis = None
        
        self._data_cache = {}
    
    def _initialize_firms(self):
        """
        Inicializa gestores de bankroll para cada IA.
        """
        firms = self.orchestrator.get_all_firms()
        
        for firm_name in firms.keys():
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
        logger.cache(f"Cleared data cache at start of cycle {cycle_start.isoformat()}")
        
        results = {
            'timestamp': cycle_start.isoformat(),
            'simulation_mode': 0,
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
        
        # Get available events (Opinion.trade SDK max limit: 20 per request)
        all_events_response = self.opinion_api.get_available_events(limit=20)
        
        if not all_events_response.get('success'):
            error_msg = all_events_response.get('message', 'Unknown error')
            logger.error(f"Failed to fetch events from Opinion.trade: {logger.sanitize_text(error_msg, 100)}")
            return events_by_category
        
        all_events = all_events_response.get('events', [])
        logger.info(f"Fetched {len(all_events)} events from Opinion.trade")
        
        # Filtrar eventos de Sports (categoría excluida)
        filtered_events = [event for event in all_events if event.get('category', 'general') != 'Sports']
        sports_filtered = len(all_events) - len(filtered_events)
        if sports_filtered > 0:
            logger.info(f"Filtered out {sports_filtered} Sports events (category excluded)")
        
        # Agrupar por categoría
        for event in filtered_events:
            category = event.get('category', 'general')
            if category not in events_by_category:
                events_by_category[category] = []
            events_by_category[category].append(event)
        
        categories_summary = {cat: len(events) for cat, events in events_by_category.items()}
        logger.category(f"Events grouped into {len(events_by_category)} categories: {categories_summary}")
        return events_by_category
    
    def _process_firm_multi_category_cycle(self, firm_name: str, events_by_category: Dict[str, List[Dict]]) -> Dict:
        """
        Procesa el ciclo completo para una IA con análisis multi-categoría.
        
        La IA analiza eventos en TODAS las categorías disponibles PRIMERO,
        luego ejecuta solo las mejores oportunidades globales.
        """
        logger.info(f"\nProcessing cycle for {firm_name}")
        logger.analysis(firm_name, f"Analyzing {len(events_by_category)} categories")
        
        tier_status = self.risk_guard.get_tier_status(firm_name)
        bankroll_manager = self.bankroll_managers[firm_name]
        
        firm_result = {
            'firm_name': firm_name,
            'events_analyzed': 0,
            'bets_placed': 0,
            'bets_skipped': 0,
            'total_bet_amount': 0,
            'risk_tier': tier_status.get('current_tier', 'conservative'),
            'current_balance': tier_status.get('current_balance', 0),
            'category_analysis': {},
            'decisions': []
        }
        
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
            logger.analysis(firm_name, f"Found {len(all_opportunities)} total opportunities across all categories")
            # Ordenar todas las oportunidades por expected value
            all_opportunities.sort(key=lambda x: x.get('expected_value', 0), reverse=True)
            
            # Ejecutar solo hasta alcanzar el límite de apuestas concurrentes
            tier_config = tier_status.get('tier_config', {})
            max_bets = min(tier_config.get('max_concurrent_positions', 2), len(all_opportunities))
            logger.analysis(firm_name, f"Will execute top {max_bets} opportunities (max_concurrent_positions: {tier_config.get('max_concurrent_positions', 2)})")
            
            for i, opportunity in enumerate(all_opportunities):
                if i < max_bets:
                    # Verificar límite diario GLOBAL ANTES de ejecutar (solo en TEST mode)
                    if self.daily_bet_limit is not None:
                        current_daily_total = self.db.get_daily_bet_total()
                        proposed_bet_size = opportunity.get('bet_size', 0)
                        
                        if current_daily_total + proposed_bet_size > self.daily_bet_limit:
                            logger.info(f"{firm_name} - Proposed ${proposed_bet_size:.2f} would exceed daily limit "
                                  f"(${current_daily_total:.2f} + ${proposed_bet_size:.2f} > ${self.daily_bet_limit})", prefix="DAILY LIMIT")
                            firm_result['bets_skipped'] += 1
                            continue
                    
                    # Ejecutar esta oportunidad
                    executed_decision = self._execute_opportunity(
                        firm_name=firm_name,
                        opportunity=opportunity,
                        bankroll_manager=bankroll_manager
                    )
                    firm_result['decisions'].append(executed_decision)
                    
                    # Solo incrementar si la ejecución fue exitosa
                    logger.analysis(firm_name, f"Executed bet {i+1}/{max_bets}")
                    # Solo incrementar si la ejecución fue exitosa
                    if executed_decision.get('action') == 'BET':
                        firm_result['bets_placed'] += 1
                        bet_size = executed_decision.get('bet_size', 0)
                        firm_result['total_bet_amount'] += bet_size
                        
                        # Registrar en tracking diario (solo en TEST mode)
                        if self.daily_bet_limit is not None:
                            new_daily_total = self.db.add_to_daily_bet_total(bet_size)
                            logger.info(f"{firm_name} - Daily total: ${new_daily_total:.2f} / ${self.daily_bet_limit}", prefix="DAILY TRACKING")
                    else:
                        firm_result['bets_skipped'] += 1
                else:
                    # Oportunidad no seleccionada para ejecución
                    firm_result['bets_skipped'] += 1
        else:
            logger.analysis(firm_name, "No opportunities found")
        
        logger.analysis(firm_name, f"Cycle complete: {firm_result['bets_placed']} bets placed, {firm_result['bets_skipped']} skipped, {firm_result['events_analyzed']} events analyzed")
        return firm_result
    
    def _process_firm_cycle(self, firm_name: str, events: List[Dict]) -> Dict:
        """
        Procesa el ciclo completo para una IA específica (método legacy).
        Mantenido para compatibilidad.
        """
        tier_status = self.risk_guard.get_tier_status(firm_name)
        bankroll_manager = self.bankroll_managers[firm_name]
        
        firm_result = {
            'firm_name': firm_name,
            'events_analyzed': 0,
            'bets_placed': 0,
            'bets_skipped': 0,
            'total_bet_amount': 0,
            'risk_tier': tier_status.get('current_tier', 'conservative'),
            'current_balance': tier_status.get('current_balance', 0),
            'decisions': []
        }
        
        active_positions_response = self.opinion_api.get_active_positions()
        active_positions = active_positions_response.get('positions', []) if active_positions_response.get('success') else []
        
        for event in events[:10]:
            decision = self._analyze_event_for_firm(
                firm_name=firm_name,
                event=event,
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
            
            tier_config = tier_status.get('tier_config', {})
            if firm_result['bets_placed'] >= tier_config.get('max_concurrent_positions', 2):
                break
        
        return firm_result
    
    def _evaluate_event_opportunity(self, firm_name: str, event: Dict,
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
        market_id = event.get('market_id')
        
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
        
        # PREVENCIÓN DE DUPLICADOS: Verificar si ya existe orden activa en este mercado
        if market_id:
            orders_check = self.opinion_api.get_my_orders(market_id=market_id)
            
            if orders_check.get('success'):
                active_orders = orders_check.get('orders', [])
                
                if active_orders:
                    evaluation['reason'] = f"Duplicate prevention: {len(active_orders)} active order(s) already exist for market {market_id}"
                    logger.info(f"{firm_name} - Skip duplicate: {evaluation['reason']}")
                    logger.log_event_analysis(firm_name, event_description, {}, evaluation, 'SKIP')
                    return evaluation
        
        symbol = self._extract_symbol_from_event(event)
        
        try:
            prediction = self._get_firm_prediction(firm_name, event_description, symbol or '', market_id)
            
            if 'error' in prediction:
                evaluation['reason'] = f"Prediction error: {prediction.get('error')}"
                evaluation['prediction'] = prediction
                logger.log_event_analysis(firm_name, event_description, prediction, evaluation, 'SKIP')
                return evaluation
            
            probability = prediction.get('probabilidad_final_prediccion', 0.5)
            confidence = prediction.get('nivel_confianza', 50)
            
            # Obtener precio real del mercado para cálculo de EV preciso
            market_price = None
            token_id = event.get('yes_token_id') if probability >= 0.5 else event.get('no_token_id')
            
            if token_id:
                price_response = self.opinion_api.get_latest_price(token_id)
                if price_response.get('success'):
                    market_price = price_response.get('price')
            
            # Calcular EV con fees (retorna dict con gross_ev y net_ev)
            ev_calc = self._calculate_expected_value(
                probability=probability,
                market_price=market_price,  # Precio real del mercado o None
                bet_size=10.0  # Tamaño nominal para cálculo inicial
            )
            
            evaluation['probability'] = probability
            evaluation['confidence'] = confidence
            evaluation['expected_value'] = ev_calc['net_ev']  # Usar net EV para decisiones
            evaluation['gross_ev'] = ev_calc['gross_ev']
            evaluation['fee_cost'] = ev_calc['fee_cost']
            evaluation['prediction'] = prediction
            
            # Usar net_ev para decisión de apuesta
            should_bet, bet_reason = bankroll_manager.should_bet(probability, confidence, ev_calc['net_ev'])
            
            if not should_bet:
                evaluation['reason'] = bet_reason
                logger.log_event_analysis(firm_name, event_description, prediction, evaluation, 'SKIP')
                return evaluation
            
            bet_calculation = bankroll_manager.calculate_bet_size(probability, confidence, ev_calc['net_ev'])
            
            if bet_calculation.get('bet_size', 0) == 0:
                evaluation['reason'] = bet_calculation.get('reason', 'Bet size calculation returned 0')
                logger.log_event_analysis(firm_name, event_description, prediction, evaluation, 'SKIP')
                return evaluation
            
            bet_size = bet_calculation['bet_size']
            
            allowed, risk_reason = self.risk_guard.can_place_bet(
                firm_name=firm_name,
                bet_amount=bet_size,
                active_positions=active_positions
            )
            
            if not allowed:
                evaluation['reason'] = risk_reason or 'Risk check failed'
                logger.log_risk_block(firm_name, risk_reason)
                logger.log_event_analysis(firm_name, event_description, prediction, evaluation, 'SKIP')
                return evaluation
            
            evaluation['is_opportunity'] = True
            evaluation['bet_size'] = bet_size
            evaluation['bet_calculation'] = bet_calculation
            evaluation['reason'] = f"Approved: Net EV={ev_calc['net_ev']:.2f}, Prob={probability:.2%}, Conf={confidence}%"
            
        except Exception as e:
            evaluation['reason'] = f"Exception during evaluation: {str(e)}"
            evaluation['error'] = str(e)
            logger.log_event_analysis(firm_name, event_description, {}, evaluation, 'SKIP')
            return evaluation
        
        # Log análisis detallado del evento (caso de oportunidad aprobada)
        logger.log_event_analysis(firm_name, event_description, prediction, evaluation, 'BET')
        
        return evaluation
    
    def _execute_opportunity(self, firm_name: str, opportunity: Dict,
                            bankroll_manager: BankrollManager) -> Dict:
        """
        Ejecuta una oportunidad previamente evaluada.
        RE-VALIDA tanto risk check como bankroll constraints con estado fresco.
        Guarda en DB y envía a Opinion.trade si no es simulación.
        Actualiza estado de managers después de ejecutar.
        """
        event = opportunity.get('event', {})
        event_id = opportunity.get('event_id', '')
        event_description = opportunity.get('event_description', '')
        category = opportunity.get('category', 'general')
        probability = opportunity.get('probability', 0.5)
        confidence = opportunity.get('confidence', 50)
        net_ev = opportunity.get('expected_value', 0.0)  # expected_value ya es net_ev del evaluation
        prediction = opportunity.get('prediction', {})
        
        decision = {
            'event_id': event_id,
            'event_description': event_description,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'action': 'BET',
            'probability': probability,
            'confidence': confidence,
            'expected_value': net_ev,
            'reason': opportunity.get('reason', '')
        }
        
        # RE-VALIDAR bankroll constraints con estado ACTUAL (puede haber cambiado)
        should_bet, bet_reason = bankroll_manager.should_bet(probability, confidence, net_ev)
        
        if not should_bet:
            decision['action'] = 'SKIP'
            decision['reason'] = f"Bankroll check failed at execution: {bet_reason}"
            decision['bankroll_check_failed'] = True
            return decision
        
        # RE-CALCULAR bet size con bankroll ACTUAL (reducido por apuestas anteriores)
        bet_calculation = bankroll_manager.calculate_bet_size(probability, confidence, net_ev)
        
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
        
        allowed, risk_reason = self.risk_guard.can_place_bet(
            firm_name=firm_name,
            bet_amount=bet_size,
            active_positions=active_positions
        )
        
        if not allowed:
            decision['action'] = 'SKIP'
            decision['reason'] = f"Risk check failed at execution: {risk_reason}"
            print(f"[RISK BLOCK] {firm_name} - {risk_reason}")
            return decision
        
        # EJECUTAR PRIMERO - solo persistir si tiene éxito
        # Esto evita inconsistencia de estado si la ejecución falla
        execution_result = self._execute_bet(
            firm_name=firm_name,
            event=event,
            event_description=event_description,
            bet_size=bet_size,
            probability=probability,
            prediction=prediction
        )
        decision['execution'] = execution_result
        
        # Si la ejecución falló, retornar sin persistir
        if execution_result.get('status') != 'success':
            decision['action'] = 'SKIP'
            decision['reason'] = f"Execution failed: {execution_result.get('error', 'Unknown error')}"
            print(f"[EXECUTION FAILED] {firm_name} - {decision['reason']}")
            return decision
        
        # Solo si la ejecución fue exitosa → persistir en bankroll y DB (con rollback si falla)
        try:
            bankroll_manager.record_bet(bet_size, probability, event_id, event_description)
            
            bet_data = {
                'firm_name': firm_name,
                'event_id': event_id,
                'event_description': event_description,
                'category': category,
                'bet_size': bet_size,
                'probability': probability,
                'confidence': confidence,
                'expected_value': net_ev,
                'betting_strategy': bankroll_manager.strategy.value,
                'reasoning': decision.get('reason'),
                'execution_timestamp': datetime.now().isoformat(),
                'simulation_mode': 0,
                'sentiment_score': prediction.get('sentiment_score', 5),
                'sentiment_analysis': prediction.get('sentiment_analysis', ''),
                'news_score': prediction.get('news_score', 5),
                'news_analysis': prediction.get('news_analysis', ''),
                'technical_score': prediction.get('technical_score', 5),
                'technical_analysis': prediction.get('technical_analysis', ''),
                'fundamental_score': prediction.get('fundamental_score', 5),
                'fundamental_analysis': prediction.get('fundamental_analysis', ''),
                'volatility_score': prediction.get('volatility_score', 5),
                'volatility_analysis': prediction.get('volatility_analysis', ''),
                'probability_reasoning': prediction.get('probability_reasoning', ''),
                'market_volume': float(event.get('volume', 0)) if event.get('volume') else None,
                'market_yes_pool': None,
                'market_no_pool': None
            }
            
            # Log warning if probability_reasoning is missing (transparency chain validation)
            if not bet_data.get('probability_reasoning'):
                print(f"[WARNING] {firm_name} - Missing probability_reasoning in prediction for event: {event_description[:50]}")
            
            bet_id = self.db.save_autonomous_bet(bet_data)
            decision['bet_id'] = bet_id
            
        except Exception as persist_error:
            # ROLLBACK: Revertir bankroll mutation si persistence falla
            bankroll_manager.rollback_last_bet()
            print(f"[PERSISTENCE ERROR] {firm_name} - Bet executed but persistence failed, bankroll rolled back: {persist_error}")
            decision['action'] = 'ERROR'
            decision['reason'] = f"Persistence failed after successful execution (rolled back): {persist_error}"
            decision['error'] = str(persist_error)
        
        return decision
    
    def _analyze_event_for_firm(self, firm_name: str, event: Dict,
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
            prediction = self._get_firm_prediction(firm_name, event_description, symbol or '', market_id)
            
            if 'error' in prediction:
                decision['reason'] = f"Prediction error: {prediction.get('error')}"
                return decision
            
            probability = prediction.get('probabilidad_final_prediccion', 0.5)
            confidence = prediction.get('nivel_confianza', 50)
            
            # Obtener precio real del mercado para cálculo de EV preciso
            market_price = None
            token_id = event.get('yes_token_id') if probability >= 0.5 else event.get('no_token_id')
            
            if token_id:
                price_response = self.opinion_api.get_latest_price(token_id)
                if price_response.get('success'):
                    market_price = price_response.get('price')
            
            # Calcular EV con fees (retorna dict con gross_ev y net_ev)
            ev_calc = self._calculate_expected_value(
                probability=probability,
                market_price=market_price,  # Precio real del mercado o None
                bet_size=10.0
            )
            
            decision['probability'] = probability
            decision['confidence'] = confidence
            decision['expected_value'] = ev_calc['net_ev']  # Usar net EV
            decision['gross_ev'] = ev_calc['gross_ev']
            decision['fee_cost'] = ev_calc['fee_cost']
            
            should_bet, bet_reason = bankroll_manager.should_bet(probability, confidence, ev_calc['net_ev'])
            
            if not should_bet:
                decision['reason'] = bet_reason
                return decision
            
            bet_calculation = bankroll_manager.calculate_bet_size(probability, confidence, ev_calc['net_ev'])
            
            if bet_calculation.get('bet_size', 0) == 0:
                decision['reason'] = bet_calculation.get('reason', 'Bet size calculation returned 0')
                return decision
            
            bet_size = bet_calculation['bet_size']
            
            allowed, risk_reason = self.risk_guard.can_place_bet(
                firm_name=firm_name,
                bet_amount=bet_size,
                active_positions=active_positions
            )
            
            if not allowed:
                decision['reason'] = risk_reason or 'Risk check failed'
                print(f"[RISK BLOCK] {firm_name} - {risk_reason}")
                return decision
            
            # EJECUTAR PRIMERO - solo persistir si tiene éxito
            execution_result = self._execute_bet(
                firm_name=firm_name,
                event=event,
                event_description=event_description,
                bet_size=bet_size,
                probability=probability,
                prediction=prediction
            )
            decision['execution'] = execution_result
            
            # Si la ejecución falló, retornar sin persistir
            if execution_result.get('status') != 'success':
                decision['action'] = 'SKIP'
                decision['reason'] = f"Execution failed: {execution_result.get('error', 'Unknown error')}"
                print(f"[EXECUTION FAILED] {firm_name} - {decision['reason']}")
                return decision
            
            # Solo si la ejecución fue exitosa → persistir (con rollback si falla)
            decision['action'] = 'BET'
            decision['bet_size'] = bet_size
            decision['bet_calculation'] = bet_calculation
            decision['reason'] = f"Approved: Net EV={ev_calc['net_ev']:.2f}, Prob={probability:.2%}, Conf={confidence}%"
            
            try:
                bankroll_manager.record_bet(bet_size, probability, event_id, event_description)
                
                bet_data = {
                    'firm_name': firm_name,
                    'event_id': event_id,
                    'event_description': event_description,
                    'category': category,
                    'bet_size': bet_size,
                    'probability': probability,
                    'confidence': confidence,
                    'expected_value': ev_calc['net_ev'],
                    'betting_strategy': bankroll_manager.strategy.value,
                    'reasoning': decision.get('reason'),
                    'execution_timestamp': datetime.now().isoformat(),
                    'simulation_mode': 0,
                    'sentiment_score': prediction.get('sentiment_score', 5),
                    'sentiment_analysis': prediction.get('sentiment_analysis', ''),
                    'news_score': prediction.get('news_score', 5),
                    'news_analysis': prediction.get('news_analysis', ''),
                    'technical_score': prediction.get('technical_score', 5),
                    'technical_analysis': prediction.get('technical_analysis', ''),
                    'fundamental_score': prediction.get('fundamental_score', 5),
                    'fundamental_analysis': prediction.get('fundamental_analysis', ''),
                    'volatility_score': prediction.get('volatility_score', 5),
                    'volatility_analysis': prediction.get('volatility_analysis', ''),
                    'probability_reasoning': prediction.get('probability_reasoning', ''),
                    'market_volume': float(event.get('volume', 0)) if event.get('volume') else None,
                    'market_yes_pool': None,
                    'market_no_pool': None
                }
                
                # Log warning if probability_reasoning is missing (transparency chain validation)
                if not bet_data.get('probability_reasoning'):
                    print(f"[WARNING] {firm_name} - Missing probability_reasoning in prediction for event: {event_description[:50]}")
                
                bet_id = self.db.save_autonomous_bet(bet_data)
                decision['bet_id'] = bet_id
                
            except Exception as persist_error:
                # ROLLBACK: Revertir bankroll mutation si persistence falla
                bankroll_manager.rollback_last_bet()
                print(f"[PERSISTENCE ERROR] {firm_name} - Bet executed but persistence failed, bankroll rolled back: {persist_error}")
                decision['action'] = 'ERROR'
                decision['reason'] = f"Persistence failed after successful execution (rolled back): {persist_error}"
                decision['error'] = str(persist_error)
            
        except Exception as e:
            decision['reason'] = f"Exception during analysis: {str(e)}"
            decision['error'] = str(e)
        
        return decision
    
    def _get_firm_prediction(self, firm_name: str, event_description: str, symbol: str, market_id: Optional[str] = None) -> Dict:
        """
        Obtiene predicción de una IA para un evento específico, recolectando datos de 5 áreas.
        Usa caché compartido para reducir llamadas a APIs externas cuando múltiples firmas analizan el mismo símbolo.
        
        Args:
            firm_name: Nombre de la IA/firma
            event_description: Descripción del evento a predecir
            symbol: Símbolo del asset (BTC, AAPL, etc.) si aplica
            market_id: ID del mercado en Opinion.trade (para price history)
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
        
        # Agregar price history como contexto (si disponible)
        price_history_report = ""
        
        if market_id:
            try:
                history_response = self.opinion_api.get_price_history(market_id=market_id, timeframe='24h')
                
                if history_response.get('success'):
                    prices = history_response.get('prices', [])
                    
                    if len(prices) >= 2:
                        first_price = prices[0]
                        last_price = prices[-1]
                        price_change = last_price - first_price
                        price_change_pct = (price_change / first_price * 100) if first_price > 0 else 0
                        
                        trend = "alcista" if price_change > 0 else "bajista" if price_change < 0 else "neutral"
                        
                        price_history_report = f"\n\n**CONTEXTO DE MERCADO (últimas 24h)**:\n"
                        price_history_report += f"- Precio inicial: {first_price:.4f}\n"
                        price_history_report += f"- Precio actual: {last_price:.4f}\n"
                        price_history_report += f"- Cambio: {price_change_pct:+.2f}%\n"
                        price_history_report += f"- Tendencia: {trend.upper()}\n"
                        price_history_report += f"- Datapoints: {len(prices)}\n"
                        price_history_report += f"\n*Nota: Este contexto es informativo. La decisión debe basarse en análisis fundamental.*\n"
            except Exception as e:
                print(f"[INFO] Could not fetch price history for market {market_id}: {e}")
        
        try:
            firm = self.orchestrator.get_all_firms()[firm_name]
            
            # Agregar price history al prompt si disponible
            extended_event_description = event_description
            if price_history_report:
                extended_event_description += price_history_report
            
            prompt = create_trading_prompt(
                event_description=extended_event_description,
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
    
    def _calculate_expected_value(self, probability: float, market_price: Optional[float] = None, bet_size: float = 10.0) -> Dict[str, float]:
        """
        Calcula el valor esperado de una apuesta con fees reales de Opinion.trade.
        
        Args:
            probability: Probabilidad estimada de que ocurra el evento (0-1)
            market_price: Precio actual del mercado (0-1). Si None, usa probability como proxy
            bet_size: Tamaño de la apuesta en USD
        
        Returns:
            Dictionary con 'gross_ev' y 'net_ev' (valores absolutos en USD)
        """
        # Si no hay market_price, usar probability como fallback
        if market_price is None:
            market_price = probability
        
        # En mercados binarios: payout = 1 si gana, 0 si pierde
        # Costo de entrada = market_price (lo que pagas por el token)
        # Expected payout = probability * 1 = probability
        # Gross EV = (expected_payout - cost) * bet_size
        gross_ev = (probability - market_price) * bet_size
        
        # Obtener fees cacheados de Opinion.trade
        fees_response = self.opinion_api.get_fee_rates(use_cache=True)
        if fees_response.get('success'):
            taker_fee = fees_response.get('taker_fee', 0.02)
        else:
            taker_fee = 0.02  # Fallback conservador (2%)
        
        # Fees se aplican al notional ejecutado (market_price * bet_size)
        executed_notional = market_price * bet_size
        fee_cost = executed_notional * taker_fee
        
        # Net EV = Gross EV - fees
        net_ev = gross_ev - fee_cost
        
        return {
            'gross_ev': gross_ev,
            'net_ev': net_ev,
            'fee_cost': fee_cost,
            'taker_fee_rate': taker_fee
        }
    
    def _execute_bet(self, firm_name: str, event: Dict, event_description: str,
                    bet_size: float, probability: float, prediction: Dict) -> Dict:
        """
        Ejecuta una apuesta real en Opinion.trade con manejo transaccional robusto.
        Si falla la ejecución real, registra el error y retorna status de fallo.
        """
        # Extract required fields from event
        market_id = event.get('market_id')
        yes_token_id = event.get('yes_token_id')
        no_token_id = event.get('no_token_id')
        event_id = event.get('event_id', 'unknown')
        
        # Validate required fields
        if not market_id or not yes_token_id or not no_token_id:
            error_msg = f"Missing required fields: market_id={market_id}, yes_token_id={yes_token_id}, no_token_id={no_token_id}"
            logger.error(f"{firm_name} - Bet validation failed: {error_msg}")
            return {
                'status': 'failed',
                'error': error_msg,
                'error_type': 'validation_error'
            }
        
        # Select token based on probability (>=0.5 = buy YES, <0.5 = buy NO)
        token_id = yes_token_id if probability >= 0.5 else no_token_id
        outcome_label = 'YES' if probability >= 0.5 else 'NO'
        
        # VALIDACIÓN DE PRECIO: Verificar precio actual antes de ejecutar
        price_check = self.opinion_api.get_latest_price(token_id)
        
        if price_check.get('success'):
            current_price = price_check.get('price', probability)
            expected_price = probability
            
            # Calcular diferencia porcentual
            if expected_price > 0:
                price_diff_pct = abs(current_price - expected_price) / expected_price
            else:
                price_diff_pct = 0
            
            # Rechazar si el spread es >5% (protección contra slippage excesivo)
            if price_diff_pct > 0.05:
                error_msg = f"Price validation failed: expected {expected_price:.4f}, got {current_price:.4f} (diff: {price_diff_pct:.2%})"
                logger.error(f"{firm_name} - {error_msg}")
                return {
                    'status': 'failed',
                    'error': error_msg,
                    'error_type': 'price_validation_failed',
                    'expected_price': expected_price,
                    'current_price': current_price,
                    'price_diff': price_diff_pct
                }
        else:
            # Si falla la validación de precio, usar probability como fallback pero loggear warning
            logger.warning(f"{firm_name} - Could not validate price for token {token_id}: {price_check.get('error')}")
            current_price = probability
        
        prediction_data = {
            'market_id': market_id,
            'token_id': token_id,
            'probability': probability,
            'amount': bet_size,
            'side': 'BUY',
            'metadata': {
                'firm_name': firm_name,
                'reasoning': prediction.get('analisis_sintesis', ''),
                'risk_posture': prediction.get('postura_riesgo', 'NEUTRAL'),
                'outcome': outcome_label,
                'validated_price': current_price
            }
        }
        
        try:
            result = self.opinion_api.submit_prediction(prediction_data)
            
            if result.get('success'):
                logger.log_bet_execution(firm_name, event_id, bet_size, event_description, True)
                return {'status': 'success', **result}
            else:
                error_msg = result.get('error', 'Unknown error from Opinion.trade')
                logger.log_bet_execution(firm_name, event_id, bet_size, event_description, False, error_msg)
                return {
                    'status': 'failed',
                    'error': error_msg,
                    'error_type': 'opinion_trade_rejection'
                }
        
        except Exception as e:
            error_msg = f"Exception during bet execution: {str(e)}"
            logger.log_bet_execution(firm_name, event_id, bet_size, event_description, False, error_msg)
            return {
                'status': 'failed',
                'error': error_msg,
                'error_type': 'execution_exception'
            }
    
    def get_competition_status(self) -> Dict:
        """
        Obtiene el estado actual de la competencia para todas las IAs.
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'simulation_mode': 0,
            'daily_cycles_completed': self.daily_analysis_count,
            'firms': {}
        }
        
        for firm_name in self.orchestrator.get_all_firms().keys():
            tier_status = self.risk_guard.get_tier_status(firm_name)
            bankroll_manager = self.bankroll_managers[firm_name]
            
            firm_status = {
                'tier': tier_status,
                'bankroll': bankroll_manager.get_statistics(),
                'ranking_score': self._calculate_ranking_score(bankroll_manager)
            }
            
            status['firms'][firm_name] = firm_status
        
        status['leaderboard'] = self._generate_leaderboard()
        
        return status
    
    def _calculate_ranking_score(self, bankroll_manager: BankrollManager) -> float:
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
            tier_status = self.risk_guard.get_tier_status(firm_name)
            bankroll_manager = self.bankroll_managers[firm_name]
            
            stats = bankroll_manager.get_statistics()
            
            leaderboard.append({
                'firm_name': firm_name,
                'current_bankroll': stats['current_bankroll'],
                'total_profit': stats['total_profit'],
                'return_pct': stats['total_return_pct'],
                'win_rate': stats['win_rate'],
                'total_bets': stats['total_bets'],
                'risk_tier': tier_status.get('current_tier', 'conservative'),
                'ranking_score': self._calculate_ranking_score(bankroll_manager)
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
            
            # Reconciliación usando get_my_trades()
            try:
                # Obtener trades recientes del usuario
                trades_response = self.opinion_api.get_my_trades(limit=100, market_id=None)
                
                if not trades_response.get('success'):
                    stats['errors'] += 1
                    stats['by_firm'][firm_name]['errors'] += 1
                    self.execution_log.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'reconciliation_api_error',
                        'firm_name': firm_name,
                        'bet_id': bet_id,
                        'error': trades_response.get('error', 'Unknown API error')
                    })
                    continue
                
                trades = trades_response.get('trades', [])
                
                # Buscar trade que coincida con opinion_trade_id
                matching_trade = None
                for trade in trades:
                    if trade.get('id') == opinion_trade_id or trade.get('order_id') == opinion_trade_id:
                        matching_trade = trade
                        break
                
                # Si encontramos el trade, verificar si está resuelto
                if matching_trade:
                    trade_status = matching_trade.get('status', 'unknown')
                    
                    # Si el trade está resuelto/settled
                    if trade_status in ['settled', 'completed', 'resolved']:
                        # Calcular profit/loss basado en el trade
                        # En mercados binarios: ganancia = (payout - costo) o pérdida = -costo
                        filled_amount = matching_trade.get('filled_amount', 0)
                        average_price = matching_trade.get('average_price', 0)
                        side = matching_trade.get('side', 'BUY')
                        
                        # Determinar resultado (1 = ganó, 0 = perdió)
                        # Esto es simplificado - en producción necesitaríamos verificar el outcome del mercado
                        actual_result = 1 if matching_trade.get('profit_loss', 0) > 0 else 0
                        profit_loss = matching_trade.get('profit_loss', 0)
                        
                        # Actualizar en la base de datos
                        self.db.update_autonomous_bet_result(
                            bet_id=bet_id,
                            actual_result=actual_result,
                            profit_loss=profit_loss
                        )
                        
                        # Actualizar bankroll manager
                        if firm_name in self.bankroll_managers:
                            bankroll_manager = self.bankroll_managers[firm_name]
                            bankroll_manager.record_result(
                                bet_id=bet_id,
                                won=(actual_result == 1),
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
                            'outcome': 'won' if actual_result == 1 else 'lost',
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
    
    def apply_risk_adaptation(self, firm_name: str, adaptation_level=None):
        """
        Aplica adaptación de riesgo delegando a TierRiskGuard.
        Enriquece con learning insights del LearningSystem.
        """
        learning_analysis = self.learning_system.analyze_weekly_performance(firm_name)
        
        learning_insights = None
        if learning_analysis.get('status') not in ['insufficient_data', 'no_recent_activity']:
            learning_insights = {
                'successful_patterns': learning_analysis.get('category_performance', {})
            }
        
        adaptation_details = self.risk_guard.update_tier_if_needed(firm_name, learning_insights)
        
        if adaptation_details:
            print(f"[TIER CHANGE] {firm_name}: {adaptation_details.get('description')}")
        
        return adaptation_details
