"""
Daily Watchdog - Sistema de mantenimiento diario automático

Este script ejecuta tareas de mantenimiento diarias:
1. Reset de contadores diarios de pérdidas (TierRiskGuard)
2. Verificación de estado del sistema
3. Logging de estado diario

Diseñado para ejecutarse una vez al día (00:00 UTC o según configuración).
"""

import os
import time
from datetime import datetime
from database import TradingDatabase
from tier_risk_guard import TierRiskGuard
from risk_tiers import risk_config

class DailyWatchdog:
    """
    Sistema de vigilancia y mantenimiento diario.
    """
    
    def __init__(self):
        self.db = TradingDatabase()
        self.risk_guard = TierRiskGuard(self.db, risk_config)
        self.bankroll_mode = os.environ.get('BANKROLL_MODE', 'TEST').upper()
        
    def run_daily_maintenance(self) -> dict:
        """
        Ejecuta todas las tareas de mantenimiento diario.
        
        Returns:
            Dict con resumen de las tareas ejecutadas
        """
        timestamp = datetime.now().isoformat()
        print(f"\n{'='*60}")
        print(f"[DAILY WATCHDOG] Starting daily maintenance at {timestamp}")
        print(f"[BANKROLL MODE] {self.bankroll_mode}")
        print(f"{'='*60}\n")
        
        results = {
            'timestamp': timestamp,
            'bankroll_mode': self.bankroll_mode,
            'tasks_completed': [],
            'tasks_failed': [],
            'system_status': {}
        }
        
        # Tarea 1: Reset de contadores diarios
        try:
            self._reset_daily_counters()
            results['tasks_completed'].append('reset_daily_counters')
            print("[✓] Daily counters reset successfully")
        except Exception as e:
            results['tasks_failed'].append(f'reset_daily_counters: {str(e)}')
            print(f"[✗] Failed to reset daily counters: {e}")
        
        # Tarea 2: Verificar estado de todas las firmas
        try:
            system_status = self._check_system_status()
            results['system_status'] = system_status
            results['tasks_completed'].append('check_system_status')
            print("[✓] System status checked successfully")
        except Exception as e:
            results['tasks_failed'].append(f'check_system_status: {str(e)}')
            print(f"[✗] Failed to check system status: {e}")
        
        # Tarea 3: Logging de estado diario
        try:
            self._log_daily_summary(results)
            results['tasks_completed'].append('log_daily_summary')
            print("[✓] Daily summary logged successfully")
        except Exception as e:
            results['tasks_failed'].append(f'log_daily_summary: {str(e)}')
            print(f"[✗] Failed to log daily summary: {e}")
        
        print(f"\n{'='*60}")
        print(f"[DAILY WATCHDOG] Maintenance completed")
        print(f"Tasks completed: {len(results['tasks_completed'])}")
        print(f"Tasks failed: {len(results['tasks_failed'])}")
        print(f"{'='*60}\n")
        
        return results
    
    def _reset_daily_counters(self):
        """
        Resetea contadores diarios de pérdidas para todas las firmas.
        """
        print("[TASK] Resetting daily loss counters...")
        self.risk_guard.reset_daily_counters()
        print("  → All daily loss counters reset to 0")
    
    def _check_system_status(self) -> dict:
        """
        Verifica el estado de todas las firmas y retorna resumen.
        
        Returns:
            Dict con estado de cada firma
        """
        print("[TASK] Checking system status for all firms...")
        
        firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
        status = {}
        
        for firm_name in firms:
            tier_status = self.risk_guard.get_tier_status(firm_name)
            portfolio = self.db.get_portfolio_with_tier_info(firm_name)
            
            if portfolio:
                current_balance = portfolio.get('current_balance', 0)
                initial_balance = portfolio.get('initial_balance', 0)
                total_bets = portfolio.get('total_bets', 0)
                winning_bets = portfolio.get('winning_bets', 0)
                current_tier = portfolio.get('current_tier', 'conservative')
                daily_loss_24h = portfolio.get('daily_loss_24h', 0)
                
                pnl = current_balance - initial_balance if initial_balance > 0 else 0
                pnl_pct = (pnl / initial_balance * 100) if initial_balance > 0 else 0
                win_rate = (winning_bets / total_bets * 100) if total_bets > 0 else 0
                
                status[firm_name] = {
                    'current_balance': current_balance,
                    'initial_balance': initial_balance,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'total_bets': total_bets,
                    'winning_bets': winning_bets,
                    'win_rate': win_rate,
                    'current_tier': current_tier,
                    'daily_loss_24h': daily_loss_24h,
                    'is_healthy': pnl_pct > -30  # Saludable si pérdida < 30%
                }
                
                print(f"  → {firm_name}: ${current_balance:.2f} ({pnl_pct:+.1f}%) | {current_tier.upper()} | {total_bets} bets | {win_rate:.1f}% WR")
            else:
                status[firm_name] = {
                    'error': 'Portfolio not found',
                    'is_healthy': False
                }
                print(f"  → {firm_name}: Portfolio not found")
        
        return status
    
    def _log_daily_summary(self, results: dict):
        """
        Guarda un resumen diario en archivo de log.
        """
        print("[TASK] Logging daily summary...")
        
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"daily_watchdog_{date_str}.log")
        
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"DAILY MAINTENANCE REPORT - {results['timestamp']}\n")
            f.write(f"{'='*80}\n\n")
            
            f.write(f"Bankroll Mode: {results['bankroll_mode']}\n\n")
            
            f.write("Tasks Completed:\n")
            for task in results['tasks_completed']:
                f.write(f"  ✓ {task}\n")
            
            if results['tasks_failed']:
                f.write("\nTasks Failed:\n")
                for task in results['tasks_failed']:
                    f.write(f"  ✗ {task}\n")
            
            f.write("\nSystem Status:\n")
            for firm_name, status_data in results['system_status'].items():
                if 'error' in status_data:
                    f.write(f"  {firm_name}: ERROR - {status_data['error']}\n")
                else:
                    health_icon = "✓" if status_data['is_healthy'] else "⚠"
                    f.write(f"  {health_icon} {firm_name}: ${status_data['current_balance']:.2f} "
                           f"({status_data['pnl_pct']:+.1f}%) | {status_data['current_tier'].upper()} | "
                           f"{status_data['total_bets']} bets | {status_data['win_rate']:.1f}% WR\n")
            
            f.write(f"\n{'='*80}\n")
        
        print(f"  → Summary written to {log_file}")

def run_continuous_watchdog(interval_hours: int = 24):
    """
    Ejecuta el watchdog continuamente cada X horas.
    
    Args:
        interval_hours: Intervalo en horas entre ejecuciones (default: 24)
    """
    watchdog = DailyWatchdog()
    
    while True:
        try:
            watchdog.run_daily_maintenance()
        except Exception as e:
            print(f"[ERROR] Watchdog execution failed: {e}")
        
        # Esperar hasta la próxima ejecución
        sleep_seconds = interval_hours * 3600
        print(f"\n[WATCHDOG] Sleeping for {interval_hours} hours until next run...\n")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    print("[DAILY WATCHDOG] Starting in continuous mode (24h interval)...")
    run_continuous_watchdog(interval_hours=24)
