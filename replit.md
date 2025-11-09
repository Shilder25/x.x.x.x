# TradingAgents Framework

## Overview
This project is a multi-LLM prediction market framework where five AI prediction agents (ChatGPT, Gemini, Qwen, Deepseek, Grok) autonomously compete on Opinion.trade (BNB Chain). Each agent analyzes financial market events using technical indicators, fundamental data, and sentiment analysis to generate probabilistic predictions for binary outcomes. The system tracks performance, maintains virtual portfolios, and includes a sophisticated prompt system simulating a 7-role internal decision-making process for each LLM. The framework supports continuous adaptation of AI strategies based on performance, aiming for ongoing improvement.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses **React/Next.js** (TypeScript + Tailwind CSS) for a professional single-page interface that exactly replicates the **Alpha Arena (Nof1.ai) design aesthetic**.

**Design System - Alpha Arena BLACK BORDERS:**
- **Defining Characteristic**: BLACK BORDERS (2px solid #000) around ALL major components
  - Typography: Inter (body text, headings), monospace (numbers)
  - Market header with crypto prices and percentage changes
  - Navigation: Horizontal tabs (LIVE | LEADERBOARD | BLOG | MODELS) with separators
  - Layout: 75/25 split on LIVE page (chart left, info panels right)
  - Table borders: Black borders on all cells in leaderboard
  - Chart: Vibrant color-coded lines (Purple/Blue/Orange/Black/Cyan)
- **Port Configuration**: Next.js runs on port 5000 (webview)
- **System Control**: No admin controls on page - controlled via SYSTEM_ENABLED in Replit Secrets

### Backend Architecture
**Two-Layer Architecture:**
1. **Flask REST API** (port 8000): Exposes 8 endpoints for frontend data consumption
   - `/api/market-header` - Real-time crypto prices
   - `/api/live-metrics` - Current AI performance metrics
   - `/api/live-chart-history` - Historical account values
   - `/api/leaderboard` - Full ranking table
   - `/api/blog` - Information content
   - `/api/models/<firm>` - Individual AI details
   - `/api/competition-status` - System status

2. **Python Backend Services**: Modular design with key components:
- **`TradingDatabase`**: SQLite-based persistence layer for predictions, firm performance, and virtual portfolios with automatic schema migration.
- **`FirmOrchestrator`**: Manages LLM clients and prediction generation.
- **Data Collectors**: Specialized classes for technical, fundamental, and sentiment data.
- **Prompt System**: Generates structured prompts simulating a 7-role decision-making process.
- **`RecommendationEngine`**: Analyzes historical performance for prediction recommendations.
- **`OpinionTradeAPI`**: Handles automated prediction submission.
- **`Autonomous Engine`**: Orchestrates daily prediction cycles, including event analysis, risk-aware betting, and simulation/real mode toggling. It now analyzes events across all Opinion.trade categories.
- **`Risk Management System`**: A multi-level adaptive system that adjusts strategies based on profit/loss thresholds and includes safety features like daily loss and category exposure limits.
- **`Bankroll Management`**: Assigns diverse betting strategies (Kelly Criterion, Modified Martingale, Fixed Fractional, Proportional, Anti-Martingale) to each AI.
- **`Learning System`**: Provides continuous improvement through weekly performance analysis, pattern recognition, and EV accuracy assessment.

### LLM Integration Architecture
A multi-provider approach supports various LLM APIs (OpenAI, Google Gemini, Qwen, Deepseek, Grok) with built-in rate limiting and cost tracking.

### Data Collection Architecture
A multi-source strategy utilizes `AlphaVantageCollector` for technical indicators, `YFinanceCollector` for fundamental data, and `RedditSentimentCollector` for social sentiment analysis.

### Data Storage
An embedded SQLite database stores `predictions`, `firm_performance`, `virtual_portfolio`, `autonomous_bets`, `autonomous_cycles`, and `strategy_adaptations`.

### Visualization Layer
**Frontend**: Recharts (React) for interactive charts with white backgrounds and clean styling
**Legacy**: Plotly support maintained in Python backend for potential future use

## External Dependencies

### LLM APIs
- OpenAI (ChatGPT)
- Google Gemini
- Qwen
- Deepseek
- Grok (XAI)

### Financial Data APIs
- Alpha Vantage
- Yahoo Finance

### Social Media Data
- Reddit API (PRAW)

### Python Libraries (Backend)
- `flask`, `flask-cors` - REST API server
- `pandas`, `plotly`, `yfinance` - Data processing & financial data
- `praw`, `nltk` - Social sentiment analysis
- `tenacity` - Retry logic
- `sqlite3` - Database
- `openai`, `google-genai` - LLM integrations

### JavaScript Libraries (Frontend)
- `next` (15.5.6) - React framework
- `react` (19.0.0), `react-dom` - UI library
- `recharts` - Chart visualization
- `tailwindcss` - CSS framework
- `typescript` - Type safety

### Environment Variables Required
- `AI_INTEGRATIONS_OPENAI_API_KEY`
- `AI_INTEGRATIONS_OPENAI_BASE_URL`
- `ALPHA_VANTAGE_API_KEY`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `OPINION_TRADE_API_KEY`
- `DEEPSEEK_API_KEY`
- `QWEN_API_KEY`
- `XAI_API_KEY`
- `ADMIN_PASSWORD`

## Recent Changes (November 9, 2025)

**MAJOR MIGRATION: Streamlit → React/Next.js (Latest):**
- **Reason**: Streamlit could not render custom CSS properly - HTML was showing as text instead of rendering the Alpha Arena design
- **Solution**: Complete migration to React/Next.js with full CSS control
- **Architecture Change**:
  - Separated concerns: Flask REST API backend (port 8000) + Next.js frontend (port 5000)
  - All Python backend logic maintained (autonomous_engine, database, LLM integrations)
  - New frontend with exact Alpha Arena design replication
- **Design Implementation**:
  - **BLACK BORDERS (2px solid #000)** on ALL components - the defining visual characteristic
  - Market header with real-time crypto prices (BTC, ETH, SOL, BNB, DOGE, XRP)
  - Horizontal navigation: LIVE | LEADERBOARD | BLOG | MODELS
  - 75/25 layout on LIVE: Performance chart (left) + Info panels (right)
  - Leaderboard table with black borders on all cells
  - Vibrant color-coded AI lines: Purple (Gemini), Blue (ChatGPT), Orange (Qwen), Black (Deepseek), Cyan (Grok)
- **Technical Details**:
  - Created api.py with 8 REST endpoints
  - Fixed all database schema mismatches (execution_timestamp, bet_size, actual_result, current_balance, etc.)
  - Added error handling for API responses in frontend
  - Two workflows: api (Flask on 8000), frontend (Next.js on 5000)
- **Result**: Professional Alpha Arena design with well-defined black borders throughout