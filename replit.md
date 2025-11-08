# TradingAgents Framework

## Overview
This project is a multi-LLM trading simulation framework where five AI-powered trading firms (ChatGPT, Gemini, Qwen, Deepseek, Grok) compete autonomously. Each firm analyzes financial market events using technical indicators, fundamental data, and sentiment analysis to generate probabilistic predictions for binary trading outcomes. The system tracks performance metrics (accuracy, Sharpe ratio, profit/loss), maintains virtual portfolios, and includes a sophisticated prompt system simulating a 7-role internal decision-making process within each LLM. The framework also features an autonomous trading mode where IAs continuously adapt their strategies based on performance, aiming for continuous improvement rather than termination upon losses.

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