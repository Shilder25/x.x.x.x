from typing import Dict, Optional, Tuple
from enum import Enum
import math

class BettingStrategy(Enum):
    KELLY_CONSERVATIVE = "kelly_conservative"
    FIXED_FRACTIONAL = "fixed_fractional"
    PROPORTIONAL = "proportional"
    MARTINGALE_MODIFIED = "martingale_modified"
    ANTI_MARTINGALE = "anti_martingale"

class BankrollManager:
    """
    Gestor de bankroll con múltiples estrategias de betting.
    Cada IA puede usar una estrategia diferente.
    """
    
    def __init__(self, firm_name: str, strategy: BettingStrategy, initial_bankroll: float):
        self.firm_name = firm_name
        self.strategy = strategy
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        
        self.min_bet_size = 5.0
        self.max_bet_size_pct = 0.02
        
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.last_bet_size = 0
        
        self.total_bets = 0
        self.winning_bets = 0
        self.total_profit = 0
        
        self.bet_history = []
    
    def calculate_bet_size(self, probability: float, confidence: int, 
                          expected_value: float) -> Dict:
        """
        Calcula el tamaño de apuesta óptimo según la estrategia configurada.
        
        Args:
            probability: Probabilidad estimada de ganar (0-1)
            confidence: Nivel de confianza (0-100)
            expected_value: Valor esperado de la apuesta
        
        Returns:
            Dictionary con tamaño de apuesta y detalles
        """
        if self.strategy == BettingStrategy.KELLY_CONSERVATIVE:
            return self._kelly_conservative(probability, confidence, expected_value)
        
        elif self.strategy == BettingStrategy.FIXED_FRACTIONAL:
            return self._fixed_fractional(probability, confidence)
        
        elif self.strategy == BettingStrategy.PROPORTIONAL:
            return self._proportional_betting(probability, confidence)
        
        elif self.strategy == BettingStrategy.MARTINGALE_MODIFIED:
            return self._martingale_modified(probability, confidence)
        
        elif self.strategy == BettingStrategy.ANTI_MARTINGALE:
            return self._anti_martingale(probability, confidence)
        
        else:
            return self._fixed_fractional(probability, confidence)
    
    def _kelly_conservative(self, probability: float, confidence: int, 
                           expected_value: float) -> Dict:
        """
        Kelly Criterion conservador con fracción de 0.25
        Fórmula: f* = (bp - q) / b donde b=odds, p=prob, q=1-p
        Usamos fracción conservadora para reducir volatilidad
        """
        if probability <= 0.5 or expected_value <= 0:
            return {
                'bet_size': 0,
                'strategy': 'kelly_conservative',
                'reason': 'Probabilidad insuficiente o EV negativo'
            }
        
        q = 1 - probability
        odds_decimal = 2.0
        
        kelly_fraction = ((odds_decimal * probability - 1) / (odds_decimal - 1))
        kelly_conservative = kelly_fraction * 0.25
        
        confidence_adjustment = confidence / 100
        kelly_adjusted = kelly_conservative * confidence_adjustment
        
        kelly_capped = min(kelly_adjusted, self.max_bet_size_pct)
        
        bet_size = self.current_bankroll * kelly_capped
        bet_size = max(self.min_bet_size, min(bet_size, self.current_bankroll * self.max_bet_size_pct))
        
        return {
            'bet_size': round(bet_size, 2),
            'bet_size_pct': round(kelly_capped * 100, 2),
            'strategy': 'kelly_conservative',
            'kelly_fraction': round(kelly_fraction, 4),
            'confidence_adj': round(confidence_adjustment, 2),
            'reason': f'Kelly conservador (25% fracción) ajustado por confianza'
        }
    
    def _fixed_fractional(self, probability: float, confidence: int) -> Dict:
        """
        Fixed Fractional: Apuesta un porcentaje fijo del bankroll
        Rango: 0.5% - 2% basado en confianza
        """
        if probability < 0.55:
            return {
                'bet_size': 0,
                'strategy': 'fixed_fractional',
                'reason': 'Probabilidad muy baja (<55%)'
            }
        
        base_fraction = 0.01
        
        if confidence >= 80:
            fraction = 0.02
        elif confidence >= 70:
            fraction = 0.015
        elif confidence >= 60:
            fraction = 0.01
        else:
            fraction = 0.005
        
        bet_size = self.current_bankroll * fraction
        bet_size = max(self.min_bet_size, min(bet_size, self.current_bankroll * self.max_bet_size_pct))
        
        return {
            'bet_size': round(bet_size, 2),
            'bet_size_pct': round(fraction * 100, 2),
            'strategy': 'fixed_fractional',
            'confidence_tier': 'high' if confidence >= 70 else 'medium' if confidence >= 60 else 'low',
            'reason': f'Fracción fija {fraction*100}% por confianza de {confidence}%'
        }
    
    def _proportional_betting(self, probability: float, confidence: int) -> Dict:
        """
        Proportional Betting: Tamaño proporcional a confianza y probabilidad
        """
        if probability < 0.60 or confidence < 60:
            return {
                'bet_size': 0,
                'strategy': 'proportional',
                'reason': 'Requisitos mínimos no cumplidos (prob>60%, conf>60%)'
            }
        
        prob_score = (probability - 0.5) * 2
        conf_score = confidence / 100
        
        combined_score = (prob_score + conf_score) / 2
        
        fraction = 0.005 + (combined_score * 0.015)
        fraction = min(fraction, self.max_bet_size_pct)
        
        bet_size = self.current_bankroll * fraction
        bet_size = max(self.min_bet_size, bet_size)
        
        return {
            'bet_size': round(bet_size, 2),
            'bet_size_pct': round(fraction * 100, 2),
            'strategy': 'proportional',
            'combined_score': round(combined_score, 2),
            'reason': f'Proporcional a prob({round(probability*100)}%) y conf({confidence}%)'
        }
    
    def _martingale_modified(self, probability: float, confidence: int) -> Dict:
        """
        Martingale Modificado: Incrementa después de pérdidas PERO con límites estrictos
        Máximo: 3 incrementos consecutivos, luego reset
        """
        if probability < 0.55:
            return {
                'bet_size': 0,
                'strategy': 'martingale_modified',
                'reason': 'Probabilidad insuficiente para Martingale'
            }
        
        base_fraction = 0.01
        
        if self.consecutive_losses > 0 and self.consecutive_losses <= 3:
            multiplier = 1.5 ** self.consecutive_losses
            fraction = base_fraction * multiplier
        else:
            fraction = base_fraction
        
        fraction = min(fraction, self.max_bet_size_pct)
        
        bet_size = self.current_bankroll * fraction
        bet_size = max(self.min_bet_size, bet_size)
        
        return {
            'bet_size': round(bet_size, 2),
            'bet_size_pct': round(fraction * 100, 2),
            'strategy': 'martingale_modified',
            'consecutive_losses': self.consecutive_losses,
            'multiplier': round(1.5 ** self.consecutive_losses, 2) if self.consecutive_losses > 0 else 1.0,
            'reason': f'Martingale modificado (pérdidas consecutivas: {self.consecutive_losses})'
        }
    
    def _anti_martingale(self, probability: float, confidence: int) -> Dict:
        """
        Anti-Martingale: Incrementa tamaño después de GANAR
        Capitaliza rachas ganadoras
        """
        if probability < 0.60:
            return {
                'bet_size': 0,
                'strategy': 'anti_martingale',
                'reason': 'Probabilidad insuficiente'
            }
        
        base_fraction = 0.01
        
        if self.consecutive_wins > 0 and self.consecutive_wins <= 3:
            multiplier = 1.3 ** self.consecutive_wins
            fraction = base_fraction * multiplier
        else:
            fraction = base_fraction
        
        fraction = min(fraction, self.max_bet_size_pct)
        
        bet_size = self.current_bankroll * fraction
        bet_size = max(self.min_bet_size, bet_size)
        
        return {
            'bet_size': round(bet_size, 2),
            'bet_size_pct': round(fraction * 100, 2),
            'strategy': 'anti_martingale',
            'consecutive_wins': self.consecutive_wins,
            'multiplier': round(1.3 ** self.consecutive_wins, 2) if self.consecutive_wins > 0 else 1.0,
            'reason': f'Anti-Martingale (ganancias consecutivas: {self.consecutive_wins})'
        }
    
    def record_bet(self, bet_size: float, probability: float, event_id: str, 
                   event_description: str) -> Dict:
        """
        Registra una nueva apuesta y REDUCE el bankroll inmediatamente.
        El bankroll se ajustará cuando se registre el resultado (ganancia o pérdida).
        """
        if bet_size > self.current_bankroll:
            return {
                'success': False,
                'error': 'Bet size exceeds current bankroll'
            }
        
        bet_record = {
            'bet_id': f"{self.firm_name}_{self.total_bets + 1}",
            'event_id': event_id,
            'event_description': event_description,
            'bet_size': bet_size,
            'probability': probability,
            'bankroll_before': self.current_bankroll,
            'timestamp': None,
            'result': None,
            'profit_loss': None
        }
        
        # REDUCIR bankroll inmediatamente al colocar la apuesta
        self.current_bankroll -= bet_size
        
        self.bet_history.append(bet_record)
        self.last_bet_size = bet_size
        self.total_bets += 1
        
        return {
            'success': True,
            'bet_id': bet_record['bet_id'],
            'bet_record': bet_record,
            'new_bankroll': self.current_bankroll
        }
    
    def rollback_last_bet(self):
        """
        Revierte la última apuesta registrada (usado si persistence falla).
        Restaura bankroll y elimina el último registro.
        """
        if not self.bet_history:
            return
        
        last_bet = self.bet_history.pop()
        bet_size = last_bet.get('bet_size', 0)
        
        # Restaurar bankroll
        self.current_bankroll += bet_size
        
        # Revertir contador
        self.total_bets -= 1
        
        # Restaurar last_bet_size al valor anterior (si hay historial previo)
        if self.bet_history:
            self.last_bet_size = self.bet_history[-1].get('bet_size', 0)
        else:
            self.last_bet_size = 0
    
    def record_result(self, bet_id: str, won: bool, profit_loss: float) -> Dict:
        """
        Registra el resultado de una apuesta y actualiza el bankroll.
        Nota: profit_loss debe incluir la devolución de la apuesta original + ganancia/pérdida.
        Por ejemplo: Si aposté $100 y gané $180 total, profit_loss = +$180
        Si aposté $100 y perdí, profit_loss = $0 (ya se dedujo en record_bet)
        """
        bet = next((b for b in self.bet_history if b.get('bet_id') == bet_id), None)
        
        if not bet:
            return {
                'success': False,
                'error': f'Bet ID {bet_id} not found'
            }
        
        bet['result'] = won
        bet['profit_loss'] = profit_loss
        
        # Agregar el retorno de la apuesta (bet_size ya fue deducido en record_bet)
        # profit_loss incluye tanto la devolución de la apuesta como la ganancia neta
        self.current_bankroll += profit_loss
        
        # Para total_profit, calcular la ganancia neta (excluyendo la devolución)
        bet_size = bet.get('bet_size', 0)
        net_profit = profit_loss - bet_size if won else -bet_size
        self.total_profit += net_profit
        
        if won:
            self.winning_bets += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_wins = 0
            self.consecutive_losses += 1
        
        return {
            'success': True,
            'new_bankroll': self.current_bankroll,
            'total_profit': self.total_profit,
            'win_rate': self.winning_bets / self.total_bets if self.total_bets > 0 else 0
        }
    
    def get_statistics(self) -> Dict:
        """
        Retorna estadísticas completas del bankroll.
        """
        total_return_pct = ((self.current_bankroll - self.initial_bankroll) / self.initial_bankroll) * 100
        win_rate = (self.winning_bets / self.total_bets * 100) if self.total_bets > 0 else 0
        
        return {
            'firm_name': self.firm_name,
            'strategy': self.strategy.value,
            'initial_bankroll': self.initial_bankroll,
            'current_bankroll': self.current_bankroll,
            'total_profit': self.total_profit,
            'total_return_pct': round(total_return_pct, 2),
            'total_bets': self.total_bets,
            'winning_bets': self.winning_bets,
            'losing_bets': self.total_bets - self.winning_bets,
            'win_rate': round(win_rate, 2),
            'consecutive_wins': self.consecutive_wins,
            'consecutive_losses': self.consecutive_losses,
            'avg_bet_size': sum(b['bet_size'] for b in self.bet_history) / len(self.bet_history) if self.bet_history else 0,
            'largest_win': max((b.get('profit_loss', 0) for b in self.bet_history if b.get('result')), default=0),
            'largest_loss': min((b.get('profit_loss', 0) for b in self.bet_history if b.get('result') is False), default=0)
        }
    
    def should_bet(self, probability: float, confidence: int, expected_value: float) -> Tuple[bool, str]:
        """
        Determina si se debe realizar una apuesta basado en criterios mínimos.
        
        Returns:
            Tuple (should_bet: bool, reason: str)
        """
        if self.current_bankroll < self.min_bet_size:
            return False, "Bankroll insuficiente para apuesta mínima"
        
        if expected_value <= 0:
            return False, "Valor esperado negativo o cero"
        
        if probability < 0.55:
            return False, "Probabilidad demasiado baja (<55%)"
        
        if confidence < 50:
            return False, "Nivel de confianza insuficiente (<50%)"
        
        return True, "Criterios mínimos cumplidos"


def assign_strategy_to_firm(firm_name: str) -> BettingStrategy:
    """
    Asigna una estrategia de betting única a cada firma de IA.
    Esto crea diversidad en el enfoque de cada competidor.
    """
    strategy_map = {
        'ChatGPT': BettingStrategy.KELLY_CONSERVATIVE,
        'Gemini': BettingStrategy.MARTINGALE_MODIFIED,
        'Qwen': BettingStrategy.FIXED_FRACTIONAL,
        'Deepseek': BettingStrategy.PROPORTIONAL,
        'Grok': BettingStrategy.ANTI_MARTINGALE
    }
    
    return strategy_map.get(firm_name, BettingStrategy.FIXED_FRACTIONAL)
