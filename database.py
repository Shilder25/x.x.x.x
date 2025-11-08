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
        
        conn.commit()
        conn.close()
    
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
        
        cursor.execute('''
        UPDATE firm_performance
        SET total_predictions = ?,
            correct_predictions = ?,
            total_profit = ?,
            total_tokens = ?,
            total_cost = ?,
            accuracy = ?,
            updated_at = ?
        WHERE firm_name = ?
        ''', (total_preds, correct_preds or 0, total_profit or 0, total_tokens or 0, 
              total_cost or 0, accuracy, datetime.now().isoformat(), firm_name))
        
        conn.commit()
        conn.close()
    
    def get_firm_performance(self, firm_name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT fp.*, vp.current_balance, vp.initial_balance, vp.total_returns
        FROM firm_performance fp
        LEFT JOIN virtual_portfolio vp ON fp.firm_name = vp.firm_name
        WHERE fp.firm_name = ?
        ''', (firm_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'firm_name': row[1],
                'total_predictions': row[2],
                'correct_predictions': row[3],
                'total_profit': row[4],
                'total_tokens': row[5],
                'total_cost': row[6],
                'sharpe_ratio': row[7],
                'accuracy': row[8],
                'current_balance': row[9] if row[9] else 10000.0,
                'initial_balance': row[10] if row[10] else 10000.0,
                'total_returns': row[11] if row[11] else 0.0
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
