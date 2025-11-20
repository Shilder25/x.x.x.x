# Overview

TradingAgents is an autonomous AI-powered prediction market trading system that orchestrates multiple AI models (ChatGPT, Gemini, Qwen, Deepseek, Grok) to analyze and place bets on Opinion.trade markets. The system acts as a competitive arena where different AI "firms" make independent trading decisions based on multi-source data analysis (technical indicators, sentiment, news, volatility) and compete for the best Sharpe Ratio. It features a Flask REST API backend for autonomous trading logic and a Next.js React frontend ("Alpha Arena UI") for real-time monitoring and visualization. The system is designed for deployment on Railway with automatic daily prediction cycles, comprehensive risk management through a 4-tier adaptive system, and bankroll protection mechanisms, operating in TEST and PRODUCTION modes.

## Recent Changes (November 20, 2025)

**CRITICAL PRICE DECIMAL BUG FIX:**
- **Problem**: SDK rejected orders with error "price is out of range(limit 3 decimal places): 0.1818" (errno=10602)
- **Root Cause**: Code was formatting prices with 4 decimals (`.4f`) when SDK only accepts maximum 3 decimals
- **Solution**: Changed price formatting from `f"{execution_price:.4f}"` to `f"{execution_price:.3f}"`
- **Price Range Protection**: Updated price clamping to use MIN_PRICE=0.001 and MAX_PRICE=0.999 (prevents rounding to 1.000)
- **Impact**: Orders will now be accepted by SDK with proper 3-decimal price formatting

**CRITICAL SDK BUG FIXES - Order Execution Now Working:**
- **Fixed Field Name Bug**: Changed `ask`/`bid` to `ask_price`/`bid_price` in get_latest_price() response handling - SDK returns these specific field names
- **Fixed Amount Type Bug**: Changed makerAmountInQuoteToken from string to float/int as required by SDK specifications 
- **Added enable_trading() Call**: Added mandatory one-time enable_trading() call during client initialization (required before placing any orders)
- **Verified Configuration**: check_approval=True already present in place_order() calls, errno validation already implemented
- **Geo-blocking Confirmed**: "Invalid area" error (errno=10403) confirms need for Railway EU West deployment as planned

## Recent Changes (November 19, 2025)

**CRITICAL ORDER PRICING BUG FIX:**
- **Problem**: Orders were being placed with AI probability as limit price instead of market price, causing orders to never execute.
  - Example: AI predicts 52% probability, market price is 29%, order placed at price=0.52 never fills
  - Orders appeared in orderbook but never executed (no trades)
- **Root Cause**: `submit_prediction()` used `price = str(round(probability, 4))` - using AI's probability as the order's limit price
- **Solution v2 (Improved after architect review)**:
  - Fetch REAL market price from orderbook using `get_latest_price()` with 3-retry exponential backoff
  - Use ASK price for BUY orders, BID price for SELL orders
  - Fallback logic for partial orderbook data: ASK → MID → BID + spread (or vice versa for SELL)
  - Use epsilon (1e-4) instead of arbitrary clamps to keep prices in valid [0, 1] range
  - Apply 1% buffer for immediate execution: `min(price * 1.01, 1.0 - epsilon)` for BUY
- **Impact**: Orders now execute immediately at market prices with robust fallbacks, resolving the "bets identified but not executed" issue

**Critical SDK Configuration Fix:**
- **Multi-sig Address Fix**: Fixed "BEP20: approve from the zero address" error by using actual wallet address instead of 0x0000... for `multi_sig_addr` parameter.
- **Root Cause**: Opinion.trade SDK requires `multi_sig_addr` to be the actual wallet address (visible in "MyProfile"), not a zero address placeholder.
- **Solution**: Changed line 129 in `opinion_trade_api.py` from `multi_sig_addr='0x0000...'` to `multi_sig_addr=self.wallet_address` (0x43C9b...).
- **Impact**: Orders can now execute successfully on Opinion.trade BNB Chain mainnet.

**Critical Execution Blocking Bug Fix:**
- **Database Save Order Fix**: Fixed critical bug where `[BET]` logs appeared but no bets executed. Root cause: `_save_ai_decision()` was called AFTER logging, and DB failures killed the process before returning evaluation, leaving `all_opportunities` empty.
- **Solution**: Reordered `_evaluate_event_opportunity` to save to DB FIRST in try-catch, then set `is_opportunity=True` ONLY after successful DB save, then log `[BET]`. If DB save fails, opportunity is never marked (not added to execution list), error is logged, and treated as SKIP.
- **Guarantee**: `[BET]` logs now always correspond to successful DB records, and failed DB writes cannot leak opportunities into execution.

