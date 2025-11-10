"""
Reconciliation System - Verificación de consistencia entre estado local y Opinion.trade

Este módulo detecta y reporta discrepancias entre:
1. Balances virtuales (tracking local en DB)
2. Balances reales (Opinion.trade API)
3. Apuestas ejecutadas pero no persistidas

Usado para auditoría y detección de inconsistencias.
"""

from typing import Dict, List
from datetime import datetime
from database import TradingDatabase
from opinion_trade_api import OpinionTradeAPI

class ReconciliationEngine:
    """
    Motor de reconciliación entre estado local y Opinion.trade.
    """
    
    def __init__(self, database: TradingDatabase):
        self.db = database
        self.opinion_api = OpinionTradeAPI()
    
    def run_full_reconciliation(self) -> Dict:
        """
        Ejecuta reconciliación completa para todas las firmas.
        
        Returns:
            Dict con resultados de reconciliación
        """
        timestamp = datetime.now().isoformat()
        print(f"\n{'='*60}")
        print(f"[RECONCILIATION] Starting full reconciliation at {timestamp}")
        print(f"{'='*60}\n")
        
        results = {
            'timestamp': timestamp,
            'firms': {},
            'total_discrepancies': 0,
            'critical_discrepancies': [],
            'warnings': []
        }
        
        firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
        
        for firm_name in firms:
            firm_result = self._reconcile_firm(firm_name)
            results['firms'][firm_name] = firm_result
            
            if firm_result.get('has_discrepancy'):
                results['total_discrepancies'] += 1
                
                # Discrepancia crítica: diferencia > $5 o > 10%
                balance_diff = abs(firm_result.get('balance_difference', 0))
                if balance_diff > 5 or firm_result.get('balance_diff_pct', 0) > 10:
                    results['critical_discrepancies'].append({
                        'firm': firm_name,
                        'type': 'balance_mismatch',
                        'amount': balance_diff,
                        'details': firm_result
                    })
        
        print(f"\n{'='*60}")
        print(f"[RECONCILIATION] Completed")
        print(f"Total discrepancies: {results['total_discrepancies']}")
        print(f"Critical discrepancies: {len(results['critical_discrepancies'])}")
        print(f"{'='*60}\n")
        
        return results
    
    def _reconcile_firm(self, firm_name: str) -> Dict:
        """
        Reconcilia estado de una firma específica.
        
        Args:
            firm_name: Nombre de la firma a reconciliar
            
        Returns:
            Dict con resultados de reconciliación
        """
        print(f"[RECONCILING] {firm_name}...")
        
        result = {
            'firm_name': firm_name,
            'local_balance': 0,
            'real_balance': 0,
            'balance_difference': 0,
            'balance_diff_pct': 0,
            'has_discrepancy': False,
            'discrepancy_type': None,
            'local_active_bets': 0,
            'real_active_bets': 0,
            'recommendations': []
        }
        
        # 1. Obtener balance local (virtual)
        portfolio = self.db.get_portfolio_with_tier_info(firm_name)
        if portfolio:
            local_balance = portfolio.get('current_balance', 0)
            result['local_balance'] = local_balance
        else:
            result['recommendations'].append("Portfolio not found in database - initialize first")
            return result
        
        # 2. Obtener balance real de Opinion.trade
        try:
            balance_response = self.opinion_api.get_balance()
            if balance_response.get('success'):
                real_balance = balance_response.get('balance', 0)
                result['real_balance'] = real_balance
            else:
                result['recommendations'].append(f"Failed to fetch real balance: {balance_response.get('error')}")
                return result
        except Exception as e:
            result['recommendations'].append(f"Exception fetching real balance: {str(e)}")
            return result
        
        # 3. Comparar balances
        balance_diff = real_balance - local_balance
        result['balance_difference'] = balance_diff
        
        if local_balance > 0:
            balance_diff_pct = abs(balance_diff / local_balance * 100)
            result['balance_diff_pct'] = balance_diff_pct
        
        # 4. Detectar discrepancias
        if abs(balance_diff) > 0.01:  # Tolerancia: $0.01
            result['has_discrepancy'] = True
            
            if balance_diff > 0:
                result['discrepancy_type'] = 'real_higher'
                result['recommendations'].append(
                    f"Real balance (${real_balance:.2f}) is ${balance_diff:.2f} higher than local (${local_balance:.2f}). "
                    "Possible causes: manual deposits, unreported wins, or local tracking errors."
                )
            else:
                result['discrepancy_type'] = 'local_higher'
                result['recommendations'].append(
                    f"Local balance (${local_balance:.2f}) is ${abs(balance_diff):.2f} higher than real (${real_balance:.2f}). "
                    "Possible causes: executed bets not persisted locally, unreported losses, or sync errors."
                )
        
        # 5. Contar apuestas activas (local)
        local_active_bets = self._count_local_active_bets(firm_name)
        result['local_active_bets'] = local_active_bets
        
        # 6. Contar apuestas activas (real)
        try:
            positions_response = self.opinion_api.get_active_positions()
            if positions_response.get('success'):
                positions = positions_response.get('positions', [])
                # Filtrar por firma (si el API lo soporta)
                real_active_bets = len(positions)
                result['real_active_bets'] = real_active_bets
        except Exception as e:
            result['recommendations'].append(f"Exception fetching active positions: {str(e)}")
        
        # Log resultado
        status_icon = "⚠" if result['has_discrepancy'] else "✓"
        print(f"  {status_icon} {firm_name}: Local=${local_balance:.2f} | Real=${real_balance:.2f} | Diff=${balance_diff:+.2f}")
        
        return result
    
    def _count_local_active_bets(self, firm_name: str) -> int:
        """
        Cuenta apuestas activas en base de datos local.
        
        Args:
            firm_name: Nombre de la firma
            
        Returns:
            Número de apuestas activas
        """
        # Obtener apuestas pendientes (sin resultado)
        query = """
            SELECT COUNT(*) as count
            FROM autonomous_bets
            WHERE firm_name = ?
            AND (actual_result IS NULL OR actual_result = '')
        """
        
        result = self.db.conn.execute(query, (firm_name,)).fetchone()
        return result['count'] if result else 0
    
    def generate_reconciliation_report(self, results: Dict) -> str:
        """
        Genera reporte legible de reconciliación.
        
        Args:
            results: Resultados de reconciliación
            
        Returns:
            String con reporte formateado
        """
        report_lines = []
        report_lines.append(f"\n{'='*80}")
        report_lines.append(f"RECONCILIATION REPORT - {results['timestamp']}")
        report_lines.append(f"{'='*80}\n")
        
        # Resumen global
        report_lines.append("SUMMARY:")
        report_lines.append(f"  Total firms checked: {len(results['firms'])}")
        report_lines.append(f"  Discrepancies found: {results['total_discrepancies']}")
        report_lines.append(f"  Critical discrepancies: {len(results['critical_discrepancies'])}\n")
        
        # Detalles por firma
        report_lines.append("FIRM DETAILS:")
        for firm_name, firm_data in results['firms'].items():
            status_icon = "⚠" if firm_data.get('has_discrepancy') else "✓"
            report_lines.append(f"\n  {status_icon} {firm_name}:")
            report_lines.append(f"    Local balance:  ${firm_data.get('local_balance', 0):.2f}")
            report_lines.append(f"    Real balance:   ${firm_data.get('real_balance', 0):.2f}")
            report_lines.append(f"    Difference:     ${firm_data.get('balance_difference', 0):+.2f}")
            
            if firm_data.get('has_discrepancy'):
                report_lines.append(f"    Type:           {firm_data.get('discrepancy_type', 'unknown')}")
            
            if firm_data.get('recommendations'):
                report_lines.append("    Recommendations:")
                for rec in firm_data['recommendations']:
                    report_lines.append(f"      - {rec}")
        
        # Discrepancias críticas
        if results['critical_discrepancies']:
            report_lines.append(f"\n{'='*80}")
            report_lines.append("CRITICAL DISCREPANCIES:")
            for disc in results['critical_discrepancies']:
                report_lines.append(f"\n  ⚠ {disc['firm']} - {disc['type']}")
                report_lines.append(f"    Amount: ${disc['amount']:.2f}")
                report_lines.append(f"    Details: {disc['details'].get('recommendations', [])}")
        
        report_lines.append(f"\n{'='*80}\n")
        
        return "\n".join(report_lines)
    
    def save_reconciliation_report(self, results: Dict):
        """
        Guarda reporte de reconciliación en archivo.
        
        Args:
            results: Resultados de reconciliación
        """
        import os
        
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(log_dir, f"reconciliation_{timestamp}.log")
        
        report = self.generate_reconciliation_report(results)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"[RECONCILIATION] Report saved to {report_file}")

if __name__ == "__main__":
    from database import TradingDatabase
    
    print("[RECONCILIATION] Running standalone reconciliation...")
    
    db = TradingDatabase()
    reconciler = ReconciliationEngine(db)
    
    results = reconciler.run_full_reconciliation()
    reconciler.save_reconciliation_report(results)
    
    print(reconciler.generate_reconciliation_report(results))
