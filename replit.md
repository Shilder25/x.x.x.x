# TradingAgents Framework

## Overview
This project is a multi-LLM prediction market framework where five AI prediction agents (ChatGPT, Gemini, Qwen, Deepseek, Grok) autonomously compete on Opinion.trade (BNB Chain). Each agent analyzes financial market events using technical indicators, fundamental data, and sentiment analysis to generate probabilistic predictions for binary outcomes. The system tracks performance, maintains virtual portfolios, and includes a sophisticated prompt system simulating a 7-role internal decision-making process for each LLM. The framework supports continuous adaptation of AI strategies based on performance, aiming for ongoing improvement.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses Streamlit for a multi-tab web interface with a wide layout, managing database connections and cached data via session state. It features a public Alpha Arena dashboard and a protected admin panel.

**Design System:**
- **Alpha Arena (Public Dashboard)**: Premium dark theme with purple/cyan gradients, glassmorphism effects, custom typography (Space Grotesk, Manrope, IBM Plex Mono)
- **Admin Panel**: Unified premium dark theme matching Alpha Arena aesthetic with Binance Gold (#F0B90B) as primary accent
  - Limited color palette: Gold (#F0B90B) + Teal (#0EA5E9) + Slate (#334155) + status colors
  - Completely emoji-free minimalist design
  - Premium cards with gold top borders and glassmorphism
  - Custom button styling with gold gradients and hover effects
  - Dark-themed charts with gold accents
  - Clean typography hierarchy with Space Grotesk headings

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
- `ADMIN_PASSWORD`

## Recent Changes (November 9, 2025)

**Admin Panel Redesign - Premium Dark Aesthetic (Latest):**
- **Complete Visual Overhaul**: Redesigned admin panel to match Alpha Arena premium dark aesthetic
- **Binance Gold Accent System**: 
  - Primary accent: #F0B90B (Binance gold) with glow effects
  - Supporting colors: Teal (#0EA5E9), Slate (#334155)
  - Status colors: Green (#22C55E), Yellow (#F59E0B), Orange (#F97316), Red (#EF4444)
- **Emoji-Free Minimalist Design**:
  - Removed ALL emojis from entire admin interface
  - Clean tab names: "Home", "Autonomous Competition", "New Prediction", etc.
  - Simple section headers without visual clutter
  - Status indicators use text (WON/LOST/PENDING) instead of checkmarks/emojis
  - Position numbers (#1, #2, #3) instead of medal emojis
- **Premium CSS System**:
  - Gold gradient header: "TRADINGAGENTS"
  - Custom button styling with gold gradients and hover glow
  - Premium cards with gold top borders and glassmorphism
  - Dark metrics with gold values
  - Custom tabs with gold active state
- **Chart Theming**:
  - All charts use plotly_dark template
  - Dark transparent backgrounds matching overall theme
  - Gold title colors
  - Custom color scales with gold highlights
- **Typography Consistency**:
  - Space Grotesk for headings (400-700)
  - Manrope for body text (400-700)
  - IBM Plex Mono for numbers (400-600)
- **Complete Implementation**:
  - 8 tabs fully redesigned with consistent styling
  - Home tab features premium cards with gold accents
  - Autonomous Competition tab with clean status boxes
  - All forms, inputs, and interactive elements themed
  - Sidebar admin controls with glassmorphism