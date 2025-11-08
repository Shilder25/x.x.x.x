# TradingAgents Framework

## Overview

This is a multi-LLM trading simulation framework that runs an autonomous prediction competition between five AI-powered trading firms: ChatGPT, Gemini, Qwen, Deepseek, and Grok. Each firm independently analyzes financial market events using technical indicators, fundamental data, and sentiment analysis, then generates probabilistic predictions for binary trading outcomes. The system tracks performance metrics (accuracy, Sharpe ratio, profit/loss) across all firms and maintains virtual portfolios to simulate real trading scenarios. Built with Streamlit for the UI, it integrates multiple data sources (Alpha Vantage, Yahoo Finance, Reddit) and uses a sophisticated prompt system that simulates a 7-role internal decision-making process within each LLM.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-tab interface
- **State Management**: Session state pattern for maintaining database connections, orchestrator instances, and cached data (predictions, technical/fundamental/sentiment data)
- **Layout**: Wide-layout configuration with four main tabs for different views (analysis, predictions, performance, portfolio management)
- **Rationale**: Streamlit provides rapid prototyping with built-in state management, eliminating the need for separate frontend/backend architecture while supporting real-time data visualization

### Backend Architecture
- **Pattern**: Modular service-oriented design with clear separation of concerns
- **Core Components**:
  - `TradingDatabase`: SQLite-based persistence layer for predictions, firm performance, and virtual portfolios
  - `FirmOrchestrator`: Manages multiple LLM clients and coordinates prediction generation across all five firms
  - Individual firm clients (ChatGPTFirm, GeminiFirm, etc.): Encapsulate LLM-specific API interactions
  - Data collectors: Specialized classes for different data sources (technical, fundamental, sentiment)
  - Prompt system: Generates structured prompts that simulate multi-agent trading firm decision-making
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
- Alpha Vantage API key (referenced in `AlphaVantageCollector`)
- Reddit API credentials for PRAW (client_id, client_secret, user_agent)
- Additional API keys for Qwen, Deepseek, and Grok integrations