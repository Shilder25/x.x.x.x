# TradingAgents Framework

## Overview

This is a multi-LLM trading simulation framework that runs an autonomous prediction competition between five AI-powered trading firms: ChatGPT, Gemini, Qwen, Deepseek, and Grok. Each firm independently analyzes financial market events using technical indicators, fundamental data, and sentiment analysis, then generates probabilistic predictions for binary trading outcomes. The system tracks performance metrics (accuracy, Sharpe ratio, profit/loss) across all firms and maintains virtual portfolios to simulate real trading scenarios. Built with Streamlit for the UI, it integrates multiple data sources (Alpha Vantage, Yahoo Finance, Reddit) and uses a sophisticated prompt system that simulates a 7-role internal decision-making process within each LLM.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-tab interface
- **State Management**: Session state pattern for maintaining database connections, orchestrator instances, RecommendationEngine, and cached data (predictions, technical/fundamental/sentiment data)
- **Layout**: Wide-layout configuration with six main tabs:
  1. Nueva Predicción: Generate predictions from all 5 firms
  2. Panel de Transparencia: View detailed reasoning chains
  3. Dashboard Comparativo: Compare firm performance (accuracy, Sharpe ratio, profit/loss)
  4. Recomendaciones & Consenso: Recommendation engine, consensus predictions, pattern analysis, attribution reports
  5. Enviar a Opinion.trade: Submit predictions via API
  6. Registrar Resultados: Track actual outcomes and profit/loss
- **Rationale**: Streamlit provides rapid prototyping with built-in state management, eliminating the need for separate frontend/backend architecture while supporting real-time data visualization

### Backend Architecture
- **Pattern**: Modular service-oriented design with clear separation of concerns
- **Core Components**:
  - `TradingDatabase`: SQLite-based persistence layer for predictions, firm performance, and virtual portfolios with automatic schema migration
  - `FirmOrchestrator`: Manages multiple LLM clients and coordinates prediction generation across all five firms
  - Individual firm clients (ChatGPTFirm, GeminiFirm, etc.): Encapsulate LLM-specific API interactions
  - Data collectors: Specialized classes for different data sources (technical, fundamental, sentiment)
  - Prompt system: Generates structured prompts that simulate multi-agent trading firm decision-making
  - `RecommendationEngine`: Analyzes historical performance to recommend which firm's prediction to use
  - `OpinionTradeAPI`: Handles automated submission of predictions to Opinion.trade platform
- **Rationale**: Modular design allows independent evolution of each component and easy addition of new LLMs or data sources

### Prompt Engineering Strategy
- **Multi-Stage Reasoning**: Prompts simulate a 7-role trading firm structure with three decision stages:
  1. Analysis & Synthesis (Analyst Team)
  2. Bullish/Bearish Debate (Researcher Team + Trader)
  3. Risk Evaluation & Final Decision (Risk Management Team)
- **Structured Output**: Forces LLMs to produce JSON-formatted predictions with probability scores, risk posture, and detailed reasoning
- **Rationale**: This simulates realistic institutional trading decision processes and provides interpretable reasoning chains while maintaining consistent output format across different LLMs

### Data Storage
- **Database**: SQLite embedded database
- **Schema Design**:
  - `predictions`: Stores individual predictions with full reasoning chain and cost tracking
  - `firm_performance`: Aggregated metrics per firm (accuracy, Sharpe ratio, total profit/loss)
  - `virtual_portfolio`: Position tracking for simulated trading
- **Schema Migration**: Automatic migration system (`_migrate_schema()`) detects legacy databases and adds new columns (e.g., sharpe_ratio) via ALTER TABLE to ensure backward compatibility
- **Rationale**: SQLite eliminates deployment complexity (no separate DB server) while providing ACID compliance for financial tracking. Suitable for single-user simulation environments with moderate data volumes.

### LLM Integration Architecture
- **Provider Strategy**: Multi-provider approach supporting different LLM APIs
- **Rate Limiting**: Exponential backoff retry mechanism with specific detection for 429/rate limit errors across all providers
- **Cost Tracking**: Token usage and cost estimation built into each firm client
- **Replit AI Integrations**: Uses Replit's managed OpenAI integration (billed to credits) for ChatGPT, avoiding manual API key management
- **Alternatives Considered**: 
  - Single LLM approach: Rejected to enable competitive comparison
  - Langchain framework: Rejected to minimize dependencies and maintain direct API control
