from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from database import TradingDatabase
from autonomous_engine import AutonomousEngine
from logger import autonomous_logger as logger
import os
from datetime import datetime, timedelta

# DEBUG: Railway environment variable detection (secure - no credential values exposed)
print("=" * 80)
print("[DEBUG] RAILWAY ENVIRONMENT VARIABLE CHECK - API.PY STARTUP")
print("=" * 80)
api_key_val = os.getenv('OPINION_TRADE_API_KEY', '')
private_key_val = os.getenv('OPINION_WALLET_PRIVATE_KEY', '')
print(f"OPINION_TRADE_API_KEY: {'SET' if api_key_val else 'MISSING'} (len={len(api_key_val)})")
print(f"OPINION_WALLET_PRIVATE_KEY: {'SET' if private_key_val else 'MISSING'} (len={len(private_key_val)})")
print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'NOT SET')}")
print(f"RAILWAY_SERVICE_NAME: {os.getenv('RAILWAY_SERVICE_NAME', 'NOT SET')}")
print("=" * 80)

app = Flask(__name__)
CORS(app)

db = TradingDatabase()

AI_FIRMS = {
    'ChatGPT': {'model': 'gpt-4o', 'color': '#3B82F6'},
    'Gemini': {'model': 'gemini-2.5-pro → gemini-2.5-flash', 'color': '#8B5CF6'},
    'Qwen': {'model': 'qwen-max-2025-01-25', 'color': '#F97316'},
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
                'openai': bool(os.getenv('AI_INTEGRATIONS_OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')),
                'gemini': bool(os.getenv('AI_INTEGRATIONS_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')),
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

@app.route('/test-opinion-detailed', methods=['GET'])
def test_opinion_detailed():
    """Test Opinion.trade API with detailed parsing diagnostics"""
    from opinion_trade_api import OpinionTradeAPI
    
    opinion_api = OpinionTradeAPI()
    result = opinion_api.get_available_events(limit=5)
    
    return jsonify(result), 200

@app.route('/test-opinion', methods=['GET'])
def test_opinion_trade():
    """
    Test Opinion.trade API accessibility from current Railway deployment region.
    This endpoint can be called after changing regions to verify geo-blocking status.
    """
    import time
    from opinion_clob_sdk import Client, CHAIN_ID_BNB_MAINNET
    from opinion_clob_sdk.model import TopicType, TopicStatusFilter
    from eth_account import Account
    
    region = os.getenv('RAILWAY_REGION', 'Unknown')
    
    try:
        api_key = os.getenv('OPINION_TRADE_API_KEY')
        private_key = os.getenv('OPINION_WALLET_PRIVATE_KEY')
        
        if not api_key or not private_key:
            return jsonify({
                'success': False,
                'region': region,
                'error': 'Missing OPINION_TRADE_API_KEY or OPINION_WALLET_PRIVATE_KEY',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        account = Account.from_key(private_key)
        wallet_address = account.address
        
        start_time = time.time()
        
        client = Client(
            host='https://proxy.opinion.trade:8443',
            apikey=api_key,
            chain_id=CHAIN_ID_BNB_MAINNET,
            rpc_url='https://bsc-dataseed.binance.org/',
            private_key=private_key,
            multi_sig_addr=wallet_address,
            conditional_tokens_addr='0xAD1a38cEc043e70E83a3eC30443dB285ED10D774',
            multisend_addr='0x998739BFdAAdde7C933B942a68053933098f9EDa',
        )
        
        init_time = time.time() - start_time
        
        test_start = time.time()
        response = client.get_markets(
            topic_type=TopicType.BINARY,
            status=TopicStatusFilter.ACTIVATED,
            page=1,
            limit=5
        )
        api_time = time.time() - test_start
        
        if response.errno == 0:
            markets = response.result.list
            sample_markets = [
                {
                    'id': m.market_id,
                    'title': m.market_title[:80]
                } for m in markets[:3]
            ]
            
            return jsonify({
                'success': True,
                'region': region,
                'status': 'ACCESSIBLE',
                'message': f'✅ Opinion.trade API is accessible from {region}',
                'wallet': wallet_address,
                'markets_retrieved': len(markets),
                'sample_markets': sample_markets,
                'performance': {
                    'sdk_init_time': round(init_time, 3),
                    'api_call_time': round(api_time, 3),
                    'total_time': round(init_time + api_time, 3)
                },
                'timestamp': datetime.now().isoformat()
            }), 200
            
        elif response.errno == 10403:
            return jsonify({
                'success': False,
                'region': region,
                'status': 'GEO_BLOCKED',
                'message': f'❌ Region {region} is GEO-BLOCKED by Opinion.trade',
                'error_code': 10403,
                'error_message': response.errmsg,
                'wallet': wallet_address,
                'next_steps': [
                    'Try deploying to a different region (US East, US West)',
                    'Contact Opinion.trade support for allowed regions',
                    'Provide API key for whitelisting'
                ],
                'timestamp': datetime.now().isoformat()
            }), 403
            
        else:
            return jsonify({
                'success': False,
                'region': region,
                'status': 'API_ERROR',
                'message': f'API returned error {response.errno}',
                'error_code': response.errno,
                'error_message': response.errmsg,
                'wallet': wallet_address,
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'region': region,
            'status': 'EXCEPTION',
            'message': 'Exception occurred during test',
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

@app.route('/api/recent-trades', methods=['GET'])
def get_recent_trades():
    """Get recent trades from Opinion.trade (últimos 20 trades)"""
    try:
        from opinion_trade_api import OpinionTradeAPI
        
        limit = request.args.get('limit', 20, type=int)
        
        opinion_api = OpinionTradeAPI()
        trades_response = opinion_api.get_my_trades(limit=limit)
        
        if trades_response.get('success'):
            return jsonify({
                'success': True,
                'trades': trades_response.get('trades', [])
            })
        else:
            # Check if it's the expected "no trades yet" API error (errno 10403)
            api_errno = trades_response.get('errno')
            if api_errno == 10403:
                # Expected case: no trades yet, return empty array gracefully
                return jsonify({
                    'success': True,
                    'trades': [],
                    'api_info': 'No trades recorded yet on Opinion.trade',
                    'api_errno': api_errno
                })
            else:
                # Unexpected API error - surface it properly
                return jsonify({
                    'success': False,
                    'errno': api_errno,
                    'error': trades_response.get('error', 'Unknown API error'),
                    'message': trades_response.get('message', '')
                }), 500
    except Exception as e:
        # Real server exception - surface it as error
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Exception in /api/recent-trades: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Server error',
            'message': str(e)
        }), 500

@app.route('/api/ai-trades/<firm_name>', methods=['GET'])
def get_ai_trades(firm_name):
    """Get trade history for a specific AI from database"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        # Validar que el firm_name sea válido
        if firm_name not in AI_FIRMS:
            return jsonify({
                'success': False,
                'error': f'Invalid firm name: {firm_name}'
            }), 400
        
        # Obtener trades de la base de datos para esta IA
        bets = db.get_autonomous_bets(firm_name=firm_name, limit=limit)
        
        return jsonify({
            'success': True,
            'firm_name': firm_name,
            'trades': bets
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cancelled-orders', methods=['GET'])
def get_cancelled_orders():
    """Get cancelled orders with strikes history and reasons"""
    try:
        limit = request.args.get('limit', 50, type=int)
        firm_name = request.args.get('firm', None)
        
        cancelled_orders = db.get_cancelled_orders(firm_name=firm_name, limit=limit)
        
        return jsonify({
            'success': True,
            'cancelled_orders': cancelled_orders
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/monitor-orders', methods=['POST'])
def monitor_orders():
    """
    Monitor active orders with 3-strike system (PROTECTED ENDPOINT).
    
    This endpoint should be called every 30 minutes by an external cron service
    to review active positions and cancel orders after 3 consecutive strikes.
    
    Security: Requires X-Cron-Secret header matching CRON_SECRET environment variable.
    
    Returns:
        JSON with monitoring execution results
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
        print(f"[SECURITY] Unauthorized attempt to trigger order monitoring from {request.remote_addr}")
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Invalid or missing X-Cron-Secret header'
        }), 401
    
    try:
        print(f"\n[ORDER MONITOR] Triggered via API endpoint at {datetime.now().isoformat()}")
        
        from autonomous_engine import AutonomousEngine, OrderMonitor
        
        # Pass credentials explicitly to avoid Gunicorn multi-worker env var issues
        api_key = os.getenv('OPINION_TRADE_API_KEY')
        private_key = os.getenv('OPINION_WALLET_PRIVATE_KEY')
        
        engine = AutonomousEngine(db, opinion_api_key=api_key, opinion_private_key=private_key)
        
        order_monitor = OrderMonitor(engine.opinion_api, engine.db, engine.orchestrator)
        monitoring_stats = order_monitor.monitor_all_orders()
        
        return jsonify({
            'success': True,
            'message': 'Order monitoring completed successfully',
            'stats': monitoring_stats
        }), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[ERROR] Order monitoring failed: {str(e)}")
        print(error_traceback)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Order monitoring failed'
        }), 500

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
        
        # Pass credentials explicitly to avoid Gunicorn multi-worker env var issues
        api_key = os.getenv('OPINION_TRADE_API_KEY')
        private_key = os.getenv('OPINION_WALLET_PRIVATE_KEY')
        
        engine = AutonomousEngine(db, opinion_api_key=api_key, opinion_private_key=private_key)
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

