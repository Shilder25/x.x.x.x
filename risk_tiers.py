"""
Risk Tier Management System
============================
Implements a 4-tier adaptive risk management system that adjusts betting behavior
based on current portfolio performance. Designed to stretch bankroll over 1-2 months
with automatic circuit breakers at -30%, -40%, and -60% drawdowns.

Risk Tiers:
- CONSERVATIVE: Balance ≥ 90% (healthy operation)
- DEFENSIVE: Balance 70-89% (reduce risk)
- RECOVERY: Balance 50-69% (major strategy change at -30%)
- EMERGENCY: Balance < 50% (automatic pause at -40%)
"""

from enum import Enum
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import os

class RiskTier(Enum):
    CONSERVATIVE = "conservative"
    DEFENSIVE = "defensive"
    RECOVERY = "recovery"
    EMERGENCY = "emergency"
    SUSPENDED = "suspended"

class RiskTierConfig:
    """Configuration for each risk tier"""
    
    def __init__(self):
        self.mode = os.environ.get("BANKROLL_MODE", "test")
        self.initial_balance = 50.0 if self.mode == "test" else 1000.0  # Changed from 10.0 to 50.0 to match actual TEST mode balance
        
        # Tier thresholds (as percentage of initial balance)
        self.CONSERVATIVE_THRESHOLD = 0.90  # >= 90%
        self.DEFENSIVE_THRESHOLD = 0.70     # 70-89%
        self.RECOVERY_THRESHOLD = 0.50      # 50-69%
        self.SUSPENSION_THRESHOLD = 0.40    # < 40%
        
        # Per-tier configurations
        self.configs = {
            RiskTier.CONSERVATIVE: {
                'max_bet_percent': 0.05,  # 5% of current balance
                'max_bet_fixed': 2.50 if self.mode == "test" else 50.0,  # Updated for $50 bankroll
                'daily_loss_cap_percent': 0.10,  # 10% of balance
                'daily_loss_cap_fixed': 5.00 if self.mode == "test" else 100.0,  # Updated for $50 bankroll
                'max_concurrent_positions': 2,
                'max_exposure_percent': 0.15,  # Total locked in bets
                'review_frequency': 'weekly',
                'description': 'Healthy operation - Cautious, long-term value seeking'
            },
            RiskTier.DEFENSIVE: {
                'max_bet_percent': 0.03,  # 3% of current balance
                'max_bet_fixed': 1.50 if self.mode == "test" else 30.0,  # Updated for $50 bankroll
                'daily_loss_cap_percent': 0.07,
                'daily_loss_cap_fixed': 3.50 if self.mode == "test" else 70.0,  # Updated for $50 bankroll
                'max_concurrent_positions': 1,
                'max_exposure_percent': 0.10,
                'review_frequency': 'daily',
                'description': 'Risk reduction - Focus on win rate over volume'
            },
            RiskTier.RECOVERY: {
                'max_bet_percent': 0.015,  # 1.5% of current balance
                'max_bet_fixed': 0.75 if self.mode == "test" else 25.0,  # Updated for $50 bankroll
                'daily_loss_cap_percent': 0.05,
                'daily_loss_cap_fixed': 2.50 if self.mode == "test" else 50.0,  # Updated for $50 bankroll
                'max_concurrent_positions': 1,
                'max_exposure_percent': 0.05,
                'review_frequency': 'per_bet',
                'requires_strategy_change': True,
                'description': 'Major drawdown (-30%) - Complete strategy overhaul required'
            },
            RiskTier.EMERGENCY: {
                'max_bet_percent': 0.0,  # No new bets allowed
                'max_bet_fixed': 0.0,
                'daily_loss_cap_percent': 0.0,
                'daily_loss_cap_fixed': 0.0,
                'max_concurrent_positions': 0,
                'max_exposure_percent': 0.0,
                'review_frequency': 'manual',
                'cooldown_days': 3,  # 72 hours pause
                'requires_full_reset': True,
                'description': 'Critical drawdown (-40%) - Automatic pause and full reset'
            },
            RiskTier.SUSPENDED: {
                'max_bet_percent': 0.0,
                'max_bet_fixed': 0.0,
                'daily_loss_cap_percent': 0.0,
                'daily_loss_cap_fixed': 0.0,
                'max_concurrent_positions': 0,
                'max_exposure_percent': 0.0,
                'review_frequency': 'manual',
                'description': 'Suspended (-60%) - Requires manual capital injection'
            }
        }
        
        # Global system limits (across all AIs)
        self.global_daily_loss_cap = 5.0 if self.mode == "test" else 50.0  # Already correct for TEST mode
        self.global_max_exposure = 15.0 if self.mode == "test" else 1200.0  # Increased from 12.0 to allow some trades
        self.global_min_balance = 10.0 if self.mode == "test" else 1000.0  # Keep minimum at $10 for safety

    def get_tier(self, current_balance: float, initial_balance: float) -> RiskTier:
        """Determine risk tier based on current balance"""
        if current_balance <= 0:
            return RiskTier.SUSPENDED
            
        balance_ratio = current_balance / initial_balance
        
        if balance_ratio >= self.CONSERVATIVE_THRESHOLD:
            return RiskTier.CONSERVATIVE
        elif balance_ratio >= self.DEFENSIVE_THRESHOLD:
            return RiskTier.DEFENSIVE
        elif balance_ratio >= self.RECOVERY_THRESHOLD:
            return RiskTier.RECOVERY
        elif balance_ratio >= self.SUSPENSION_THRESHOLD:
            return RiskTier.EMERGENCY
        else:
            return RiskTier.SUSPENDED

    def get_max_bet_size(self, tier: RiskTier, current_balance: float) -> float:
        """Calculate maximum bet size for current tier and balance"""
        config = self.configs[tier]
        
        # Use the MINIMUM of percentage-based and fixed cap
        percent_limit = current_balance * config['max_bet_percent']
        fixed_limit = config['max_bet_fixed']
        
        return min(percent_limit, fixed_limit)

    def get_daily_loss_cap(self, tier: RiskTier, current_balance: float) -> float:
        """Calculate daily loss limit for current tier"""
        config = self.configs[tier]
        
        percent_limit = current_balance * config['daily_loss_cap_percent']
        fixed_limit = config['daily_loss_cap_fixed']
        
        return min(percent_limit, fixed_limit)

    def get_max_exposure(self, tier: RiskTier, current_balance: float) -> float:
        """Calculate maximum total exposure (locked in active bets)"""
        config = self.configs[tier]
        return current_balance * config['max_exposure_percent']

    def get_tier_config(self, tier: RiskTier) -> Dict:
        """Get full configuration for a tier"""
        return self.configs[tier]

    def check_circuit_breaker(
        self, 
        current_balance: float, 
        initial_balance: float,
        last_cooldown_end: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str], Optional[datetime]]:
        """
        Check if circuit breaker should trigger
        
        Returns:
            (should_pause, reason, cooldown_until)
        """
        tier = self.get_tier(current_balance, initial_balance)
        balance_ratio = current_balance / initial_balance
        drawdown = (1 - balance_ratio) * 100
        
        # Check if currently in cooldown
        if last_cooldown_end and datetime.now() < last_cooldown_end:
            remaining = (last_cooldown_end - datetime.now()).total_seconds() / 3600
            return (
                True, 
                f"Still in cooldown period ({remaining:.1f} hours remaining)", 
                last_cooldown_end
            )
        
        # Emergency tier (-40% drawdown) - 72 hour pause
        if tier == RiskTier.EMERGENCY:
            cooldown_until = datetime.now() + timedelta(days=3)
            return (
                True,
                f"EMERGENCY: -{drawdown:.1f}% drawdown. Automatic 72-hour pause for full strategy reset.",
                cooldown_until
            )
        
        # Suspended tier (-60% drawdown)
        if tier == RiskTier.SUSPENDED:
            return (
                True,
                f"SUSPENDED: -{drawdown:.1f}% drawdown. Manual intervention required.",
                None  # Indefinite until manual action
            )
        
        return (False, None, None)

    def requires_strategy_adaptation(
        self, 
        current_tier: RiskTier, 
        previous_tier: Optional[RiskTier]
    ) -> Tuple[bool, str]:
        """
        Check if strategy adaptation is required due to tier change
        
        Returns:
            (requires_change, change_type)
        """
        # No previous tier (first run)
        if previous_tier is None:
            return (False, "")
        
        # Downgrade to RECOVERY tier (-30% drawdown)
        if current_tier == RiskTier.RECOVERY and previous_tier != RiskTier.RECOVERY:
            return (True, "MAJOR_ADAPTATION")
        
        # Downgrade to EMERGENCY tier (-40% drawdown)
        if current_tier == RiskTier.EMERGENCY and previous_tier != RiskTier.EMERGENCY:
            return (True, "COMPLETE_RESET")
        
        # Downgrade to SUSPENDED
        if current_tier == RiskTier.SUSPENDED:
            return (True, "SUSPENSION")
        
        # Any other tier downgrade
        if current_tier.value != previous_tier.value:
            tier_order = [RiskTier.CONSERVATIVE, RiskTier.DEFENSIVE, RiskTier.RECOVERY, RiskTier.EMERGENCY, RiskTier.SUSPENDED]
            if tier_order.index(current_tier) > tier_order.index(previous_tier):
                return (True, "MINOR_ADAPTATION")
        
        return (False, "")

# Global instance
risk_config = RiskTierConfig()
