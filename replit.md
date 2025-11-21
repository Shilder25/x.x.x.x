# Overview

TradingAgents is an autonomous AI-powered prediction market trading system designed for the Opinion.trade platform. It orchestrates multiple AI models (ChatGPT, Gemini, Qwen, Deepseek, Grok) to analyze markets and place bets. The system features a competitive "Alpha Arena" where different AI "firms" make independent trading decisions based on multi-source data analysis (technical indicators, sentiment, news, volatility) and compete for the best Sharpe Ratio. It includes a Flask REST API backend for trading logic and a Next.js React frontend for real-time monitoring. The system supports deployment on Railway, includes automatic daily prediction cycles, comprehensive 4-tier adaptive risk management, and bankroll protection.

**Recent Memory Optimizations (Nov 21, 2025):** Sequential agent execution with garbage collection after each AI firm to prevent Railway out-of-memory crashes during daily cycles. Progress logging ([1/5], [2/5], etc.) added to identify which AI firm causes OOM if it occurs. Cache intentionally preserved across firms to reuse expensive collector data (technical, news, sentiment).

**Gunicorn Timeout Fix (Nov 21, 2025):** Increased Gunicorn timeouts to 900s (15 minutes) with graceful-timeout to allow daily cycle with 5 AI agents to complete without worker timeouts.

**Portfolio Initialization (Nov 21, 2025):** Created `/admin/initialize-portfolios` endpoint to initialize portfolios for all 5 AI agents. This endpoint must be run after database resets to create initial portfolios ($50 balance in TEST mode) for ChatGPT, Gemini, Qwen, Deepseek, and Grok.

**Database Thread-Safety Fix (Nov 21, 2025):** ✓ COMPLETED - Refactored ALL 25+ database methods in `database.py` to use re-entrant context manager pattern (`with self.get_connection() as conn:`) with automatic transaction management. The context manager now:
- Uses thread-local connections (one per Gunicorn worker)
- Tracks transaction depth to support nested method calls (e.g., save_prediction → update_firm_stats)
- Begins transaction explicitly with `BEGIN` only at outermost level (depth 0)
- Auto-commits on success at outermost level
- Auto-rolls back on any exception to prevent database locks (unwinds entire transaction)
- Uses WAL mode for better concurrency
- Removed all 17 explicit `conn.commit()` calls from methods
Fixed all indentation and syntax errors. This resolves "Cannot operate on a closed database", "database is locked", and "cannot start a transaction within a transaction" errors during concurrent bet execution. System now runs stably in production with 2 Gunicorn workers.

**Minimum Bet Amount Fix (Nov 21, 2025):** Increased minimum bet from $1.00 to $1.50 USDT in `opinion_trade_api.py` and `risk_management.py` to meet Opinion.trade's minimum requirement of $1.30 USDT.

**Frontend-Backend Connection Fix (Nov 21, 2025):** ✓ COMPLETED - Fixed Next.js frontend not communicating with Flask backend in Railway deployment. Updated `next.config.mjs` to use internal rewrites (`localhost:8000`) and `frontend/lib/config.ts` to use relative API paths. This allows the frontend (port 5000) to proxy API requests internally to Flask (port 8000) within the same Railway container. Verified working - all API endpoints responding with HTTP 200.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture (Flask + Python)

**Core Components:**
- **Autonomous Engine**: Orchestrates market fetching, multi-source data analysis, AI prediction coordination, and trade execution within risk limits.
- **LLM Integration**: Manages connections to five different AI models with robust retry logic, rate limit handling, and response validation.
- **Opinion.trade SDK Integration**: Wraps the official `opinion-clob-sdk` for BNB Chain mainnet interaction, handling market data retrieval and order placement.
- **Database Layer**: SQLite-based persistence for predictions, firm performance, virtual portfolios, and betting history.

**Risk Management System:**
- **4-Tier Adaptive Risk Guard**: Implements progressive risk reduction based on portfolio balance (Conservative → Defensive → Recovery → Emergency/Suspended).
- **Bankroll Management**: Supports multiple betting strategies per firm (e.g., Kelly Conservative, Fixed Fractional).
- **Circuit Breakers**: Features automatic trading suspension at specified drawdown levels, daily loss caps, and maximum concurrent position limits.

**Data Collection Pipeline:**
- Modular collectors for technical indicators, fundamental market data, social sentiment, news aggregation, and market volatility.

**Prompt Engineering System:**
- Utilizes a three-stage reasoning framework to simulate internal firm decision-making, synthesizing multi-source data into structured JSON predictions, and incorporating debate simulation.

**Learning & Adaptation:**
- **LearningSystem**: Analyzes historical performance for strategy improvement.
- **RecommendationEngine**: Recommends top-performing firms based on ROI, accuracy, and cost-efficiency.

**Deployment & Monitoring:**
- **Health Check Endpoint**: Monitors API keys, database, and system status.
- **Daily Watchdog**: Manages automated maintenance and daily counter resets.
- **Reconciliation Engine**: Detects discrepancies between local state and Opinion.trade balances.
- **Centralized Logging**: Provides structured logging for debugging and auditing.

## Frontend Architecture (Next.js + React)

- The "Alpha Arena UI" is a Next.js React application providing real-time monitoring and visualization of trading activities, consuming data from the Flask API.

## Deployment Configuration

- **Railway Integration**: Utilizes Nixpacks for automatic environment setup and is configurable via `railway.json` for deployment and restart policies, supporting `TEST` and `PRODUCTION` modes.
- **Multi-Process Launcher**: `main.py` orchestrates the startup of both Flask backend and Next.js frontend.

## Architectural Decisions

- **SQLite**: Chosen for simpler deployment and local development.
- **Flask**: Selected for ease of debugging, development, and its middleware ecosystem.
- **Opinion.trade SDK**: Used for handling BNB Chain wallet signing, built-in retry logic, and error handling.
- **Multi-AI Orchestration**: Diversifies predictions and identifies optimal models for various event types.
- **4-Tier Risk System**: Prevents significant losses through progressive risk reduction and automatic circuit breakers.
- **Separate Data Collectors**: Ensures modularity, independent updates, and fault isolation for various data sources.

# External Dependencies

## AI/LLM APIs
- **OpenAI API**: GPT-4.
- **Google Gemini**: gemini-2.0-flash-exp.
- **Qwen API**.
- **Deepseek API**.
- **xAI Grok**: grok-beta.

## Prediction Market Platform
- **Opinion.trade**: Official `opinion-clob-sdk` (v0.2.5) for BNB Chain Mainnet interaction.

## Financial Data APIs
- **Alpha Vantage**: Technical indicators.
- **Yahoo Finance** (`yfinance`): Fundamental market data.
- **Reddit API** (`praw`): Social sentiment analysis.

## Blockchain Infrastructure
- **Web3.py**: Ethereum/BNB Chain interaction.
- **eth-account**: Wallet management and transaction signing.
- **BNB Chain RPC**: Multiple provider fallbacks.

## Python Libraries
- **Flask + Flask-CORS**: REST API.
- **SQLite3**: Embedded database.
- **NLTK + VADER**: Sentiment analysis.
- **Pandas**: Data processing.
- **Tenacity**: Retry logic.

## Frontend (Next.js)
- React-based UI framework.

## Deployment Platform
- **Railway**: Primary deployment target.
- **Nixpacks**: Automatic build system.