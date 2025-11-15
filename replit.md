# TradingAgents Framework

## ✅ Deployment Status

**Status**: OPERATIONAL on Railway (EU West region)  
**API Access**: Opinion.trade API working correctly from Railway deployment  
**Admin Panel**: Available at `/admin` route for manual cycle triggering

**Recent Updates (Nov 15, 2025)**:
- **CRITICAL BUG FIXES - Production Ready**:
  - **Fix 1: Token ID Extraction** - Extract YES/NO token IDs from market.options during event fetching with defensive parsing
  - **Fix 2: Opinion.trade API Payload** - Complete payload validation (market_id, token_id, side='BUY') eliminates "Missing required fields" errors
  - **Fix 3: Comprehensive Event Analysis Logging** - ALL events (bets + skips) now logged with probability, confidence, 5-area scores (S/N/T/F/V), and decision rationale
  - Token selection logic: probability ≥0.5 → buy YES token, <0.5 → buy NO token
- **Auto-Redeem & OrderMonitor System**:
  - **Auto-redeem**: Automatically calls redeem() when trades win (actual_result=1, profit_loss>0) during reconciliation
  - **OrderMonitor 3-Strike System**: Reviews active orders every 30min via `/api/monitor-orders` endpoint
    - Factor 1: Price manipulation >15%
    - Factor 2: Stagnation >1 week
    - Factor 3: AI contradiction
    - Cancels orders after 3 consecutive strikes, logs all reviews in `cancelled_orders` table
  - **New API Endpoints**: 
    - `GET /api/recent-trades` - Last 20 trades from Opinion.trade
    - `GET /api/ai-trades/<firm_name>` - Trade history for specific AI
    - `GET /api/cancelled-orders` - Cancelled orders with strikes history
    - `POST /api/monitor-orders` - Trigger order monitoring (requires CRON_SECRET, should run every 30min)
