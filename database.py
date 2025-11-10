import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class TradingDatabase:
    def __init__(self, db_path: str = "trading_agents.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL,
            event_description TEXT NOT NULL,
            prediction_date TEXT NOT NULL,
            probability REAL NOT NULL,
            postura_riesgo TEXT NOT NULL,
            analisis_sintesis TEXT,
            debate_bullish_bearish TEXT,
            ajuste_riesgo_justificacion TEXT,
            tokens_used INTEGER,
            estimated_cost REAL,
            actual_result INTEGER,
            profit_loss REAL,
            created_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS firm_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL,
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            total_profit REAL DEFAULT 0.0,
            total_tokens INTEGER DEFAULT 0,
            total_cost REAL DEFAULT 0.0,
            sharpe_ratio REAL DEFAULT 0.0,
            accuracy REAL DEFAULT 0.0,
            updated_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS virtual_portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL UNIQUE,
            initial_balance REAL DEFAULT 10000.0,
            current_balance REAL DEFAULT 10000.0,
            total_returns REAL DEFAULT 0.0,
            created_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS autonomous_bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL,
            event_id TEXT NOT NULL,
            event_description TEXT NOT NULL,
            category TEXT,
            bet_size REAL NOT NULL,
            probability REAL NOT NULL,
            confidence INTEGER NOT NULL,
            expected_value REAL,
            risk_level TEXT,
            adaptation_level INTEGER,
            betting_strategy TEXT,
            reasoning TEXT,
            sentiment_score REAL,
            sentiment_analysis TEXT,
            news_score REAL,
            news_analysis TEXT,
            technical_score REAL,
            technical_analysis TEXT,
            fundamental_score REAL,
            fundamental_analysis TEXT,
            volatility_score REAL,
            volatility_analysis TEXT,
            actual_result INTEGER,
            profit_loss REAL,
            execution_timestamp TEXT NOT NULL,
            resolution_timestamp TEXT,
            simulation_mode INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS autonomous_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_timestamp TEXT NOT NULL,
            total_events_analyzed INTEGER DEFAULT 0,
            total_bets_placed INTEGER DEFAULT 0,
            total_bets_skipped INTEGER DEFAULT 0,
            simulation_mode INTEGER DEFAULT 1,
            execution_summary TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategy_adaptations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL,
            adaptation_level INTEGER NOT NULL,
            trigger_reason TEXT,
            previous_params TEXT,
            new_params TEXT,
            changes_applied TEXT,
            bankroll_at_adaptation REAL,
            loss_percentage REAL,
            adaptation_timestamp TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_bet_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_date TEXT NOT NULL,
            total_bet_amount REAL DEFAULT 0.0,
            bet_count INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL,
            UNIQUE(tracking_date)
        )
        ''')
        
        self._migrate_schema(cursor)
        
        conn.commit()
        conn.close()
    
    def _migrate_schema(self, cursor):
        """
        Perform automatic schema migrations for existing databases.
        """
        cursor.execute("PRAGMA table_info(firm_performance)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'sharpe_ratio' not in columns:
            cursor.execute('''
            ALTER TABLE firm_performance ADD COLUMN sharpe_ratio REAL DEFAULT 0.0
            ''')
            print("Database migrated: Added sharpe_ratio column to firm_performance table")
        
        cursor.execute("PRAGMA table_info(autonomous_bets)")
        bet_columns = [row[1] for row in cursor.fetchall()]
        
        if 'sentiment_score' not in bet_columns:
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN sentiment_score REAL')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN sentiment_analysis TEXT')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN news_score REAL')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN news_analysis TEXT')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN technical_score REAL')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN technical_analysis TEXT')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN fundamental_score REAL')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN fundamental_analysis TEXT')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN volatility_score REAL')
            cursor.execute('ALTER TABLE autonomous_bets ADD COLUMN volatility_analysis TEXT')
            print("Database migrated: Added 5-area analysis columns to autonomous_bets table")
        
        cursor.execute("PRAGMA table_info(virtual_portfolio)")
        portfolio_columns = [row[1] for row in cursor.fetchall()]
        
        if 'current_tier' not in portfolio_columns:
            cursor.execute('ALTER TABLE virtual_portfolio ADD COLUMN current_tier TEXT DEFAULT "conservative"')
            cursor.execute('ALTER TABLE virtual_portfolio ADD COLUMN previous_tier TEXT')
            cursor.execute('ALTER TABLE virtual_portfolio ADD COLUMN cooldown_end TEXT')
            cursor.execute('ALTER TABLE virtual_portfolio ADD COLUMN daily_loss_today REAL DEFAULT 0.0')
            cursor.execute('ALTER TABLE virtual_portfolio ADD COLUMN last_reset_date TEXT')
            cursor.execute('ALTER TABLE virtual_portfolio ADD COLUMN total_bets INTEGER DEFAULT 0')
            cursor.execute('ALTER TABLE virtual_portfolio ADD COLUMN winning_bets INTEGER DEFAULT 0')
            print("Database migrated: Added risk tier tracking columns to virtual_portfolio table")
    
    def initialize_firm_portfolio(self, firm_name: str, initial_balance: float = 10000.0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO virtual_portfolio (firm_name, initial_balance, current_balance, total_returns, created_at)
            VALUES (?, ?, ?, 0.0, ?)
            ''', (firm_name, initial_balance, initial_balance, datetime.now().isoformat()))
            
            cursor.execute('''
            INSERT INTO firm_performance (firm_name, updated_at)
            VALUES (?, ?)
            ''', (firm_name, datetime.now().isoformat()))
            
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
    
    def save_prediction(self, prediction_data: Dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO predictions (
            firm_name, event_description, prediction_date, probability, postura_riesgo,
            analisis_sintesis, debate_bullish_bearish, ajuste_riesgo_justificacion,
            tokens_used, estimated_cost, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_data['firm_name'],
            prediction_data['event_description'],
            prediction_data['prediction_date'],
            prediction_data['probability'],
            prediction_data['postura_riesgo'],
            prediction_data.get('analisis_sintesis', ''),
            prediction_data.get('debate_bullish_bearish', ''),
            prediction_data.get('ajuste_riesgo_justificacion', ''),
            prediction_data.get('tokens_used', 0),
            prediction_data.get('estimated_cost', 0.0),
            datetime.now().isoformat()
        ))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.update_firm_stats(prediction_data['firm_name'])
        return prediction_id
    
    def update_prediction_result(self, prediction_id: int, actual_result: int, profit_loss: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE predictions
        SET actual_result = ?, profit_loss = ?
        WHERE id = ?
        ''', (actual_result, profit_loss, prediction_id))
        
        cursor.execute('SELECT firm_name FROM predictions WHERE id = ?', (prediction_id,))
        firm_name = cursor.fetchone()[0]
        
        cursor.execute('''
        UPDATE virtual_portfolio
        SET current_balance = current_balance + ?,
            total_returns = total_returns + ?
        WHERE firm_name = ?
        ''', (profit_loss, profit_loss, firm_name))
        
        conn.commit()
        conn.close()
        
        self.update_firm_stats(firm_name)
    
    def update_firm_stats(self, firm_name: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*), 
               SUM(CASE WHEN actual_result IS NOT NULL AND 
                   ((probability >= 0.5 AND actual_result = 1) OR (probability < 0.5 AND actual_result = 0))
                   THEN 1 ELSE 0 END),
               SUM(COALESCE(profit_loss, 0)),
               SUM(tokens_used),
               SUM(estimated_cost)
        FROM predictions
        WHERE firm_name = ?
        ''', (firm_name,))
        
        total_preds, correct_preds, total_profit, total_tokens, total_cost = cursor.fetchone()
        accuracy = (correct_preds / total_preds * 100) if total_preds > 0 else 0
        
        sharpe_ratio = self._calculate_sharpe_ratio(firm_name, cursor)
        
        cursor.execute('''
        UPDATE firm_performance
        SET total_predictions = ?,
            correct_predictions = ?,
            total_profit = ?,
            total_tokens = ?,
            total_cost = ?,
            accuracy = ?,
            sharpe_ratio = ?,
            updated_at = ?
        WHERE firm_name = ?
        ''', (total_preds, correct_preds or 0, total_profit or 0, total_tokens or 0, 
              total_cost or 0, accuracy, sharpe_ratio, datetime.now().isoformat(), firm_name))
        
        conn.commit()
        conn.close()
    
    def _calculate_sharpe_ratio(self, firm_name: str, cursor) -> float:
        """
        Calculate Sharpe Ratio: (Average Return - Risk-Free Rate) / Standard Deviation of Returns
        Risk-free rate assumed to be 0 for simplicity
        """
        cursor.execute('''
        SELECT profit_loss
        FROM predictions
        WHERE firm_name = ? AND actual_result IS NOT NULL AND profit_loss IS NOT NULL
        ORDER BY created_at
        ''', (firm_name,))
        
        returns = [row[0] for row in cursor.fetchall()]
        
        if len(returns) < 2:
            return 0.0
        
        import numpy as np
        
        mean_return = np.mean(returns)
        std_return = np.std(returns, ddof=1)
        
        if std_return == 0:
            return 0.0
        
        sharpe_ratio = mean_return / std_return
        
        return float(sharpe_ratio)
    
    def get_firm_performance(self, firm_name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT fp.firm_name, fp.total_predictions, fp.correct_predictions, fp.total_profit,
               fp.total_tokens, fp.total_cost, fp.sharpe_ratio, fp.accuracy,
               vp.current_balance, vp.initial_balance, vp.total_returns
        FROM firm_performance fp
        LEFT JOIN virtual_portfolio vp ON fp.firm_name = vp.firm_name
        WHERE fp.firm_name = ?
        ''', (firm_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'firm_name': row[0],
                'total_predictions': row[1],
                'correct_predictions': row[2],
                'total_profit': row[3],
                'total_tokens': row[4],
                'total_cost': row[5],
                'sharpe_ratio': row[6],
                'accuracy': row[7],
                'current_balance': row[8] if row[8] else 10000.0,
                'initial_balance': row[9] if row[9] else 10000.0,
                'total_returns': row[10] if row[10] else 0.0
            }
        return None
    
    def get_all_firm_performances(self) -> List[Dict]:
        firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
        performances = []
        
        for firm in firms:
            perf = self.get_firm_performance(firm)
            if perf:
                performances.append(perf)
        
        return performances
    
    def get_recent_predictions(self, firm_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if firm_name:
            cursor.execute('''
            SELECT * FROM predictions
            WHERE firm_name = ?
            ORDER BY created_at DESC
            LIMIT ?
            ''', (firm_name, limit))
        else:
            cursor.execute('''
            SELECT * FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            predictions.append({
                'id': row[0],
                'firm_name': row[1],
                'event_description': row[2],
                'prediction_date': row[3],
                'probability': row[4],
                'postura_riesgo': row[5],
                'analisis_sintesis': row[6],
                'debate_bullish_bearish': row[7],
                'ajuste_riesgo_justificacion': row[8],
                'tokens_used': row[9],
                'estimated_cost': row[10],
                'actual_result': row[11],
                'profit_loss': row[12],
                'created_at': row[13]
            })
        
        return predictions
    
    def save_autonomous_bet(self, bet_data: Dict) -> int:
        """
        Guarda una apuesta autónoma en la base de datos con análisis de 5 áreas.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO autonomous_bets (
            firm_name, event_id, event_description, category, bet_size,
            probability, confidence, expected_value, risk_level, adaptation_level,
            betting_strategy, reasoning,
            sentiment_score, sentiment_analysis,
            news_score, news_analysis,
            technical_score, technical_analysis,
            fundamental_score, fundamental_analysis,
            volatility_score, volatility_analysis,
            execution_timestamp, simulation_mode, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bet_data['firm_name'],
            bet_data['event_id'],
            bet_data['event_description'],
            bet_data.get('category'),
            bet_data['bet_size'],
            bet_data['probability'],
            bet_data['confidence'],
            bet_data.get('expected_value'),
            bet_data.get('risk_level'),
            bet_data.get('adaptation_level'),
            bet_data.get('betting_strategy'),
            bet_data.get('reasoning'),
            bet_data.get('sentiment_score'),
            bet_data.get('sentiment_analysis'),
            bet_data.get('news_score'),
            bet_data.get('news_analysis'),
            bet_data.get('technical_score'),
            bet_data.get('technical_analysis'),
            bet_data.get('fundamental_score'),
            bet_data.get('fundamental_analysis'),
            bet_data.get('volatility_score'),
            bet_data.get('volatility_analysis'),
            bet_data['execution_timestamp'],
            bet_data.get('simulation_mode', 1),
            datetime.now().isoformat()
        ))
        
        bet_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return bet_id
    
    def update_autonomous_bet_result(self, bet_id: int, actual_result: int, profit_loss: float):
        """
        Actualiza el resultado de una apuesta autónoma.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE autonomous_bets
        SET actual_result = ?, profit_loss = ?, resolution_timestamp = ?
        WHERE id = ?
        ''', (actual_result, profit_loss, datetime.now().isoformat(), bet_id))
        
        conn.commit()
        conn.close()
    
    def save_autonomous_cycle(self, cycle_data: Dict) -> int:
        """
        Guarda un ciclo de ejecución autónoma.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO autonomous_cycles (
            cycle_timestamp, total_events_analyzed, total_bets_placed,
            total_bets_skipped, simulation_mode, execution_summary, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            cycle_data['timestamp'],
            cycle_data.get('total_events_analyzed', 0),
            cycle_data.get('total_bets_placed', 0),
            cycle_data.get('total_bets_skipped', 0),
            cycle_data.get('simulation_mode', 1),
            json.dumps(cycle_data),
            datetime.now().isoformat()
        ))
        
        cycle_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return cycle_id
    
    def save_strategy_adaptation(self, adaptation_data: Dict) -> int:
        """
        Guarda una adaptación de estrategia.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO strategy_adaptations (
            firm_name, adaptation_level, trigger_reason, previous_params,
            new_params, changes_applied, bankroll_at_adaptation, loss_percentage,
            adaptation_timestamp, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            adaptation_data['firm_name'],
            adaptation_data['level'],
            adaptation_data.get('description'),
            json.dumps(adaptation_data.get('previous_params', {})),
            json.dumps(adaptation_data.get('new_params', {})),
            json.dumps(adaptation_data.get('changes', [])),
            adaptation_data.get('bankroll_at_adaptation'),
            adaptation_data.get('loss_percentage'),
            adaptation_data['timestamp'],
            datetime.now().isoformat()
        ))
        
        adaptation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return adaptation_id
    
    def get_autonomous_bets(self, firm_name: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Obtiene apuestas autónomas registradas con análisis de 5 áreas.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if firm_name:
            cursor.execute('''
            SELECT * FROM autonomous_bets
            WHERE firm_name = ?
            ORDER BY created_at DESC
            LIMIT ?
            ''', (firm_name, limit))
        else:
            cursor.execute('''
            SELECT * FROM autonomous_bets
            ORDER BY created_at DESC
            LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        bets = []
        for row in rows:
            bets.append({
                'id': row[0],
                'firm_name': row[1],
                'event_id': row[2],
                'event_description': row[3],
                'category': row[4],
                'bet_size': row[5],
                'probability': row[6],
                'confidence': row[7],
                'expected_value': row[8],
                'risk_level': row[9],
                'adaptation_level': row[10],
                'betting_strategy': row[11],
                'reasoning': row[12],
                'sentiment_score': row[13],
                'sentiment_analysis': row[14],
                'news_score': row[15],
                'news_analysis': row[16],
                'technical_score': row[17],
                'technical_analysis': row[18],
                'fundamental_score': row[19],
                'fundamental_analysis': row[20],
                'volatility_score': row[21],
                'volatility_analysis': row[22],
                'actual_result': row[23],
                'profit_loss': row[24],
                'execution_timestamp': row[25],
                'resolution_timestamp': row[26],
                'simulation_mode': row[27],
                'created_at': row[28]
            })
        
        return bets
    
    def get_strategy_adaptations(self, firm_name: Optional[str] = None) -> List[Dict]:
        """
        Obtiene historial de adaptaciones de estrategia.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if firm_name:
            cursor.execute('''
            SELECT * FROM strategy_adaptations
            WHERE firm_name = ?
            ORDER BY adaptation_timestamp DESC
            ''', (firm_name,))
        else:
            cursor.execute('''
            SELECT * FROM strategy_adaptations
            ORDER BY adaptation_timestamp DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        adaptations = []
        for row in rows:
            adaptations.append({
                'id': row[0],
                'firm_name': row[1],
                'adaptation_level': row[2],
                'trigger_reason': row[3],
                'previous_params': json.loads(row[4]) if row[4] else {},
                'new_params': json.loads(row[5]) if row[5] else {},
                'changes_applied': json.loads(row[6]) if row[6] else [],
                'bankroll_at_adaptation': row[7],
                'loss_percentage': row[8],
                'adaptation_timestamp': row[9],
                'created_at': row[10]
            })
        
        return adaptations
    
    def get_autonomous_statistics(self, firm_name: str) -> Dict:
        """
        Obtiene estadísticas del modo autónomo para una IA.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            COUNT(*) as total_bets,
            SUM(CASE WHEN actual_result = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN actual_result = 0 THEN 1 ELSE 0 END) as losses,
            SUM(COALESCE(profit_loss, 0)) as total_profit,
            AVG(bet_size) as avg_bet_size,
            AVG(probability) as avg_probability,
            AVG(confidence) as avg_confidence
        FROM autonomous_bets
        WHERE firm_name = ?
        ''', (firm_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            total_bets = row[0] or 0
            wins = row[1] or 0
            win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
            
            return {
                'firm_name': firm_name,
                'total_autonomous_bets': total_bets,
                'wins': wins,
                'losses': row[2] or 0,
                'win_rate': round(win_rate, 2),
                'total_profit': row[3] or 0,
                'avg_bet_size': row[4] or 0,
                'avg_probability': row[5] or 0,
                'avg_confidence': row[6] or 0
            }
        
        return {}
    
    def get_recent_cycles(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene los ciclos de ejecución autónoma más recientes.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM autonomous_cycles
        ORDER BY created_at DESC
        LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        cycles = []
        for row in rows:
            cycles.append({
                'id': row[0],
                'cycle_timestamp': row[1],
                'total_events_analyzed': row[2],
                'total_bets_placed': row[3],
                'total_bets_skipped': row[4],
                'simulation_mode': row[5],
                'execution_summary': json.loads(row[6]) if row[6] else {},
                'created_at': row[7]
            })
        
        return cycles
    
    def get_latest_ai_thinking(self) -> List[Dict]:
        """
        Obtiene el análisis más reciente de cada IA con desglose de las 5 áreas.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
        latest_thinking = []
        
        for firm in firms:
            cursor.execute('''
            SELECT * FROM autonomous_bets
            WHERE firm_name = ?
            ORDER BY created_at DESC
            LIMIT 1
            ''', (firm,))
            
            row = cursor.fetchone()
            if row:
                latest_thinking.append({
                    'firm_name': row[1],
                    'event_description': row[3],
                    'category': row[4],
                    'probability': row[6],
                    'confidence': row[7],
                    'sentiment_score': row[13],
                    'sentiment_analysis': row[14],
                    'news_score': row[15],
                    'news_analysis': row[16],
                    'technical_score': row[17],
                    'technical_analysis': row[18],
                    'fundamental_score': row[19],
                    'fundamental_analysis': row[20],
                    'volatility_score': row[21],
                    'volatility_analysis': row[22],
                    'execution_timestamp': row[25]
                })
        
        conn.close()
        return latest_thinking
    
    def get_active_positions_from_db(self) -> List[Dict]:
        """
        Obtiene posiciones activas (bets sin resolver) con análisis completo.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM autonomous_bets
        WHERE actual_result IS NULL
        ORDER BY created_at DESC
        LIMIT 50
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        positions = []
        for row in rows:
            positions.append({
                'id': row[0],
                'firm_name': row[1],
                'event_id': row[2],
                'event_description': row[3],
                'category': row[4],
                'bet_size': row[5],
                'probability': row[6],
                'confidence': row[7],
                'expected_value': row[8],
                'risk_level': row[9],
                'reasoning': row[12],
                'sentiment_score': row[13],
                'sentiment_analysis': row[14],
                'news_score': row[15],
                'news_analysis': row[16],
                'technical_score': row[17],
                'technical_analysis': row[18],
                'fundamental_score': row[19],
                'fundamental_analysis': row[20],
                'volatility_score': row[21],
                'volatility_analysis': row[22],
                'execution_timestamp': row[25]
            })
        
        return positions
    
    def update_tier_state(self, firm_name: str, current_tier: str, previous_tier: Optional[str] = None, cooldown_end: Optional[str] = None):
        """
        Actualiza el estado del tier de riesgo de una AI.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE virtual_portfolio
        SET current_tier = ?, previous_tier = ?, cooldown_end = ?
        WHERE firm_name = ?
        ''', (current_tier, previous_tier, cooldown_end, firm_name))
        
        conn.commit()
        conn.close()
    
    def reset_daily_loss(self, firm_name: Optional[str] = None):
        """
        Resetea el contador de pérdidas diarias. Si no se especifica firm_name, resetea todas.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        if firm_name:
            cursor.execute('''
            UPDATE virtual_portfolio
            SET daily_loss_today = 0.0, last_reset_date = ?
            WHERE firm_name = ?
            ''', (today, firm_name))
        else:
            cursor.execute('''
            UPDATE virtual_portfolio
            SET daily_loss_today = 0.0, last_reset_date = ?
            ''', (today,))
        
        conn.commit()
        conn.close()
    
    def record_daily_loss(self, firm_name: str, loss_amount: float):
        """
        Registra una pérdida en el contador diario.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE virtual_portfolio
        SET daily_loss_today = daily_loss_today + ?
        WHERE firm_name = ?
        ''', (loss_amount, firm_name))
        
        conn.commit()
        conn.close()
    
    def get_portfolio_with_tier_info(self, firm_name: str) -> Optional[Dict]:
        """
        Obtiene información del portfolio incluyendo tier state.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM virtual_portfolio
        WHERE firm_name = ?
        ''', (firm_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'firm_name': row[1],
                'initial_balance': row[2],
                'current_balance': row[3],
                'total_returns': row[4],
                'current_tier': row[6] if len(row) > 6 else 'conservative',
                'previous_tier': row[7] if len(row) > 7 else None,
                'cooldown_end': row[8] if len(row) > 8 else None,
                'daily_loss_today': row[9] if len(row) > 9 else 0.0,
                'last_reset_date': row[10] if len(row) > 10 else None,
                'total_bets': row[11] if len(row) > 11 else 0,
                'winning_bets': row[12] if len(row) > 12 else 0
            }
        return None
    
    def update_portfolio_bet_stats(self, firm_name: str, won: bool):
        """
        Actualiza estadísticas de apuestas en el portfolio.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if won:
            cursor.execute('''
            UPDATE virtual_portfolio
            SET total_bets = total_bets + 1, winning_bets = winning_bets + 1
            WHERE firm_name = ?
            ''', (firm_name,))
        else:
            cursor.execute('''
            UPDATE virtual_portfolio
            SET total_bets = total_bets + 1
            WHERE firm_name = ?
            ''', (firm_name,))
        
        conn.commit()
        conn.close()
    
    def get_daily_bet_total(self, date: str = None) -> float:
        """
        Obtiene el total apostado hoy (o en fecha específica).
        
        Args:
            date: Fecha en formato YYYY-MM-DD. Si None, usa fecha actual.
            
        Returns:
            Total apostado en la fecha
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT total_bet_amount FROM daily_bet_tracking
        WHERE tracking_date = ?
        ''', (date,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
        return 0.0
    
    def add_to_daily_bet_total(self, amount: float, date: str = None) -> float:
        """
        Agrega una cantidad al total diario de apuestas.
        
        Args:
            amount: Cantidad a agregar
            date: Fecha en formato YYYY-MM-DD. Si None, usa fecha actual.
            
        Returns:
            Nuevo total diario
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Intentar actualizar registro existente
        cursor.execute('''
        UPDATE daily_bet_tracking
        SET total_bet_amount = total_bet_amount + ?,
            bet_count = bet_count + 1,
            last_updated = ?
        WHERE tracking_date = ?
        ''', (amount, datetime.now().isoformat(), date))
        
        # Si no existe, insertar nuevo registro
        if cursor.rowcount == 0:
            cursor.execute('''
            INSERT INTO daily_bet_tracking (tracking_date, total_bet_amount, bet_count, last_updated)
            VALUES (?, ?, 1, ?)
            ''', (date, amount, datetime.now().isoformat()))
        
        # Obtener nuevo total
        cursor.execute('''
        SELECT total_bet_amount FROM daily_bet_tracking
        WHERE tracking_date = ?
        ''', (date,))
        
        new_total = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return new_total