- **Pros**: Direct API access provides fine-grained control over prompts and responses; competitive framework enables quality benchmarking
- **Cons**: Managing multiple API clients increases code complexity; rate limits require careful handling

### Data Collection Architecture
- **Multi-Source Strategy**: Three specialized collectors for different data types
  - `AlphaVantageCollector`: Technical indicators (RSI, MACD, price quotes)
  - `YFinanceCollector`: Fundamental data and historical prices
  - `RedditSentimentCollector`: Social sentiment analysis using VADER
- **Error Handling**: Each collector returns structured error objects with timestamps
- **Rationale**: Separating data sources allows independent failure handling and makes it easy to swap providers or add new sources. VADER sentiment analysis provides lightweight NLP without heavy model dependencies.

### Visualization Layer
- **Libraries**: Plotly for interactive charts (graph_objects and express APIs)
- **Chart Types**: Time series for price data, performance metrics dashboards, portfolio visualizations
- **Rationale**: Plotly provides rich interactivity within Streamlit without custom JavaScript, supporting drill-down analysis of firm performance

## External Dependencies

### LLM APIs
- **OpenAI** (ChatGPT): Accessed via Replit AI Integrations with automatic billing to Replit credits
- **Google Gemini**: Uses `google.genai` SDK for Gemini model access
- **Qwen, Deepseek, Grok**: Integrated as additional competing firms (implementation details in `llm_clients.py`)

### Financial Data APIs
- **Alpha Vantage**: Real-time and historical market data, technical indicators (RSI, MACD)
  - Requires API key via environment variable
  - Rate limits apply to free tier
- **Yahoo Finance** (yfinance): Fundamental data, company financials, historical prices
  - No API key required
  - Unofficial API, subject to changes

### Social Media Data
- **Reddit API** (PRAW): Sentiment analysis from trading-related subreddits
  - Requires Reddit API credentials
  - VADER lexicon for sentiment scoring (NLTK dependency)

### Python Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization
- **yfinance**: Yahoo Finance data wrapper
- **praw**: Reddit API wrapper
- **nltk**: Natural language processing (VADER sentiment)
- **tenacity**: Retry logic with exponential backoff
- **sqlite3**: Database (Python standard library)
- **openai**: OpenAI API client
- **google-genai**: Google Gemini API client

### Environment Variables Required
- `AI_INTEGRATIONS_OPENAI_API_KEY`: Managed by Replit for OpenAI access
- `AI_INTEGRATIONS_OPENAI_BASE_URL`: Managed by Replit for OpenAI routing
- `ALPHA_VANTAGE_API_KEY`: For technical indicators and market data
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`: For Reddit sentiment analysis
- `OPINION_TRADE_API_KEY`: For automated prediction submission to Opinion.trade platform
- `DEEPSEEK_API_KEY`, `QWEN_API_KEY`, `XAI_API_KEY`: For additional LLM providers

## Recent Changes

### November 8, 2025 - Advanced Analytics & Integration Features
**Added Opinion.trade Integration (opinion_trade_api.py):**
- Automated submission module for posting predictions to Opinion.trade platform
- Retry logic with exponential backoff for API failures
- Proper error handling and validation for prediction data
- Integrated into Tab 5 UI with firm selection and manual submission controls

**Implemented Recommendation Engine (recommendation_engine.py):**
- Smart firm selection based on historical accuracy, Sharpe ratio, and total profit
- Confidence scoring system with alternative recommendations
- Weighted consensus predictions combining multiple firms
- Pattern analysis correlating risk postures with success rates
- Detailed attribution reporting showing which firms generated wins/losses

**Added Sharpe Ratio Calculation:**
- Risk-adjusted return metric for comparing firm performance
- Automatic database migration for existing databases
- Proper handling of zero-variance edge cases
- Integrated into comparative dashboard and performance metrics

**Expanded UI to 6 Tabs:**
- Tab 4 (Recomendaciones & Consenso): Displays best firm recommendation, consensus prediction with visualization, reasoning pattern analysis by risk posture, and detailed attribution reports
- Tab 5 (Enviar a Opinion.trade): Manual submission interface with firm selection, prediction review, and API integration
- Tab 6 (Registrar Resultados): Result tracking interface for recording actual outcomes and calculating profit/loss

**Database Enhancements:**
- Automatic schema migration system (`_migrate_schema()`) for backward compatibility
- Added `sharpe_ratio` column to `firm_performance` table
- Enhanced error handling for schema changes
- Migration runs automatically on database initialization