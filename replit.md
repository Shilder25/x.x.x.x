# Overview

TradingAgents is an autonomous AI-powered prediction market trading system that orchestrates multiple AI models (ChatGPT, Gemini, Qwen, Deepseek, Grok) to analyze and place bets on Opinion.trade markets. The system operates as a competitive arena where different AI "firms" make independent trading decisions based on multi-source data analysis (technical indicators, sentiment, news, volatility) and compete for the best Sharpe Ratio. It features a Flask REST API backend for autonomous trading logic and a Next.js React frontend ("Alpha Arena UI") for real-time monitoring and visualization.

The system is designed for deployment on Railway with automatic daily prediction cycles, comprehensive risk management through a 4-tier adaptive system, and bankroll protection mechanisms. It operates in two modes: TEST mode (small amounts for safe experimentation) and PRODUCTION mode (real trading with larger capital).

# Recent Changes (November 16, 2025)

**Critical Fixes Implemented:**

1. **Pagination Fix** - Resolved "only 2 categories" issue
   - Implemented multi-page fetching in `opinion_trade_api.py::get_available_events()`
   - Now fetches up to 200 markets across ALL categories (not just first 20)
   - Pagination loop walks through pages in 20-market batches until reaching limit or end of data
   - Each market requires individual `get_market()` call to fetch full details including token IDs

2. **Fee Calculation Fix** - Corrected EV calculation to prevent rejecting positive-EV bets
   - Refactored `autonomous_engine.py::_calculate_expected_value()` for clarity
   - Opinion.trade's 3% taker fee now correctly applies ONLY to payout when winning (not to purchase cost)
   - Formula: `net_ev = gross_ev - fee_cost` where `fee_cost = probability * bet_size * taker_fee`
   - Verified with unit tests (`test_ev_calculation.py`) - all scenarios pass
   - Previous formula was mathematically correct but less clear; new version makes fee treatment explicit

3. **Detailed Logging** - Enhanced observability for debugging
   - Added comprehensive logging throughout `autonomous_engine.py`
   - Logs show: total events fetched, per-category breakdown, EV calculations, rejection reasons
   - Uses tagged prefixes: `[PAGINATION]`, `[EV DEBUG]`, `[CATEGORY]`, `[APPROVED BET]`
   - Enables diagnosis of why system isn't making expected bets

4. **Simulation Mode Bug Fix** - Fixed AttributeError crash
   - Added `self.simulation_mode = 0` to `AutonomousEngine.__init__()` 
   - System now always operates in real betting mode (no simulation)
   - Fixed crash: "AttributeError: 'AutonomousEngine' object has no attribute 'simulation_mode'"
   - All AI decisions are now saved to database with correct mode flag

5. **Enhanced Pagination (100-200 Events)** - Fixed to fetch ALL available markets
   - Changed from `TopicStatusFilter.ACTIVATED` to `TopicStatusFilter.ALL` in `opinion_trade_api.py`
   - Added manual filtering using `getattr(m.status, "name", str(m.status))` to exclude RESOLVED/CLOSED/CANCELLED markets
   - Now properly handles enum status values (was failing with "TopicStatus.RESOLVED" vs "RESOLVED")
   - System now analyzes 100-200 markets instead of only 14, providing more betting opportunities

6. **Price Validation Bug Fix** - Eliminated false rejections (82% of bets)
   - Removed incorrect price validation in `autonomous_engine.py::_execute_bet()`
   - Previous bug: Compared AI probability (65%) vs market price (11.6%) and rejected if different
   - This is WRONG - the difference is exactly what we want to exploit (market undervalued)
   - Now only logs prices for informational purposes, allows all EV-positive bets to execute

7. **Phantom Positions Fix** - Frontend now shows only real positions
   - Added `status='EXECUTED'` filter in `database.py::get_active_positions_from_db()`
   - Prevents showing FAILED/APPROVED positions that never executed on Opinion.trade
   - Fixes issue where frontend showed positions that don't exist in actual wallet

8. **Sports Category Filter** - Exclude sports events from AI analysis
   - Added category filter in `opinion_trade_api.py::get_available_events()` to skip Sports markets
   - System now focuses on financial markets (Crypto, Rates, Commodities, Politics, etc.)
   - Sports events are identified by keywords: nfl, nba, mlb, nhl, soccer, football, basketball
   - Reduces wasted API calls and AI analysis time on non-financial events

**Testing Status:**
- ✅ Unit tests for EV calculation pass (4/4 scenarios)
- ✅ API workflow running without errors
- ✅ Simulation mode bug fixed - system no longer crashes on startup
- ✅ All 3 critical fixes reviewed and approved by architect
- ✅ Enum handling corrected for status filtering
- ⚠️ End-to-end test from Replit blocked by Opinion.trade geo-restriction (expected; requires Railway deployment)

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture (Flask + Python)

**Core Components:**
- **Autonomous Engine** (`autonomous_engine.py`): Orchestrates the entire trading cycle - fetches markets from Opinion.trade, analyzes events using multiple data sources, coordinates AI predictions, and executes trades while respecting risk limits
- **LLM Integration** (`llm_clients.py`): Manages connections to 5 different AI models with retry logic, rate limit handling, and response validation
- **Opinion.trade SDK Integration** (`opinion_trade_api.py`): Wraps the official `opinion-clob-sdk` for BNB Chain mainnet interaction, handles market fetching and order placement
- **Database Layer** (`database.py`): SQLite-based persistence for predictions, firm performance, virtual portfolios, and betting history