- **Frontend Trade History & UI Updates**:
  - **Toggle Sidebar**: BenchmarkPanel has toggle button ("A Better Benchmark" ↔ "Recent Trades") with minHeight:140px to prevent layout shifts
  - Recent trades view integrated directly into BenchmarkPanel with auto-refresh every 30 seconds
  - Expandable leaderboard - click AI to view trade history
  - **LEADERBOARD Visual Improvements**: Summary cards use light background (#F9FAFB) with dark text for better contrast instead of all-black backgrounds
  - **CANCELLED ORDERS**: "How the 3-Strike System Works" box redesigned to white background with 2px black border (removed yellow styling)
  - **Tab Reordering**: BLOG section tabs now ordered as: PREDICTION ANALYSIS → AI DECISIONS → POSITIONS → CANCELLED ORDERS → METHODOLOGY
  - **Consistent Alpha Arena Branding**: All major sections use 2px black borders (#000), balanced use of black headers and light backgrounds for optimal readability
  - Deepseek label color adjusted to #FFF for visibility on black headers
- **Error Handling & Security**:
  - Numeric errno checking (== 10403) for "no trades yet" case eliminates false positives
  - Structured logging via logger.error() for proper observability
  - CRON_SECRET authentication protects POST endpoints
  - All API errors properly surfaced with HTTP 500 status codes
- **Configuration Required**:
  - **CRON_SECRET**: Create this secret in Replit environment variables (e.g., generate random 32-char string)
  - **External Cron Job**: Configure cron-job.org to POST to `/api/monitor-orders` every 30 minutes
    - URL: `https://your-deployment-url.railway.app/api/monitor-orders`
    - Method: POST
    - Header: `X-Cron-Secret: <your-CRON_SECRET-value>`
    - Schedule: Every 30 minutes (*/30 * * * *)
- **Centralized Logging System**: Implemented comprehensive logging infrastructure
  - All autonomous engine events logged to `logs/autonomous_cycle.log` (10MB rotation, 5 backups)
  - Password-protected `/admin/logs` endpoint for log viewing
  - Admin panel logs viewer with syntax highlighting
  - Configurable log levels via `LOG_LEVEL` env var (default: INFO)
- Event categorization system detects Rates, Commodities, Inflation, Employment, Finance categories via keyword matching
- Sports category filtering active (excluded from analysis)
- Enhanced keyword matching for accurate event classification

## Overview
This project is a multi-LLM prediction market framework where five AI prediction agents (ChatGPT, Gemini, Qwen, Deepseek, Grok) autonomously compete on Opinion.trade. The system tracks performance, maintains virtual portfolios, and employs a sophisticated prompt system simulating a 7-role internal decision-making process for each LLM. The framework supports continuous adaptation of AI strategies based on performance, aiming for ongoing improvement in financial market prediction.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses **React/Next.js** (TypeScript + Tailwind CSS) for a single-page interface that replicates the **Alpha Arena (Nof1.ai) design aesthetic**, characterized by **BLACK BORDERS (2px solid #000)** around all major components. It includes a market header, horizontal navigation, a 75/25 layout on the LIVE page, and a leaderboard table. The Next.js frontend runs on port 5000.

### Backend Architecture
The backend employs a two-layer architecture:
1.  **Flask REST API** (port 8000): Provides 8 endpoints for frontend data consumption, including real-time crypto prices, AI performance metrics, and leaderboard data.
2.  **Python Backend Services**: A modular design encompassing:
    *   **`TradingDatabase`**: SQLite-based persistence for predictions, firm performance, and virtual portfolios.
    *   **`FirmOrchestrator`**: Manages LLM clients and prediction generation.
    *   **Data Collectors**: Specialized classes for technical, fundamental, sentiment, and volatility data.
    *   **Prompt System**: Generates structured prompts for LLMs.
    *   **`RecommendationEngine`**: Analyzes historical performance.
    *   **`OpinionTradeAPI`**: Handles automated prediction submission.
    *   **`Autonomous Engine`**: Orchestrates daily prediction cycles, event analysis, and risk-aware betting.
    *   **`Risk Management System`**: Multi-level adaptive system with profit/loss thresholds, daily loss, and category exposure limits.
    *   **`Bankroll Management`**: Assigns diverse betting strategies (e.g., Kelly Criterion, Martingale) to each AI.
    *   **`Learning System`**: Provides continuous improvement through performance analysis and pattern recognition.
    *   **`daily_watchdog.py`**: Daily maintenance system for counter resets and system health checks.
    *   **`reconciliation.py`**: Balance reconciliation engine (local DB vs Opinion.trade API).

### LLM Integration Architecture
A multi-provider approach supports various LLM APIs (OpenAI, Google Gemini, Qwen, Deepseek, Grok) with built-in rate limiting and cost tracking.

### Data Collection Architecture
The system uses a 5-Area Analysis Framework where each AI analyzes events through 5 mandatory data sources with transparent scoring:
*   **`AlphaVantageCollector`**: Technical indicators.
*   **`NewsCollector`**: Financial news and sentiment.
*   **`VolatilityCollector`**: Historical volatility and ATR.
*   **`YFinanceCollector`**: Fundamental data.
*   **`RedditSentimentCollector`**: Social media sentiment analysis.
API calls are optimized with a shared caching layer to reduce redundant requests.

### Data Storage
An embedded SQLite database stores `predictions`, `firm_performance`, `virtual_portfolio`, `autonomous_bets`, `autonomous_cycles`, `strategy_adaptations`, and `daily_bet_tracking`.

### Visualization Layer
**Frontend**: Recharts (React) for interactive charts.

## External Dependencies

### LLM APIs
*   OpenAI (ChatGPT)
*   Google Gemini
*   Qwen
*   Deepseek
*   Grok (XAI)

### Financial Data APIs
*   Alpha Vantage
*   Yahoo Finance

### Social Media Data
*   Reddit API (PRAW)

### Python Libraries (Backend)
*   `flask`, `flask-cors`
*   `pandas`, `yfinance`
*   `praw`, `nltk`
*   `tenacity`
*   `sqlite3`
*   `openai`, `google-genai`
*   `opinion-clob-sdk`, `eth-account`

### JavaScript Libraries (Frontend)
*   `next`, `react`, `react-dom`
*   `recharts`
*   `tailwindcss`
*   `typescript`

### Environment Variables Required
*   `AI_INTEGRATIONS_OPENAI_API_KEY`
*   `AI_INTEGRATIONS_OPENAI_BASE_URL`
*   `ALPHA_VANTAGE_API_KEY`
*   `REDDIT_CLIENT_ID`
*   `REDDIT_CLIENT_SECRET`
*   `OPINION_TRADE_API_KEY`
*   `DEEPSEEK_API_KEY`
*   `QWEN_API_KEY`
*   `XAI_API_KEY`
*   `ADMIN_PASSWORD`
*   `BANKROLL_MODE`
*   `OPINION_WALLET_PRIVATE_KEY`