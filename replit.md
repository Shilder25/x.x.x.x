# TradingAgents Framework

## Overview
This project is a multi-LLM trading simulation framework where five AI-powered trading firms (ChatGPT, Gemini, Qwen, Deepseek, Grok) compete autonomously. Each firm analyzes financial market events using technical indicators, fundamental data, and sentiment analysis to generate probabilistic predictions for binary trading outcomes. The system tracks performance metrics (accuracy, Sharpe ratio, profit/loss), maintains virtual portfolios, and includes a sophisticated prompt system simulating a 7-role internal decision-making process within each LLM. The framework also features an autonomous trading mode where IAs continuously adapt their strategies based on performance, aiming for continuous improvement rather than termination upon losses.

## Current Status
**System Status:** ✅ Fully Functional (Last Verified: November 8, 2025)
- Complete autonomous trading system implemented and tested
- Database integration: All bets, cycles, and adaptations are persisted
- Learning system: Weekly analysis and continuous improvement active
- UI reorganized with premium design: Clear separation between manual and autonomous systems
- E2E testing: Passed comprehensive UI/UX validation

## Recent Changes (November 8, 2025)
**Public Dashboard - Complete Redesign (White Minimalist Theme):**
- Created public-facing dashboard (public_dashboard.py) with nof1.ai-inspired minimalist aesthetic
  - Clean white background throughout (no dark themes)
  - Native Streamlit components (st.metric, st.dataframe, st.expander) instead of raw HTML
  - 4 key metrics: Total Capital, Current Leader, Average P&L, Best/Worst Performance
  - Interactive Plotly chart showing all 5 AI account values over time (white theme)
  - Leaderboard table with ranking (#1, #2, etc.) - minimalist typography
  - System Activity table showing 7 internal departments with status
  - **AI Internal Deliberation section**: Shows how each AI's 7 departments debate before making decisions
    - Pulls real data from predictions table (analisis_sintesis, debate_bullish_bearish, ajuste_riesgo_justificacion)
    - Expandable sections for each AI showing their complete decision-making process
    - Three-stage visualization: Analysis & Synthesis, Bullish vs Bearish Debate, Risk Adjustment
    - Department activity badges showing all 7 active departments
  - Auto-refresh every 30 seconds using streamlit-autorefresh
  - Runs on port 5000 as standalone dashboard
  - E2E tested: All components render correctly, white theme verified

**Navigation Reorganization - Improved Discoverability:**
- Created new Tab 1 (Inicio): Landing page with two prominent cards explaining both modes
  - Sistema Manual card: 6 features, ideal use cases, and navigation button
  - Competencia Autónoma card: 6 features, ideal use cases, and navigation button
  - Comparison section: Control, time dedication, and objectives
- Moved Competencia Autónoma from Tab 7 to Tab 2 for better visibility
- Reorganized manual system tabs (3-8) maintaining all functionality
- Security fix: Removed hardcoded Alpha Vantage API key, added proper error handling
- E2E tested: All 8 tabs verified and functional

**Previous UI Reorganization - Premium Design:**
- Tab 3 (Manual System): Reorganized in 3 clear steps with visual hierarchy, progress metrics, and status indicators
- Tab 2 (Autonomous System): Two-column layout with control panel, global metrics, premium leaderboard with position badges
- Visual improvements: Consistent dividers, containers, metrics with deltas, status indicators with emojis
- Better UX: Clear separation between manual prediction system and autonomous competition mode

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses Streamlit for a multi-tab web interface, configured with a wide layout. It uses session state for managing database connections, orchestrators, and cached data. There are seven main tabs: 'Nueva Predicción' (Generate predictions), 'Panel de Transparencia' (Detailed reasoning), 'Dashboard Comparativo' (Compare firm performance), 'Recomendaciones & Consenso' (Recommendation engine), 'Enviar a Opinion.trade' (Submit predictions), 'Registrar Resultados' (Track outcomes), and 'Competencia Autónoma' (Autonomous trading competition dashboard).

### Backend Architecture
The backend employs a modular, service-oriented design. Key components include:
- **`TradingDatabase`**: An SQLite-based persistence layer for predictions, firm performance, and virtual portfolios with automatic schema migration.
- **`FirmOrchestrator`**: Manages LLM clients and prediction generation across firms.
- **Individual Firm Clients**: Encapsulate LLM-specific API interactions.
- **Data Collectors**: Specialized classes for technical, fundamental, and sentiment data.
- **Prompt System**: Generates structured prompts simulating a 7-role trading firm decision-making process across three stages: Analysis & Synthesis, Bullish/Bearish Debate, and Risk Evaluation & Final Decision.
- **`RecommendationEngine`**: Analyzes historical performance for prediction recommendations.
- **`OpinionTradeAPI`**: Handles automated prediction submission.
- **`Autonomous Engine`**: Orchestrates daily trading cycles for all IAs, including event analysis, risk-aware betting, and simulation/real mode toggling.
- **`Risk Management System`**: A multi-level adaptive system that never stops, but adapts strategies based on profit/loss thresholds (-0% to -9% normal, -10% to -19% tactical adjustment, -20% to -29% strategy change, -30%+ reinvention, +50% positive adaptation). It includes safety features like daily loss limits and category exposure limits.
- **`Bankroll Management`**: Assigns different betting strategies to each IA (Kelly Criterion, Modified Martingale, Fixed Fractional, Proportional, Anti-Martingale) to foster competitive diversity.
- **`Learning System`**: Provides continuous improvement through weekly performance analysis, including pattern recognition, category performance tracking, confidence calibration, and EV accuracy assessment, generating actionable recommendations.

### LLM Integration Architecture
A multi-provider approach supports different LLM APIs with built-in rate limiting (exponential backoff) and cost tracking. It leverages Replit's managed OpenAI integration for ChatGPT.

### Data Collection Architecture
A multi-source strategy uses specialized collectors: `AlphaVantageCollector` for technical indicators, `YFinanceCollector` for fundamental data, and `RedditSentimentCollector` for social sentiment analysis using VADER.

### Data Storage
An embedded SQLite database is used, with a schema designed for `predictions`, `firm_performance`, `virtual_portfolio`, `autonomous_bets`, `autonomous_cycles`, and `strategy_adaptations`. Automatic schema migration ensures backward compatibility.

### Visualization Layer
Plotly is used for interactive charts within Streamlit, including time series, performance dashboards, and portfolio visualizations.

## External Dependencies

### LLM APIs
- **OpenAI** (ChatGPT)
- **Google Gemini**
- **Qwen, Deepseek, Grok**

### Financial Data APIs
- **Alpha Vantage** (technical indicators, market data)
- **Yahoo Finance** (fundamental data, historical prices)

### Social Media Data
- **Reddit API** (PRAW for sentiment analysis)

### Python Libraries
- `streamlit`
- `streamlit-autorefresh`
- `pandas`
- `plotly`
- `yfinance`
- `praw`
- `nltk` (for VADER sentiment)
- `tenacity`
- `sqlite3`
- `openai`
- `google-genai`

### Environment Variables Required
- `AI_INTEGRATIONS_OPENAI_API_KEY`
- `AI_INTEGRATIONS_OPENAI_BASE_URL`
- `ALPHA_VANTAGE_API_KEY`
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- `OPINION_TRADE_API_KEY`
- `DEEPSEEK_API_KEY`, `QWEN_API_KEY`, `XAI_API_KEY`