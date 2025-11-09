# TradingAgents Framework

## Overview
This project is a multi-LLM prediction market framework where five AI prediction agents (ChatGPT, Gemini, Qwen, Deepseek, Grok) autonomously compete on Opinion.trade (BNB Chain). Each agent analyzes financial market events using technical indicators, fundamental data, and sentiment analysis to generate probabilistic predictions for binary outcomes. The system tracks performance, maintains virtual portfolios, and includes a sophisticated prompt system simulating a 7-role internal decision-making process for each LLM. The framework supports continuous adaptation of AI strategies based on performance, aiming for ongoing improvement.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses Streamlit for a multi-tab web interface with a wide layout, managing database connections and cached data via session state. It features a public Alpha Arena dashboard and a protected admin panel. The UI has undergone a complete visual transformation to a premium dark theme with glassmorphism effects, custom typography, and a comprehensive CSS variable system.

### Backend Architecture
The backend employs a modular, service-oriented design with key components such as:
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
Plotly is used for interactive charts within Streamlit, providing time series, performance dashboards, and portfolio visualizations with a dark theme.

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

### Python Libraries
- `streamlit`
- `streamlit-autorefresh`
- `pandas`
- `plotly`
- `yfinance`
- `praw`
- `nltk`
- `tenacity`
- `sqlite3`
- `openai`
- `google-genai`

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