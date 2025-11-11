# TradingAgents Framework

## ⚠️ Known Issue: Opinion.trade API Geo-Blocking

**Status**: BLOCKED - Requires whitelist from Opinion.trade  
**Error**: API error 10403 "Invalid area"  
**Impact**: System is 90% complete. All components work except Opinion.trade API access.

**Solution Required**:
- Contact Opinion.trade support to whitelist Railway deployment IPs
- See `PROBLEMA_OPINION_TRADE_GEO_BLOCK.md` for detailed instructions
- Run `python health_check_opinion_trade.py` to verify when access is restored

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