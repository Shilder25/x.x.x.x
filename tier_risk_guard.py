"""
Tier-Based Risk Guard System
============================
Integrates the 4-tier risk management system with the database and
provides high-level orchestration for bet approval and strategy adaptation.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
from risk_tiers import RiskTier, RiskTierConfig, risk_config
from database import TradingDatabase

class TierRiskGuard:
    """
    High-level orchestrator for tier-based risk management.
    Integrates with database and enforces tier-based betting limits.
    """
    
    def __init__(self, db: TradingDatabase, risk_config: RiskTierConfig):
        self.db = db
        self.config = risk_config
    
    def _calculate_global_daily_loss(self) -> float:
        """Calculate total losses across all AIs today"""
        conn = self.db.db_path
        import sqlite3
        db_conn = sqlite3.connect(conn)
        cursor = db_conn.cursor()
        
        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT SUM(daily_loss_today)
            FROM virtual_portfolio
            WHERE last_reset_date = ?
        ''', (today,))
        
        result = cursor.fetchone()[0]
        db_conn.close()
        
        return result if result else 0.0
    
    def _calculate_global_exposure(self) -> float:
        """Calculate total exposure across all active positions"""
        active_positions = self.db.get_active_positions_from_db()
        return sum(p.get('bet_size', 0) for p in active_positions)
    
    def can_place_bet(
        self, 
        firm_name: str, 
        bet_amount: float,
        active_positions: Optional[list] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a bet can be placed considering all tier-based restrictions.
        
        Returns:
            (allowed, reason_if_not)
        """
        portfolio = self.db.get_portfolio_with_tier_info(firm_name)
        
        if not portfolio:
            return (False, f"Portfolio not found for {firm_name}")
        
        current_balance = portfolio['current_balance']
        initial_balance = portfolio['initial_balance']
        current_tier_str = portfolio['current_tier']
        cooldown_end_str = portfolio['cooldown_end']
        daily_loss_today = portfolio['daily_loss_today']
        
        current_tier = RiskTier(current_tier_str) if current_tier_str else RiskTier.CONSERVATIVE
        
        cooldown_end = None
        if cooldown_end_str:
            try:
                cooldown_end = datetime.fromisoformat(cooldown_end_str)
            except:
                pass
        
        should_pause, pause_reason, new_cooldown = self.config.check_circuit_breaker(
            current_balance,
            initial_balance,
            cooldown_end
        )
        
        if should_pause:
            return (False, pause_reason)
        
        max_bet = self.config.get_max_bet_size(current_tier, current_balance)
        if bet_amount > max_bet:
            return (
                False, 
                f"Bet ${bet_amount:.2f} exceeds tier {current_tier.value} limit of ${max_bet:.2f}"
            )
        
        daily_loss_cap = self.config.get_daily_loss_cap(current_tier, current_balance)
        if daily_loss_today >= daily_loss_cap:
            return (
                False,
                f"Daily loss cap of ${daily_loss_cap:.2f} reached (lost ${daily_loss_today:.2f} today)"
            )
        
        tier_config = self.config.get_tier_config(current_tier)
        max_concurrent = tier_config['max_concurrent_positions']
        
        if active_positions and len(active_positions) >= max_concurrent:
            return (
                False,
                f"Tier {current_tier.value} allows max {max_concurrent} concurrent positions"
            )
        
        current_exposure = sum(p.get('bet_size', 0) for p in (active_positions or []))
        max_exposure = self.config.get_max_exposure(current_tier, current_balance)
        
        if current_exposure + bet_amount > max_exposure:
            return (
                False,
                f"Total exposure would exceed tier limit of ${max_exposure:.2f}"
            )
        
        global_daily_loss = self._calculate_global_daily_loss()
        if global_daily_loss >= self.config.global_daily_loss_cap:
            return (
                False,
                f"Global system daily loss cap of ${self.config.global_daily_loss_cap:.2f} reached"
            )
        
        global_exposure = self._calculate_global_exposure()
        if global_exposure + bet_amount > self.config.global_max_exposure:
            return (
                False,
                f"Global system exposure limit of ${self.config.global_max_exposure:.2f} would be exceeded"
            )
        
        return (True, None)
    
    def update_tier_if_needed(self, firm_name: str, learning_insights: Optional[Dict] = None) -> Optional[Dict]:
        """
        Check if tier update is needed and apply if necessary.
        Returns adaptation details if tier changed, None otherwise.
        
        Args:
            firm_name: Name of the AI firm
            learning_insights: Optional learning insights to persist with adaptation
        """
        portfolio = self.db.get_portfolio_with_tier_info(firm_name)
        
        if not portfolio:
            return None
        
        current_balance = portfolio['current_balance']
        initial_balance = portfolio['initial_balance']
        current_tier_str = portfolio['current_tier']
        previous_tier_str = portfolio['previous_tier']
        
        current_tier = RiskTier(current_tier_str) if current_tier_str else RiskTier.CONSERVATIVE
        previous_tier = RiskTier(previous_tier_str) if previous_tier_str else None
        
        new_tier = self.config.get_tier(current_balance, initial_balance)
        
        if new_tier != current_tier:
            should_pause, pause_reason, cooldown_end = self.config.check_circuit_breaker(
                current_balance, 
                initial_balance
            )
            
            cooldown_str = cooldown_end.isoformat() if cooldown_end else None
            
            self.db.update_tier_state(
                firm_name,
                new_tier.value,
                current_tier.value,
                cooldown_str
            )
            
            requires_adaptation, adaptation_type = self.config.requires_strategy_adaptation(
                new_tier,
                current_tier
            )
            
            if requires_adaptation:
                balance_ratio = current_balance / initial_balance
                loss_percentage = (1 - balance_ratio) * 100
                
                adaptation_data = {
                    'firm_name': firm_name,
                    'level': new_tier.value,
                    'description': f"Tier change: {current_tier.value} → {new_tier.value} ({adaptation_type})",
                    'previous_params': {
                        'tier': current_tier.value,
                        'balance': current_balance,
                        'balance_ratio': balance_ratio
                    },
                    'new_params': {
                        'tier': new_tier.value,
                        'max_bet': self.config.get_max_bet_size(new_tier, current_balance),
                        'daily_loss_cap': self.config.get_daily_loss_cap(new_tier, current_balance),
                        'max_exposure': self.config.get_max_exposure(new_tier, current_balance)
                    },
                    'changes': [
                        f"Tier downgraded from {current_tier.value} to {new_tier.value}",
                        f"Loss percentage: -{loss_percentage:.1f}%",
                        f"Adaptation type: {adaptation_type}"
                    ],
                    'bankroll_at_adaptation': current_balance,
                    'loss_percentage': loss_percentage,
                    'timestamp': datetime.now().isoformat()
                }
                
                if learning_insights:
                    adaptation_data['learning_insights'] = learning_insights
                
                self.db.save_strategy_adaptation(adaptation_data)
                
                return adaptation_data
        
        return None
    
    def record_bet_result(self, firm_name: str, profit_loss: float, won: bool):
        """
        Record the result of a bet and update daily loss tracking.
        """
        if profit_loss < 0:
            self.db.record_daily_loss(firm_name, abs(profit_loss))
        
        self.db.update_portfolio_bet_stats(firm_name, won)
        
        self.update_tier_if_needed(firm_name)
    
    def reset_daily_counters(self):
        """
        Reset daily loss counters for all firms.
        Should be called at the start of each new day.
        """
        self.db.reset_daily_loss()
    
    def get_tier_status(self, firm_name: str) -> Dict:
        """
        Get current tier status and limits for a firm.
        """
        portfolio = self.db.get_portfolio_with_tier_info(firm_name)
        
        if not portfolio:
            return {}
        
        current_balance = portfolio['current_balance']
        initial_balance = portfolio['initial_balance']
        current_tier_str = portfolio['current_tier']
        
        current_tier = RiskTier(current_tier_str) if current_tier_str else RiskTier.CONSERVATIVE
        
        return {
            'firm_name': firm_name,
            'current_tier': current_tier.value,
            'current_balance': current_balance,
            'initial_balance': initial_balance,
            'balance_ratio': current_balance / initial_balance,
            'loss_percentage': (1 - current_balance / initial_balance) * 100,
            'max_bet': self.config.get_max_bet_size(current_tier, current_balance),
            'daily_loss_cap': self.config.get_daily_loss_cap(current_tier, current_balance),
            'daily_loss_today': portfolio['daily_loss_today'],
            'max_exposure': self.config.get_max_exposure(current_tier, current_balance),
            'tier_config': self.config.get_tier_config(current_tier)
        }
