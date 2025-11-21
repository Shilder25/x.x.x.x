from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum

class RiskLevel(Enum):
    NORMAL = "normal"
    CAUTION = "caution"
    ALERT = "alert"
    CRITICAL = "critical"

class AdaptationLevel(Enum):
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3

class RiskManager:
    """
    Sistema de gestión de riesgo multinivel con adaptación automática.
    Implementa stop-loss dinámicos, circuit breakers y sistema de aprendizaje.
    """
    
    def __init__(self, firm_name: str, initial_bankroll: float):
        self.firm_name = firm_name
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        
        self.daily_loss_limit = 0.05
        self.weekly_loss_limit = 0.10
        self.monthly_loss_limit = 0.20
        
        self.max_bet_size_pct = 0.02
        self.max_concurrent_bets = 5
        self.max_category_exposure = 0.10
        
        self.consecutive_losses = 0
        self.cooldown_until = None
        
        self.daily_losses = []
        self.weekly_losses = []
        self.monthly_losses = []
        
        self.adaptation_level = AdaptationLevel.LEVEL_0
        self.strategy_changes = []
    
    def get_risk_level(self) -> RiskLevel:
        """
        Calcula el nivel de riesgo actual basado en pérdidas acumuladas.
        """
        total_loss_pct = (self.initial_bankroll - self.current_bankroll) / self.initial_bankroll
        
        if total_loss_pct >= 0.30:
            return RiskLevel.CRITICAL
        elif total_loss_pct >= 0.20:
            return RiskLevel.ALERT
        elif total_loss_pct >= 0.10:
            return RiskLevel.CAUTION
        else:
            return RiskLevel.NORMAL
    
    def check_adaptation_needed(self) -> Optional[AdaptationLevel]:
        """
        Verifica si se necesita adaptación de estrategia basada en pérdidas.
        Retorna el nivel de adaptación necesario o None si no se requiere.
        """
        total_loss_pct = (self.initial_bankroll - self.current_bankroll) / self.initial_bankroll
        
        if total_loss_pct >= 0.30 and self.adaptation_level != AdaptationLevel.LEVEL_3:
            return AdaptationLevel.LEVEL_3
        elif total_loss_pct >= 0.20 and self.adaptation_level.value < 2:
            return AdaptationLevel.LEVEL_2
        elif total_loss_pct >= 0.10 and self.adaptation_level.value < 1:
            return AdaptationLevel.LEVEL_1
        
        return None
    
    def apply_adaptation(self, level: AdaptationLevel, analysis_data: Optional[Dict] = None) -> Dict:
        """
        Aplica adaptación de estrategia según el nivel de pérdida.
        
        Args:
            level: Nivel de adaptación a aplicar
            analysis_data: Datos de análisis de performance reciente
        
        Returns:
            Dictionary con detalles de la adaptación aplicada
        """
        self.adaptation_level = level
        
        adaptation_details = {
            'timestamp': datetime.now().isoformat(),
            'firm_name': self.firm_name,
            'level': level.value,
            'previous_params': self._get_current_params(),
            'changes': []
        }
        
        if level == AdaptationLevel.LEVEL_1:
            adaptation_details['changes'] = self._apply_level_1_adaptation()
            adaptation_details['description'] = "Ajuste Táctico: Reducción moderada de riesgo"
        
        elif level == AdaptationLevel.LEVEL_2:
            adaptation_details['changes'] = self._apply_level_2_adaptation()
            adaptation_details['description'] = "Cambio de Estrategia: Enfoque conservador"
        
        elif level == AdaptationLevel.LEVEL_3:
            adaptation_details['changes'] = self._apply_level_3_adaptation(analysis_data)
            adaptation_details['description'] = "Reinvención Total: Ultra conservador + aprendizaje"
        
        adaptation_details['new_params'] = self._get_current_params()
        self.strategy_changes.append(adaptation_details)
        
        return adaptation_details
    
    def _apply_level_1_adaptation(self) -> List[str]:
        """
        Nivel 1: -10% pérdida → Ajuste Táctico
        - Reducir tamaño de apuesta a 1.5%
        - Incrementar umbral de confianza mínima
        """
        changes = []
        
        if self.max_bet_size_pct > 0.015:
            self.max_bet_size_pct = 0.015
            changes.append("Tamaño máximo de apuesta reducido a 1.5%")
        
        if self.max_concurrent_bets > 3:
            self.max_concurrent_bets = 3
            changes.append("Apuestas concurrentes limitadas a 3")
        
        changes.append("Incrementado umbral de confianza mínima a 65%")
        
        return changes
    
    def _apply_level_2_adaptation(self) -> List[str]:
        """
        Nivel 2: -20% pérdida → Cambio de Estrategia
        - Cambiar a Fixed Fractional conservador
        - Aumentar diversificación
        """
        changes = []
        
        self.max_bet_size_pct = 0.01
        changes.append("Tamaño máximo de apuesta reducido a 1%")
        
        self.max_concurrent_bets = 5
        self.max_category_exposure = 0.05
        changes.append("Diversificación aumentada: máx 5% por categoría")
        
        changes.append("Cambio a estrategia Fixed Fractional conservadora")
        changes.append("Solo eventos con alta liquidez")
        
        return changes
    
    def _apply_level_3_adaptation(self, analysis_data: Optional[Dict]) -> List[str]:
        """
        Nivel 3: -30% pérdida → Reinvención Total
        - Ultra conservador: 0.5% por apuesta
        - Solo apuestas con EV > 15%
        - Aprender de IAs ganadoras
        """
        changes = []
        
        self.max_bet_size_pct = 0.005
        changes.append("Modo ultra-conservador: 0.5% por apuesta")
        
        self.max_concurrent_bets = 3
        changes.append("Máximo 3 posiciones concurrentes")
        
        changes.append("Solo apuestas con EV > 15%")
        changes.append("Analizar y adoptar estrategias de IAs ganadoras")
        
        if analysis_data and 'successful_patterns' in analysis_data:
            patterns = analysis_data['successful_patterns']
            changes.append(f"Adoptando patrones exitosos: {', '.join(patterns)}")
        
        return changes
    
    def _get_current_params(self) -> Dict:
        """Retorna parámetros actuales de configuración."""
        return {
            'max_bet_size_pct': self.max_bet_size_pct,
            'max_concurrent_bets': self.max_concurrent_bets,
            'max_category_exposure': self.max_category_exposure,
            'adaptation_level': self.adaptation_level.value
        }
    
    def can_place_bet(self, bet_amount: float, category: Optional[str] = None, 
                     current_positions: Optional[List[Dict]] = None) -> Dict:
        """
        Verifica si se puede colocar una apuesta basado en límites de riesgo.
        
        Args:
            bet_amount: Monto de la apuesta propuesta
            category: Categoría del evento (opcional)
            current_positions: Lista de posiciones activas actuales
        
        Returns:
            Dictionary con resultado de la verificación
        """
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return {
                'allowed': False,
                'reason': f"En cooldown hasta {self.cooldown_until.strftime('%Y-%m-%d %H:%M')}",
                'cooldown_remaining_hours': (self.cooldown_until - datetime.now()).total_seconds() / 3600
            }
        
        if bet_amount > self.current_bankroll * self.max_bet_size_pct:
            return {
                'allowed': False,
                'reason': f"Apuesta excede límite de {self.max_bet_size_pct*100}% del bankroll",
                'max_allowed': self.current_bankroll * self.max_bet_size_pct
            }
        
        if current_positions and len(current_positions) >= self.max_concurrent_bets:
            return {
                'allowed': False,
                'reason': f"Límite de {self.max_concurrent_bets} apuestas concurrentes alcanzado"
            }
        
        if category and current_positions:
            category_exposure = sum(
                p.get('amount', 0) for p in current_positions 
                if p.get('category') == category
            )
            if category_exposure + bet_amount > self.current_bankroll * self.max_category_exposure:
                return {
                    'allowed': False,
                    'reason': f"Exposición en categoría {category} excede {self.max_category_exposure*100}%"
                }
        
        daily_loss = self._calculate_daily_loss()
        if daily_loss > self.initial_bankroll * self.daily_loss_limit:
            self._activate_cooldown(24)
            return {
                'allowed': False,
                'reason': f"Stop-loss diario activado ({self.daily_loss_limit*100}%)",
                'cooldown_hours': 24
            }
        
        return {
            'allowed': True,
            'message': 'Apuesta autorizada',
            'risk_level': self.get_risk_level().value
        }
    
    def record_bet_result(self, bet_amount: float, profit_loss: float, won: bool):
        """
        Registra el resultado de una apuesta y actualiza contadores.
        """
        self.current_bankroll += profit_loss
        
        if not won:
            self.consecutive_losses += 1
            
            self.daily_losses.append({
                'amount': abs(profit_loss),
                'timestamp': datetime.now()
            })
            
            if self.consecutive_losses >= 3:
                self._activate_cooldown(24)
        else:
            self.consecutive_losses = 0
        
        adaptation_needed = self.check_adaptation_needed()
        if adaptation_needed:
            return self.apply_adaptation(adaptation_needed)
        
        return None
    
    def _calculate_daily_loss(self) -> float:
        """Calcula pérdidas acumuladas en las últimas 24 horas."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_losses = [
            loss['amount'] for loss in self.daily_losses 
            if loss['timestamp'] > cutoff_time
        ]
        return sum(recent_losses)
    
    def _activate_cooldown(self, hours: int):
        """Activa período de cooldown."""
        self.cooldown_until = datetime.now() + timedelta(hours=hours)
    
    def get_recommended_bet_size(self, probability: float, kelly_fraction: float = 0.25) -> float:
        """
        Calcula tamaño de apuesta recomendado usando Kelly Criterion ajustado.
        
        Args:
            probability: Probabilidad estimada de ganar (0-1)
            kelly_fraction: Fracción de Kelly a usar (default 0.25 = conservador)
        
        Returns:
            Tamaño de apuesta recomendado en valor absoluto
        """
        # Opinion.trade minimum bet requirement (1.30 USDT minimum, we use 1.50 for safety)
        MINIMUM_BET_USDT = 1.5
        
        if probability <= 0.5:
            return 0
        
        odds_decimal = 1 / probability
        
        kelly_pct = ((odds_decimal * probability - 1) / (odds_decimal - 1)) * kelly_fraction
        kelly_pct = max(0, min(kelly_pct, self.max_bet_size_pct))
        
        recommended_amount = self.current_bankroll * kelly_pct
        
        # Ensure minimum bet size if recommendation is above 0
        # If below minimum, return 0 (don't bet) to avoid wasting fees on tiny bets
        if 0 < recommended_amount < MINIMUM_BET_USDT:
            return 0
        
        return recommended_amount
    
    def get_status_report(self) -> Dict:
        """
        Genera reporte del estado actual del sistema de riesgo.
        """
        total_loss_pct = (self.initial_bankroll - self.current_bankroll) / self.initial_bankroll
        
        return {
            'firm_name': self.firm_name,
            'initial_bankroll': self.initial_bankroll,
            'current_bankroll': self.current_bankroll,
            'total_loss_pct': total_loss_pct * 100,
            'risk_level': self.get_risk_level().value,
            'adaptation_level': self.adaptation_level.value,
            'consecutive_losses': self.consecutive_losses,
            'in_cooldown': self.cooldown_until is not None and datetime.now() < self.cooldown_until,
            'cooldown_until': self.cooldown_until.isoformat() if self.cooldown_until else None,
            'current_limits': self._get_current_params(),
            'recent_adaptations': self.strategy_changes[-3:] if self.strategy_changes else []
        }