@app.route('/admin', methods=['GET'])
def admin_page():
    """Serve admin page for manual cycle triggering"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Trading Agents</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 500px;
                width: 100%;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                color: #555;
                margin-bottom: 8px;
                font-weight: 500;
                font-size: 14px;
            }
            input[type="password"] {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input[type="password"]:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                font-size: 14px;
                display: none;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status.loading {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .spinner {
                display: inline-block;
                width: 14px;
                height: 14px;
                border: 2px solid rgba(0,0,0,0.1);
                border-radius: 50%;
                border-top-color: #0c5460;
                animation: spin 1s linear infinite;
                margin-right: 8px;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .results {
                margin-top: 10px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
                font-family: monospace;
                font-size: 12px;
                max-height: 300px;
                overflow-y: auto;
            }
            .logs-section {
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #e0e0e0;
            }
            .logs-viewer {
                margin-top: 15px;
                padding: 15px;
                background: #1e1e1e;
                color: #d4d4d4;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                max-height: 500px;
                overflow-y: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
                display: none;
            }
            .logs-viewer.visible {
                display: block;
            }
            .log-line {
                line-height: 1.6;
            }
            .log-admin { color: #4ec9b0; }
            .log-info { color: #9cdcfe; }
            .log-category { color: #dcdcaa; }
            .log-bet { color: #4fc1ff; }
            .log-skip { color: #ce9178; }
            .log-error { color: #f48771; }
            .log-warning { color: #ffd700; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Admin Panel</h1>
            <p class="subtitle">Trigger AI prediction cycle manually</p>
            
            <form id="adminForm">
                <div class="form-group">
                    <label for="password">Admin Password</label>
                    <input type="password" id="password" placeholder="Enter admin password" required>
                </div>
                
                <button type="submit" id="submitBtn">
                    Run Daily Cycle
                </button>
            </form>
            
            <div id="status" class="status"></div>
            
            <div class="logs-section">
                <h2>📋 System Logs</h2>
                <p class="subtitle">View autonomous engine execution logs</p>
                <button type="button" id="viewLogsBtn" style="margin-bottom: 15px;">
                    View Recent Logs (Last 500 lines)
                </button>
                <div id="logsViewer" class="logs-viewer"></div>
            </div>
        </div>

        <script>
            const form = document.getElementById('adminForm');
            const submitBtn = document.getElementById('submitBtn');
            const statusDiv = document.getElementById('status');
            const passwordInput = document.getElementById('password');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const password = passwordInput.value;
                
                // Show loading state
                submitBtn.disabled = true;
                submitBtn.textContent = 'Running...';
                statusDiv.className = 'status loading';
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '<span class="spinner"></span>Executing daily cycle... This may take 2-3 minutes.';
                
                try {
                    const response = await fetch('/admin/trigger-cycle', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.success) {
                        statusDiv.className = 'status success';
                        let html = '✅ Daily cycle completed successfully!';
                        
                        if (data.results) {
                            const r = data.results;
                            html += '<div class="results">';
                            html += `<div><strong>Status:</strong> ${r.status || 'completed'}</div>`;
                            html += `<div><strong>Bets Placed:</strong> ${r.total_bets_placed || 0}</div>`;
                            html += `<div><strong>Bets Skipped:</strong> ${r.total_bets_skipped || 0}</div>`;
                            html += `<div><strong>Categories:</strong> ${(r.categories_analyzed || []).length}</div>`;
                            
                            if (r.firms_results) {
                                html += '<div style="margin-top:10px"><strong>AI Results:</strong></div>';
                                Object.entries(r.firms_results).forEach(([firm, result]) => {
                                    html += `<div style="margin-left:10px">• ${firm}: ${result.bets_placed || 0} bets</div>`;
                                });
                            }
                            html += '</div>';
                        }
                        
                        statusDiv.innerHTML = html;
                        passwordInput.value = '';
                    } else {
                        statusDiv.className = 'status error';
                        statusDiv.innerHTML = '❌ ' + (data.error || data.message || 'Unknown error');
                    }
                } catch (error) {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '❌ Network error: ' + error.message;
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Run Daily Cycle';
                }
            });

            // Logs viewer functionality
            const viewLogsBtn = document.getElementById('viewLogsBtn');
            const logsViewer = document.getElementById('logsViewer');

            viewLogsBtn.addEventListener('click', async () => {
                const password = passwordInput.value;
                
                if (!password) {
                    alert('Please enter admin password first');
                    return;
                }
                
                viewLogsBtn.disabled = true;
                viewLogsBtn.textContent = 'Loading logs...';
                
                try {
                    const response = await fetch(`/admin/logs?password=${encodeURIComponent(password)}&lines=500`);
                    const data = await response.json();
                    
                    if (response.ok && data.success) {
                        const logs = data.logs;
                        
                        // Apply syntax highlighting
                        const formattedLogs = logs.split('\\n').map(line => {
                            let className = 'log-line';
                            if (line.includes('[ADMIN]')) className += ' log-admin';
                            else if (line.includes('[INFO]')) className += ' log-info';
                            else if (line.includes('[CATEGORY]')) className += ' log-category';
                            else if (line.includes('[BET]')) className += ' log-bet';
                            else if (line.includes('[SKIP]')) className += ' log-skip';
                            else if (line.includes('[ERROR]')) className += ' log-error';
                            else if (line.includes('[WARNING]')) className += ' log-warning';
                            
                            return `<div class="${className}">${line}</div>`;
                        }).join('');
                        
                        logsViewer.innerHTML = formattedLogs || '<div class="log-line">No logs available yet. Run a daily cycle to generate logs.</div>';
                        logsViewer.classList.add('visible');
                        
                        // Scroll to bottom
                        logsViewer.scrollTop = logsViewer.scrollHeight;
                        
                        viewLogsBtn.textContent = 'Refresh Logs';
                    } else {
                        alert('Failed to load logs: ' + (data.error || 'Unknown error'));
                        viewLogsBtn.textContent = 'View Recent Logs (Last 500 lines)';
                    }
                } catch (error) {
                    alert('Network error: ' + error.message);
                    viewLogsBtn.textContent = 'View Recent Logs (Last 500 lines)';
                } finally {
                    viewLogsBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/admin/trigger-cycle', methods=['POST'])
def trigger_cycle():
    """Admin endpoint to manually trigger daily cycle with password protection"""
    import hmac
    
    try:
        data = request.get_json()
        provided_password = data.get('password', '')
        
        # Get admin password from environment
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_password:
            return jsonify({
                'success': False,
                'error': 'Admin password not configured on server'
            }), 500
        
        # Verify password using constant-time comparison
        if not provided_password or not hmac.compare_digest(admin_password, provided_password):
            logger.warning(f"Failed admin login attempt from {request.remote_addr}", prefix="SECURITY")
            return jsonify({
                'success': False,
                'error': 'Invalid password'
            }), 401
        
        # Execute daily cycle (now faster with liquidity filter + 600s timeout)
        logger.admin(f"Daily cycle manually triggered from {request.remote_addr} at {datetime.now().isoformat()}")
        
        # Pass credentials explicitly from startup context where they ARE available
        # to avoid Gunicorn multi-worker environment variable issues
        api_key = os.getenv('OPINION_TRADE_API_KEY')
        private_key = os.getenv('OPINION_WALLET_PRIVATE_KEY')
        
        engine = AutonomousEngine(db, opinion_api_key=api_key, opinion_private_key=private_key)
        results = engine.run_daily_cycle()
        
        # Check if the cycle actually succeeded based on results
        cycle_success = results.get('success', False)
        has_critical_error = results.get('critical_error')
        errors = results.get('errors', [])
        
        if cycle_success:
            logger.admin("Daily cycle completed successfully")
            return jsonify({
                'success': True,
                'message': 'Daily cycle completed successfully',
                'results': results
            }), 200
        else:
            # Cycle failed - return detailed error information
            error_message = has_critical_error or 'Daily cycle failed'
            if errors:
                error_message = f"{error_message}. Errors: {'; '.join(errors[:3])}"  # Show first 3 errors
            
            logger.error(f"Daily cycle failed: {error_message}")
            
            return jsonify({
                'success': False,
                'message': error_message,
                'critical_error': has_critical_error,
                'errors': errors,
                'results': results
            }), 500
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Admin-triggered cycle failed: {str(e)}\n{error_traceback}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Daily cycle execution failed'
        }), 500

@app.route('/admin/logs', methods=['GET'])
def get_admin_logs():
    """
    Admin endpoint to retrieve recent logs from autonomous_cycle.log
    Requires password authentication via query parameter or header
    """
    import hmac
    
    try:
        # Get password from query parameter or Authorization header
        provided_password = request.args.get('password') or request.headers.get('X-Admin-Password', '')
        
        # Get admin password from environment
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_password:
            return jsonify({
                'success': False,
                'error': 'Admin password not configured on server'
            }), 500
        
        # Verify password using constant-time comparison
        if not provided_password or not hmac.compare_digest(admin_password, provided_password):
            logger.warning(f"Failed admin logs access attempt from {request.remote_addr}", prefix="SECURITY")
            return jsonify({
                'success': False,
                'error': 'Invalid password'
            }), 401
        
        # Get number of lines to return (default: 500)
        lines = request.args.get('lines', 500, type=int)
        lines = min(lines, 2000)  # Cap at 2000 lines for performance
        
        # Get recent logs
        recent_logs = logger.get_recent_logs(lines=lines)
        log_file_path = logger.get_log_file_path()
        
        return jsonify({
            'success': True,
            'logs': recent_logs,
            'log_file_path': log_file_path,
            'lines_returned': len(recent_logs.split('\n')),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Admin logs retrieval failed: {str(e)}\n{error_traceback}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve logs'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
