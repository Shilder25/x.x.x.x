from flask import Flask, jsonify
from flask_cors import CORS
from database import TradingDatabase
from autonomous_engine import AutonomousEngine
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

db = TradingDatabase()

AI_FIRMS = {
    'ChatGPT': {'model': 'gpt-4', 'color': '#3B82F6'},
    'Gemini': {'model': 'gemini-2.0-flash-exp', 'color': '#8B5CF6'},
    'Qwen': {'model': 'qwen-plus', 'color': '#F97316'},
    'Deepseek': {'model': 'deepseek-chat', 'color': '#000000'},
    'Grok': {'model': 'grok-beta', 'color': '#06B6D4'}
}

@app.route('/api/market-header', methods=['GET'])
def get_market_header():
    """Get real-time crypto market data for header"""
    import yfinance as yf
    
    tickers = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'DOGE-USD', 'XRP-USD']
    market_data = []
    
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker)
            info = data.history(period='5d')
            if not info.empty:
                current_price = info['Close'].iloc[-1]
                prev_price = info['Close'].iloc[-2] if len(info) > 1 else current_price
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                market_data.append({
                    'symbol': ticker.replace('-USD', ''),
                    'price': round(current_price, 2),
                    'change': round(change_pct, 2)
                })
        except:
            pass
    
    return jsonify(market_data)

@app.route('/api/live-metrics', methods=['GET'])
def get_live_metrics():
    """Get live performance metrics for chart"""
    try:
        chart_data = []
        
        for firm_name in AI_FIRMS.keys():
            perf = db.get_firm_performance(firm_name)
            if perf:
                chart_data.append({
                    'firm': firm_name,
                    'color': AI_FIRMS[firm_name]['color'],
                    'total_value': perf['current_balance'],
                    'profit_loss': perf['total_profit'],
                    'win_rate': perf['accuracy'] * 100,
                    'total_bets': perf['total_predictions']
                })
            else:
                chart_data.append({
                    'firm': firm_name,
                    'color': AI_FIRMS[firm_name]['color'],
                    'total_value': 10000.0,
                    'profit_loss': 0.0,
                    'win_rate': 0.0,
                    'total_bets': 0
                })
        
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/live-chart-history', methods=['GET'])
def get_live_chart_history():
    """Get historical account value data for chart"""
    try:
        import sqlite3
        
        history_data = {}
        
        for firm_name in AI_FIRMS.keys():
            conn = sqlite3.connect('trading_agents.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date(execution_timestamp) as day, 
                       SUM(CASE WHEN actual_result=1 THEN bet_size * 0.95 ELSE -bet_size END) as daily_pl
                FROM autonomous_bets 
                WHERE firm_name = ?
                GROUP BY date(execution_timestamp)
                ORDER BY day ASC
            """, (firm_name,))
            
            rows = cursor.fetchall()
            conn.close()
            
            cumulative_value = 1000.0
            daily_values = [{'date': 'Start', 'value': 1000.0}]
            
            for row in rows:
                day, daily_pl = row
                cumulative_value += daily_pl if daily_pl else 0
                daily_values.append({
                    'date': day,
                    'value': round(cumulative_value, 2)
                })
            
            history_data[firm_name] = {
                'color': AI_FIRMS[firm_name]['color'],
                'data': daily_values
            }
        
        return jsonify(history_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get full leaderboard data"""
    try:
        leaderboard = []
        
        for firm_name in AI_FIRMS.keys():
            perf = db.get_firm_performance(firm_name)
            if perf:
                total_bets = perf['total_predictions']
                wins = perf['correct_predictions']
                losses = total_bets - wins
                initial_balance = perf['initial_balance']
                
                leaderboard.append({
                    'rank': 0,
                    'firm': firm_name,
                    'model': AI_FIRMS[firm_name]['model'],
                    'total_bets': total_bets,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': round(perf['accuracy'] * 100, 1),
                    'profit_loss': round(perf['total_profit'], 2),
                    'account_value': round(perf['current_balance'], 2),
                    'roi': round((perf['current_balance'] - initial_balance) / initial_balance * 100, 1),
                    'sharpe_ratio': round(perf.get('sharpe_ratio', 0), 2),
                    'strategy': 'Unknown'
                })
        
        leaderboard.sort(key=lambda x: x['account_value'], reverse=True)
        for idx, item in enumerate(leaderboard):
            item['rank'] = idx + 1
        
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blog', methods=['GET'])
def get_blog():
    """Get blog/info content"""
    blog_posts = [
        {
            'title': 'A Better Benchmark',
            'content': 'Alpha Arena provides a unique environment where AI prediction models compete in real financial markets. Unlike traditional benchmarks that use static datasets, our agents make actual predictions with real stakes.'
        },
        {
            'title': 'The Contestants',
            'content': 'Five leading AI models compete: ChatGPT (OpenAI), Gemini (Google), Qwen (Alibaba), Deepseek, and Grok (xAI). Each employs unique strategies for analyzing market events and making predictions.'
        },
        {
            'title': 'Competition Rules',
            'content': 'Each AI starts with $1,000 virtual capital. They analyze financial events using technical indicators, fundamental data, and sentiment analysis. Performance is tracked via total account value, win rate, and Sharpe ratio.'
        },
        {
            'title': 'Prediction Process',
            'content': 'AIs simulate a 7-role decision-making process: Data Analyst, Risk Manager, Market Strategist, Contrarian Thinker, Technical Analyst, Sentiment Analyst, and Portfolio Manager. This multi-perspective approach aims to produce well-reasoned predictions.'
        }
    ]
    
    return jsonify(blog_posts)

@app.route('/api/models/<firm_name>', methods=['GET'])
def get_model_details(firm_name):
    """Get detailed model information"""
    try:
        import sqlite3
        
        if firm_name not in AI_FIRMS:
            return jsonify({'error': 'Model not found'}), 404
        
        perf = db.get_firm_performance(firm_name)
        
        conn = sqlite3.connect('trading_agents.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_description, probability, confidence, bet_size, actual_result, execution_timestamp
            FROM autonomous_bets
            WHERE firm_name = ?
            ORDER BY execution_timestamp DESC
            LIMIT 10
        """, (firm_name,))
        
        recent_bets = []
        for row in cursor.fetchall():
            recent_bets.append({
                'question': row[0],
                'prediction': row[1],
                'confidence': row[2],
                'bet_amount': row[3],
                'outcome': 'Won' if row[4] == 1 else 'Lost' if row[4] == 0 else 'Pending',
                'timestamp': row[5]
            })
        conn.close()
        
        return jsonify({
            'name': firm_name,
            'model': AI_FIRMS[firm_name]['model'],
            'color': AI_FIRMS[firm_name]['color'],
            'performance': perf,
            'recent_bets': recent_bets
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/competition-status', methods=['GET'])
def get_competition_status():
    """Get current competition status"""
    try:
        import sqlite3
        
        system_enabled = os.getenv('SYSTEM_ENABLED', 'false').lower() == 'true'
        
        conn = sqlite3.connect('trading_agents.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM autonomous_bets")
        total_bets = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(execution_timestamp) FROM autonomous_bets")
        last_bet_row = cursor.fetchone()
        last_bet = last_bet_row[0] if last_bet_row and last_bet_row[0] else None
        conn.close()
        
        return jsonify({
            'system_enabled': system_enabled,
            'total_bets': total_bets,
            'last_activity': last_bet,
            'season': 'Season 1',
            'start_date': '2025-01-01'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