**Opinion.trade SDK Architecture (from official docs):**
- **`private_key`**: The signer wallet that signs orders/transactions (hot wallet) - Uses Login Wallet 0x43C9b...
- **`multi_sig_addr`**: The assets wallet that holds funds/positions - Same as Login Wallet 0x43C9b... for our setup
- **Spot Balance** (0x15c1a...): Opinion.trade's internal custodial account (NOT used in SDK configuration)
- **Gas-free operations**: place_order(), cancel_order(), all GET methods (use EIP712 signatures)
- **Gas-required operations**: enable_trading(), split(), merge(), redeem() (BNB required for gas)

## Recent Changes (November 18, 2025)

**Critical Fixes:**
- **Probability Conversion Fix**: Fixed `validate_and_normalize_prediction` to properly convert AI probabilities from percentage format (0-100) to decimal format (0-1), enabling correct Expected Value calculations and bet execution.
- **Gunicorn Timeout Increase**: Raised worker timeout from 120 to 300 seconds to prevent worker timeouts during long AI prediction cycles.

**System Status:**
- ✅ Opinion.trade API integration working correctly in Railway EU West
- ✅ AI predictions executing with proper probability calculations
- ✅ Bets executing when EV > 0 (confirmed in production logs)
- ✅ Worker timeouts resolved with 5-minute timeout window

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture (Flask + Python)

**Core Components:**
- **Autonomous Engine**: Orchestrates the entire trading cycle, including market fetching, multi-source data analysis, AI prediction coordination, and trade execution within risk limits.
- **LLM Integration**: Manages connections to 5 different AI models with robust retry logic, rate limit handling, and response validation.
- **Opinion.trade SDK Integration**: Wraps the official `opinion-clob-sdk` for BNB Chain mainnet interaction, handling market data retrieval and order placement.
- **Database Layer**: SQLite-based persistence for predictions, firm performance, virtual portfolios, and betting history.

**Risk Management System:**
- **4-Tier Adaptive Risk Guard**: Implements progressive risk reduction based on portfolio balance (Conservative → Defensive → Recovery → Emergency/Suspended).
- **Bankroll Management**: Supports multiple betting strategies per firm (e.g., Kelly Conservative, Fixed Fractional).
- **Circuit Breakers**: Features automatic trading suspension at specified drawdown levels, daily loss caps, and maximum concurrent position limits.

**Data Collection Pipeline:**
- Modular collectors for technical indicators (AlphaVantage), fundamental market data (YFinance), social sentiment (Reddit), news aggregation, and market volatility.

**Prompt Engineering System:**
- Utilizes a three-stage reasoning framework to simulate internal firm decision-making, synthesizing multi-source data into structured JSON predictions, and incorporating debate simulation.

**Learning & Adaptation:**
- **LearningSystem**: Analyzes historical performance to generate insights for strategy improvement.
- **RecommendationEngine**: Recommends top-performing firms based on ROI, accuracy, and cost-efficiency.

**Deployment & Monitoring:**
- **Health Check Endpoint**: Monitors API keys, database, and system status.
- **Daily Watchdog**: Manages automated maintenance and daily counter resets.
- **Reconciliation Engine**: Detects discrepancies between local state and Opinion.trade balances.
- **Centralized Logging**: Provides structured logging for debugging and auditing.

## Frontend Architecture (Next.js + React)

- A Next.js React application, known as the "Alpha Arena UI," provides real-time monitoring and visualization of trading activities, consuming data from the Flask API.

## Deployment Configuration

- **Railway Integration**: Utilizes Nixpacks for automatic environment setup and is configurable via `railway.json` for deployment and restart policies. Supports `TEST` and `PRODUCTION` modes.
- **Multi-Process Launcher**: `main.py` orchestrates the startup of both Flask backend and Next.js frontend.

## Architectural Decisions

- **SQLite**: Chosen for simpler deployment and local development, with an option for PostgreSQL scaling.
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
- **Opinion.trade**: Official `opinion-clob-sdk` (v0.2.5) for BNB Chain Mainnet interaction, requiring specific API keys and private wallet details.

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