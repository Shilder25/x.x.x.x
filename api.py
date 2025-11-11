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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway deployment monitoring"""
    try:
        env_status = {
            'database': 'connected' if db else 'error',
            'api_keys_configured': {
                'openai': bool(os.getenv('AI_INTEGRATIONS_OPENAI_API_KEY')),
                'deepseek': bool(os.getenv('DEEPSEEK_API_KEY')),
                'qwen': bool(os.getenv('QWEN_API_KEY')),
                'xai': bool(os.getenv('XAI_API_KEY')),
                'opinion_trade': bool(os.getenv('OPINION_TRADE_API_KEY')),
                'wallet': bool(os.getenv('OPINION_WALLET_PRIVATE_KEY'))
            },
            'bankroll_mode': os.getenv('BANKROLL_MODE', 'UNKNOWN'),
            'system_enabled': os.getenv('SYSTEM_ENABLED', 'false')
        }
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'environment': env_status
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

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
                current_balance = perf.get('current_balance')
                total_profit = perf.get('total_profit')
                accuracy = perf.get('accuracy')
                total_predictions = perf.get('total_predictions')
                
                chart_data.append({
                    'firm': firm_name,
                    'color': AI_FIRMS[firm_name]['color'],
                    'total_value': 10000.0 if current_balance is None else current_balance,
                    'profit_loss': 0.0 if total_profit is None else total_profit,
                    'win_rate': (0.0 if accuracy is None else accuracy) * 100,
                    'total_bets': 0 if total_predictions is None else total_predictions
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
        from datetime import datetime, timedelta
        
        history_data = {}
        
        conn = sqlite3.connect('trading_agents.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT MIN(date(execution_timestamp)) FROM autonomous_bets")
        earliest_date_result = cursor.fetchone()[0]
        
        if earliest_date_result:
            earliest_date = datetime.fromisoformat(earliest_date_result)
            system_start_date = (earliest_date - timedelta(days=1)).date().isoformat()
        else:
            system_start_date = datetime.now().date().isoformat()
        
        all_dates = set()
        firm_daily_data = {}
        
        for firm_name in AI_FIRMS.keys():
            cursor.execute("""
                SELECT date(execution_timestamp) as day, 
                       SUM(CASE WHEN actual_result=1 THEN bet_size * 0.95 ELSE -bet_size END) as daily_pl
                FROM autonomous_bets 
                WHERE firm_name = ?
                GROUP BY date(execution_timestamp)
                ORDER BY day ASC
            """, (firm_name,))
            
            rows = cursor.fetchall()
            firm_daily_data[firm_name] = {row[0]: row[1] for row in rows}
            all_dates.update(firm_daily_data[firm_name].keys())
        
        conn.close()
        
        sorted_dates = sorted(list(all_dates))
        
        for firm_name in AI_FIRMS.keys():
            cumulative_value = 10000.0
            daily_values = [{'date': system_start_date, 'value': 10000.0}]
            
            for date in sorted_dates:
                daily_pl = firm_daily_data[firm_name].get(date, 0)
                cumulative_value += daily_pl if daily_pl else 0
                daily_values.append({
                    'date': date,
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
                total_bets = perf.get('total_predictions')
                wins = perf.get('correct_predictions')
                initial_balance = perf.get('initial_balance')
                current_balance = perf.get('current_balance')
                accuracy = perf.get('accuracy')
                total_profit = perf.get('total_profit')
                sharpe_ratio = perf.get('sharpe_ratio')
                
                total_bets = 0 if total_bets is None else total_bets
                wins = 0 if wins is None else wins
                losses = total_bets - wins
                initial_balance = 10000.0 if initial_balance is None else initial_balance
                current_balance = 10000.0 if current_balance is None else current_balance
                accuracy = 0.0 if accuracy is None else accuracy
                total_profit = 0.0 if total_profit is None else total_profit
                sharpe_ratio = 0.0 if sharpe_ratio is None else sharpe_ratio
                
                leaderboard.append({
                    'rank': 0,
                    'firm': firm_name,
                    'model': AI_FIRMS[firm_name]['model'],
                    'total_bets': total_bets,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': round(accuracy * 100, 1),
                    'profit_loss': round(total_profit, 2),
                    'account_value': round(current_balance, 2),
                    'roi': round((current_balance - initial_balance) / initial_balance * 100, 1) if initial_balance > 0 else 0.0,
                    'sharpe_ratio': round(sharpe_ratio, 2),
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
            'content': 'Each AI starts with $10,000 virtual capital. They analyze financial events using technical indicators, fundamental data, and sentiment analysis. Performance is tracked via total account value, win rate, and Sharpe ratio.'
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

@app.route('/api/ai-thinking', methods=['GET'])
def get_ai_thinking():
    """Get latest AI thinking/analysis for all 5 AIs with 5-area breakdown"""
    try:
        latest_thinking = db.get_latest_ai_thinking()
        return jsonify(latest_thinking)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-decisions-history', methods=['GET'])
def get_ai_decisions_history():
    """Get full history of AI decisions with 5-area analysis"""
    try:
        import sqlite3
        from flask import request
        
        limit = request.args.get('limit', 100, type=int)
        firm_name = request.args.get('firm', None)
        
        bets = db.get_autonomous_bets(firm_name=firm_name, limit=limit)
        return jsonify(bets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/active-positions', methods=['GET'])
def get_active_positions():
    """Get active positions (unresolved bets) with full analysis"""
    try:
        positions = db.get_active_positions_from_db()
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-daily-cycle', methods=['POST'])
def run_daily_cycle():
    """
    Trigger the daily autonomous cycle manually (PROTECTED ENDPOINT).
    
    This endpoint allows external cron services (like cron-job.org) to trigger
    the daily prediction cycle without needing a dedicated Railway cron service.
    
    Security: Requires X-Cron-Secret header matching CRON_SECRET environment variable.
    Uses constant-time comparison to prevent timing attacks.
    
    Returns:
        JSON with cycle execution results
    """
    from flask import request
    import hmac
    
    # Verify authentication
    expected_secret = os.getenv('CRON_SECRET')
    if not expected_secret:
        return jsonify({
            'success': False,
            'error': 'CRON_SECRET not configured on server',
            'message': 'Endpoint not properly configured'
        }), 500
    
    provided_secret = request.headers.get('X-Cron-Secret', '')
    
    # Use constant-time comparison to prevent timing attacks
    if not provided_secret or not hmac.compare_digest(expected_secret, provided_secret):
        print(f"[SECURITY] Unauthorized attempt to trigger daily cycle from {request.remote_addr}")
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Invalid or missing X-Cron-Secret header'
        }), 401
    
    try:
        print(f"\n[MANUAL TRIGGER] Daily cycle triggered via API endpoint at {datetime.now().isoformat()}")
        
        engine = AutonomousEngine(db)
        results = engine.run_daily_cycle()
        
        return jsonify({
            'success': True,
            'message': 'Daily cycle completed successfully',
            'results': results
        }), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[ERROR] Daily cycle failed: {str(e)}")
        print(error_traceback)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Daily cycle failed'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