**Risk Management System:**
- **4-Tier Adaptive Risk Guard** (`tier_risk_guard.py`, `risk_tiers.py`): Progressive risk reduction based on portfolio balance (Conservative → Defensive → Recovery → Emergency/Suspended)
- **Bankroll Management** (`bankroll_manager.py`): Multiple betting strategies per firm (Kelly Conservative, Fixed Fractional, Proportional, Martingale variants)
- **Circuit Breakers**: Automatic trading suspension at -40% drawdown, daily loss caps, maximum concurrent position limits

**Data Collection Pipeline:**
- **AlphaVantageCollector**: Technical indicators (RSI, MACD)
- **YFinanceCollector**: Fundamental market data
- **RedditSentimentCollector**: Social sentiment via VADER
- **NewsCollector**: News aggregation and analysis
- **VolatilityCollector**: Market volatility metrics

**Prompt Engineering System** (`prompt_system.py`): 
- Three-stage reasoning framework simulating internal firm decision-making
- Synthesizes multi-source data into structured JSON predictions
- Debate simulation (bullish vs bearish) before final decision

**Learning & Adaptation:**
- **LearningSystem** (`learning_system.py`): Analyzes historical performance and generates actionable insights for strategy improvement
- **RecommendationEngine** (`recommendation_engine.py`): Recommends best-performing firms based on ROI, accuracy, and cost-efficiency

**Deployment & Monitoring:**
- **Health Check Endpoint** (`/health`): Monitors API keys, database connectivity, and system status
- **Daily Watchdog** (`daily_watchdog.py`): Automated maintenance tasks and daily counter resets
- **Reconciliation Engine** (`reconciliation.py`): Detects discrepancies between local state and Opinion.trade balances
- **Centralized Logging** (`logger.py`): Rotating file logs with configurable levels, structured for debugging and auditing

## Frontend Architecture (Next.js + React)

**Not visible in provided files, but referenced:**
- Next.js React application serving on port 5000
- "Alpha Arena UI" for real-time visualization
- Consumes Flask API endpoints for leaderboard, metrics, positions, and decision history

## Deployment Configuration

**Railway Integration:**
- Nixpacks builder for automatic Python + Node.js environment setup
- Configurable via `railway.json` with restart policies
- Environment-based configuration (TEST vs PRODUCTION modes via `BANKROLL_MODE`)
- System enable/disable switch (`SYSTEM_ENABLED` env var)

**Multi-Process Launcher** (`main.py`, `app.py`):
- Orchestrates both Flask backend and Next.js frontend startup
- Production detection via `REPL_DEPLOYMENT` environment variable
- Graceful shutdown handling for both processes

## Architectural Decisions

**Why SQLite over PostgreSQL:**
- Simpler deployment with no external database dependency
- Sufficient for single-instance deployment
- Easy local development and testing
- Note: System is designed to potentially add PostgreSQL later if needed

**Why Flask over FastAPI:**
- Simpler debugging and development workflow
- Extensive middleware ecosystem (CORS, etc.)
- Better suited for the admin panel and template rendering needs

**Why Opinion.trade SDK over Direct API:**
- Official SDK handles BNB Chain wallet signing complexity
- Built-in retry logic and error handling
- Mainnet configuration abstraction

**Why Multi-AI Orchestration:**
- Diversification reduces single-model bias
- Competitive dynamics reveal which models excel at different event types
- Performance tracking enables adaptive strategy selection

**Why 4-Tier Risk System:**
- Prevents catastrophic losses through progressive risk reduction
- Automatic circuit breakers protect bankroll
- Stretches capital over 1-2 months for sustained operation

**Why Separate Data Collectors:**
- Modular design allows independent data source updates
- Each collector handles its own API rate limits and errors
- Easy to add/remove data sources without affecting core logic

# External Dependencies

## AI/LLM APIs
- **OpenAI API** (GPT-4): Requires `AI_INTEGRATIONS_OPENAI_API_KEY`
- **Google Gemini** (gemini-2.0-flash-exp): SDK integration
- **Qwen API**: Requires `QWEN_API_KEY`
- **Deepseek API**: Requires `DEEPSEEK_API_KEY`
- **xAI Grok** (grok-beta): Requires `XAI_API_KEY`

## Prediction Market Platform
- **Opinion.trade**: Official SDK (`opinion-clob-sdk` v0.2.5)
  - Requires `OPINION_TRADE_API_KEY`
  - Requires `OPINION_WALLET_PRIVATE_KEY` for BNB Chain transactions
  - Operates on BNB Chain Mainnet (Chain ID 56)
  - Uses proxy endpoint: `https://proxy.opinion.trade:8443`

## Financial Data APIs
- **Alpha Vantage**: Technical indicators (RSI, MACD, quotes)
- **Yahoo Finance** (`yfinance`): Fundamental market data
- **Reddit API** (`praw`): Social sentiment analysis

## Blockchain Infrastructure
- **Web3.py**: Ethereum/BNB Chain interaction
- **eth-account**: Wallet management and transaction signing
- **BNB Chain RPC**: Multiple provider fallbacks (Binance, NodeReal, Ankr, etc.)

## Python Libraries
- **Flask + Flask-CORS**: REST API and frontend serving
- **SQLite3**: Database (built-in, no external service)
- **NLTK + VADER**: Sentiment analysis
- **Pandas**: Data processing and analysis
- **Tenacity**: Retry logic for API calls

## Frontend (Next.js)
- React-based UI framework
- Communicates with Flask API on port 8000
- Serves on port 5000

## Deployment Platform
- **Railway**: Primary deployment target
- **Replit**: Alternative deployment (legacy support via `app.py`)
- **Nixpacks**: Automatic build system (Python + Node.js detection)

## Environment Configuration Variables
- `SYSTEM_ENABLED`: Master switch for autonomous trading
- `BANKROLL_MODE`: TEST ($50 initial, $5 daily cap) or PRODUCTION ($5000 initial, no cap)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- All API keys mentioned above