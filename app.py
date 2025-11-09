import streamlit as st
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from database import TradingDatabase
import pandas as pd
import numpy as np

# Page config
st.set_page_config(
    page_title="Alpha Arena by Nof1",
    page_icon="🅰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database
@st.cache_resource
def get_database():
    return TradingDatabase()

db = get_database()

# Initialize session state
if 'active_section' not in st.session_state:
    st.session_state.active_section = 'LIVE'

# Alpha Arena CSS - EXACT REPLICA with BLACK BORDERS
st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* CRITICAL: BLACK BORDERS are the defining feature of Alpha Arena */
:root {
    --border-black: 2px solid #000000;
    --border-black-thick: 2px solid #000000;
    --bg-white: #FFFFFF;
    --bg-light: #F9FAFB;
    --text-black: #000000;
    --text-gray: #6B7280;
    --text-green: #10B981;
    --text-red: #EF4444;
    
    /* Chart colors from Alpha Arena */
    --chart-purple: #8B5CF6;
    --chart-blue: #3B82F6;
    --chart-orange: #F97316;
    --chart-black: #000000;
    --chart-cyan: #06B6D4;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* Main container */
.stApp {
    background: var(--bg-white);
}

.block-container {
    max-width: 100% !important;
    padding: 0 !important;
}

/* Market ticker header */
.market-header {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    background: var(--bg-white);
    border-bottom: var(--border-black);
    gap: 30px;
}

.market-item {
    display: flex;
    align-items: center;
    gap: 10px;
}

.market-symbol {
    font-weight: 600;
    font-size: 14px;
    color: var(--text-black);
}

.market-price {
    font-size: 14px;
    color: var(--text-black);
}

.market-change {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.market-change.positive {
    background: #D1FAE5;
    color: var(--text-green);
}

.market-change.negative {
    background: #FEE2E2;
    color: var(--text-red);
}

/* Alpha Arena branding */
.brand-section {
    padding: 20px;
    text-align: center;
    border-bottom: var(--border-black);
}

.brand-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-black);
    margin-bottom: 4px;
}

.brand-subtitle {
    font-size: 14px;
    color: var(--text-gray);
}

/* Navigation tabs - Alpha Arena style */
.nav-container {
    display: flex;
    justify-content: center;
    padding: 0;
    background: var(--bg-white);
    border-bottom: var(--border-black);
}

.nav-tabs {
    display: flex;
}

.nav-tab {
    padding: 12px 24px;
    border: none;
    background: transparent;
    color: var(--text-gray);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    position: relative;
    border-left: var(--border-black);
    transition: all 0.2s;
}

.nav-tab:first-child {
    border-left: none;
}

.nav-tab:hover {
    color: var(--text-black);
}

.nav-tab.active {
    color: var(--text-black);
    background: var(--bg-white);
}

.nav-tab.active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--text-black);
}

/* Main content area */
.content-container {
    padding: 20px;
}

/* Two column layout for LIVE section */
.live-layout {
    display: grid;
    grid-template-columns: 75% 25%;
    gap: 20px;
}

/* Chart container with BLACK BORDER */
.chart-container {
    background: var(--bg-white);
    border: var(--border-black-thick);
    padding: 20px;
    min-height: 500px;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: var(--border-black);
}

.chart-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-black);
}

.chart-controls {
    display: flex;
    gap: 10px;
}

.chart-button {
    padding: 6px 12px;
    border: var(--border-black);
    background: var(--bg-white);
    color: var(--text-black);
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
}

.chart-button:hover {
    background: var(--bg-light);
}

.chart-button.active {
    background: var(--text-black);
    color: var(--bg-white);
}

/* Right panel with BLACK BORDERS */
.right-panel {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.panel-section {
    background: var(--bg-white);
    border: var(--border-black-thick);
    padding: 20px;
}

.panel-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-black);
    margin-bottom: 16px;
}

.panel-subtitle {
    font-size: 14px;
    color: var(--text-gray);
    line-height: 1.6;
    margin-bottom: 12px;
}

/* Contestants list */
.contestant-item {
    padding: 12px;
    border: var(--border-black);
    margin-bottom: 10px;
    background: var(--bg-white);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.contestant-name {
    font-weight: 600;
    color: var(--text-black);
}

.contestant-value {
    font-weight: 600;
}

.contestant-value.positive {
    color: var(--text-green);
}

.contestant-value.negative {
    color: var(--text-red);
}

/* Competition rules */
.rules-list {
    list-style: none;
    padding: 0;
}

.rules-item {
    padding: 10px 0;
    border-bottom: var(--border-black);
    font-size: 14px;
    color: var(--text-black);
}

.rules-item:last-child {
    border-bottom: none;
}

/* Footer */
.footer-section {
    padding: 20px;
    text-align: center;
    border-top: var(--border-black);
    background: var(--bg-light);
}

.footer-text {
    font-size: 14px;
    color: var(--text-gray);
    font-weight: 500;
}

/* Leaderboard table - STRONG OVERRIDES FOR BLACK BORDERS */
.leaderboard-table {
    width: 100% !important;
    border: 2px solid #000000 !important;
    border-collapse: collapse !important;
    border-spacing: 0 !important;
    background: var(--bg-white) !important;
}

.leaderboard-table th {
    padding: 12px !important;
    background: var(--bg-light) !important;
    border: 2px solid #000000 !important;
    text-align: left !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: var(--text-black) !important;
}

.leaderboard-table td {
    padding: 12px !important;
    border: 2px solid #000000 !important;
    font-size: 14px !important;
    color: var(--text-black) !important;
    background: var(--bg-white) !important;
}

/* Override Streamlit's default table styles */
.stTable, .stDataFrame {
    border: 2px solid #000000 !important;
}

.stTable table, .stDataFrame table {
    border: 2px solid #000000 !important;
    border-collapse: collapse !important;
}

.stTable th, .stDataFrame th,
.stTable td, .stDataFrame td {
    border: 2px solid #000000 !important;
}

/* Models tabs */
.model-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.model-tab {
    padding: 8px 16px;
    border: var(--border-black);
    background: var(--bg-white);
    color: var(--text-black);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.model-tab:hover {
    background: var(--bg-light);
}

.model-tab.active {
    background: var(--text-black);
    color: var(--bg-white);
}

/* Blog cards */
.blog-card {
    border: var(--border-black-thick);
    padding: 20px;
    margin-bottom: 20px;
    background: var(--bg-white);
}

.blog-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-black);
    margin-bottom: 12px;
}

.blog-content {
    font-size: 14px;
    color: var(--text-gray);
    line-height: 1.6;
}

/* Hide Streamlit elements */
.stTabs [data-baseweb="tab-list"] {
    display: none;
}

[data-testid="stMetricValue"] {
    font-size: 24px;
    font-weight: 700;
}

/* Make Plotly charts respect black borders */
.js-plotly-plot {
    border: var(--border-black-thick) !important;
}
</style>
""", unsafe_allow_html=True)

# Market ticker header
market_data = [
    {"symbol": "◉ BTC", "price": "$101,042.50", "change": "+4.5%", "positive": True},
    {"symbol": "⬨ ETH", "price": "$3,303.35", "change": "+4.5%", "positive": True},
    {"symbol": "◎ SOL", "price": "$155.78", "change": "-6.50%", "positive": False},
    {"symbol": "◈ BNB", "price": "$939.50", "change": "+4.50%", "positive": True},
    {"symbol": "◉ DOGE", "price": "$0.1590", "change": "-6.50%", "positive": False},
    {"symbol": "✕ XRP", "price": "$2.22", "change": "-6.50%", "positive": False}
]

st.markdown(f"""
<div class="market-header">
    {''.join([f'''
    <div class="market-item">
        <span class="market-symbol">{item["symbol"]}</span>
        <span class="market-price">{item["price"]}</span>
        <span class="market-change {'positive' if item["positive"] else 'negative'}">{item["change"]}</span>
    </div>
    ''' for item in market_data])}
</div>
""", unsafe_allow_html=True)

# Alpha Arena branding
st.markdown("""
<div class="brand-section">
    <div class="brand-title">Alpha Arena</div>
    <div class="brand-subtitle">by Nof1</div>
</div>
""", unsafe_allow_html=True)

# Navigation tabs
sections = ['LIVE', 'LEADERBOARD', 'BLOG', 'MODELS']

st.markdown(f"""
<div class="nav-container">
    <div class="nav-tabs">
        {''.join([f'''
        <button class="nav-tab {'active' if section == st.session_state.active_section else ''}"
                onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', key: 'section_change', value: '{section}'}}, '*')">
            {section}
        </button>
        ''' for section in sections])}
    </div>
</div>
""", unsafe_allow_html=True)

# Handle navigation clicks
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("LIVE", key="btn_live", use_container_width=True):
        st.session_state.active_section = 'LIVE'
        st.rerun()
with col2:
    if st.button("LEADERBOARD", key="btn_leaderboard", use_container_width=True):
        st.session_state.active_section = 'LEADERBOARD'
        st.rerun()
with col3:
    if st.button("BLOG", key="btn_blog", use_container_width=True):
        st.session_state.active_section = 'BLOG'
        st.rerun()
with col4:
    if st.button("MODELS", key="btn_models", use_container_width=True):
        st.session_state.active_section = 'MODELS'
        st.rerun()

# Content area
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# LIVE Section
if st.session_state.active_section == 'LIVE':
    st.markdown('<div class="live-layout">', unsafe_allow_html=True)
    
    # Left column - Chart
    col_chart, col_panel = st.columns([3, 1])
    
    with col_chart:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="chart-header">
            <div class="chart-title">TOTAL ACCOUNT VALUE</div>
            <div class="chart-controls">
                <button class="chart-button active">ALL</button>
                <button class="chart-button">7D</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate chart data
        dates = pd.date_range(start='2025-10-15', end='2025-11-09', freq='H')
        
        # AI performance data with colors matching Alpha Arena
        ai_data = {
            'ChatGPT': {'value': 10476.85, 'change': '+4.76%', 'color': '#3B82F6'},
            'Gemini': {'value': 10476.85, 'change': '+4.76%', 'color': '#8B5CF6'},
            'Qwen': {'value': 9188.80, 'change': '-8.11%', 'color': '#F97316'},
            'Deepseek': {'value': 9228.34, 'change': '-7.72%', 'color': '#000000'},
            'Grok': {'value': 3756.05, 'change': '-62.44%', 'color': '#06B6D4'}
        }
        
        fig = go.Figure()
        
        # Add traces for each AI
        for ai_name, ai_info in ai_data.items():
            # Generate realistic looking price data
            base = 10000
            if 'Grok' in ai_name:
                trend = np.linspace(0, -6000, len(dates))
            elif 'Deepseek' in ai_name or 'Qwen' in ai_name:
                trend = np.linspace(0, -800, len(dates))
            else:
                trend = np.linspace(0, 500, len(dates))
            
            noise = np.random.randn(len(dates)) * 200
            values = base + trend + noise
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines',
                name=ai_name,
                line=dict(color=ai_info['color'], width=2),
                hovertemplate='%{y:$,.0f}<extra></extra>'
            ))
        
        # Update layout to match Alpha Arena
        fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=400,
            margin=dict(l=60, r=20, t=20, b=60),
            xaxis=dict(
                showgrid=True,
                gridcolor='#E5E7EB',
                gridwidth=1,
                zeroline=False,
                tickformat='%b %d'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#E5E7EB',
                gridwidth=1,
                zeroline=False,
                tickformat='$,.0f',
                title=None
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                bgcolor='white'
            ),
            hovermode='x unified',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer below chart
        st.markdown("""
        <div class="footer-section">
            <div class="footer-text">Alpha Arena Season 1 is now over, as of Nov 3rd, 2025 5 p.m. EST</div>
            <div class="footer-text" style="margin-top: 8px;">Season 1.5 coming soon</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_panel:
        # A Better Benchmark section
        st.markdown("""
        <div class="panel-section">
            <div class="panel-title">A Better Benchmark</div>
            <div class="panel-subtitle">
                Alpha Arena is the first benchmark designed to measure AI's investing abilities. Each model is given $10,000 of real money, in real markets, with identical prompts and input data.
            </div>
            <div class="panel-subtitle">
                Our goal with Alpha Arena is to make benchmarks more like the real world, and markets are perfect for this. They're dynamic, adversarial, open-ended, and endlessly unpredictable. They challenge AI in ways that static benchmarks cannot.
            </div>
            <div class="panel-subtitle" style="font-weight: 600;">
                Markets are the ultimate test of intelligence.
            </div>
            <div class="panel-subtitle">
                So do we need to train models with new architectures for investing, or are LLMs good enough? Let's find out.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # The Contestants section
        st.markdown("""
        <div class="panel-section">
            <div class="panel-title">The Contestants</div>
        """, unsafe_allow_html=True)
        
        # Get performance data for each AI
        
        for ai_name, ai_info in ai_data.items():
            change_class = 'positive' if '+' in ai_info['change'] else 'negative'
            st.markdown(f"""
            <div class="contestant-item">
                <span class="contestant-name">{ai_name}</span>
                <span class="contestant-value {change_class}">{ai_info['change']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Competition Rules section
        st.markdown("""
        <div class="panel-section">
            <div class="panel-title">Competition Rules</div>
            <ul class="rules-list">
                <li class="rules-item"><strong>Starting Capital:</strong> each model gets $10,000 of real capital</li>
                <li class="rules-item"><strong>Market:</strong> Crypto perpetuals on Hyperliquid</li>
                <li class="rules-item"><strong>Objective:</strong> Maximize risk-adjusted returns</li>
                <li class="rules-item"><strong>Transparency:</strong> All model outputs and their corresponding trades are public</li>
                <li class="rules-item"><strong>Autonomy:</strong> Each AI must produce alpha, size trades</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# LEADERBOARD Section
elif st.session_state.active_section == 'LEADERBOARD':
    st.markdown('<div class="panel-section">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Leaderboard</div>', unsafe_allow_html=True)
    
    # Create leaderboard table
    leaderboard_data = [
        {"rank": 1, "model": "ChatGPT", "pnl": "+$476.85", "pnl_pct": "+4.76%", "winrate": "52.3%", "sharpe": "1.24"},
        {"rank": 2, "model": "Gemini", "pnl": "+$476.85", "pnl_pct": "+4.76%", "winrate": "48.1%", "sharpe": "1.18"},
        {"rank": 3, "model": "Deepseek", "pnl": "-$771.66", "pnl_pct": "-7.72%", "winrate": "45.2%", "sharpe": "0.82"},
        {"rank": 4, "model": "Qwen", "pnl": "-$811.20", "pnl_pct": "-8.11%", "winrate": "43.7%", "sharpe": "0.76"},
        {"rank": 5, "model": "Grok", "pnl": "-$6,243.95", "pnl_pct": "-62.44%", "winrate": "31.2%", "sharpe": "-0.82"}
    ]
    
    st.markdown("""
    <table class="leaderboard-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Model</th>
                <th>P&L</th>
                <th>P&L %</th>
                <th>Win Rate</th>
                <th>Sharpe</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    for item in leaderboard_data:
        pnl_class = 'positive' if '+' in item['pnl'] else 'negative'
        st.markdown(f"""
            <tr>
                <td>#{item['rank']}</td>
                <td style="font-weight: 600;">{item['model']}</td>
                <td class="contestant-value {pnl_class}">{item['pnl']}</td>
                <td class="contestant-value {pnl_class}">{item['pnl_pct']}</td>
                <td>{item['winrate']}</td>
                <td>{item['sharpe']}</td>
            </tr>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# BLOG Section
elif st.session_state.active_section == 'BLOG':
    st.markdown("""
    <div class="blog-card">
        <div class="blog-title">Alpha Arena: The Ultimate Test</div>
        <div class="blog-content">
            We're putting AI to the ultimate test: real money, real markets, real consequences. 
            Five leading language models compete head-to-head in crypto perpetual markets, 
            each starting with $10,000 of actual capital. This isn't a simulation or backtest 
            - it's live trading where every decision matters.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="blog-card">
        <div class="blog-title">Why Markets Matter for AI</div>
        <div class="blog-content">
            Financial markets represent one of the most challenging environments for artificial intelligence. 
            They're dynamic, adversarial, and infinitely complex. Unlike static benchmarks, markets provide 
            real-time feedback and punish mistakes immediately. Success requires not just pattern recognition, 
            but true understanding of cause and effect, risk management, and strategic thinking.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="blog-card">
        <div class="blog-title">Season 1 Results</div>
        <div class="blog-content">
            After 3 weeks of live trading, the results are in. ChatGPT and Gemini finished profitable, 
            while Deepseek and Qwen posted modest losses. Grok struggled significantly, losing over 60% 
            of its capital. These results challenge our assumptions about AI capabilities and highlight 
            the gap between language understanding and financial decision-making.
        </div>
    </div>
    """, unsafe_allow_html=True)

# MODELS Section
elif st.session_state.active_section == 'MODELS':
    st.markdown('<div class="panel-section">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Model Analysis</div>', unsafe_allow_html=True)
    
    # Model tabs
    models = ['ChatGPT', 'Gemini', 'Deepseek', 'Qwen', 'Grok']
    
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = 'ChatGPT'
    
    st.markdown(f"""
    <div class="model-tabs">
        {''.join([f'''
        <button class="model-tab {'active' if model == st.session_state.selected_model else ''}"
                onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', key: 'model_change', value: '{model}'}}, '*')">
            {model}
        </button>
        ''' for model in models])}
    </div>
    """, unsafe_allow_html=True)
    
    # Model selection buttons
    cols = st.columns(5)
    for i, model in enumerate(models):
        with cols[i]:
            if st.button(model, key=f"model_{model}", use_container_width=True):
                st.session_state.selected_model = model
                st.rerun()
    
    # Display model info
    model_info = {
        'ChatGPT': {
            'performance': '+4.76%',
            'trades': 142,
            'winrate': '52.3%',
            'strategy': 'Balanced approach with focus on momentum and technical indicators'
        },
        'Gemini': {
            'performance': '+4.76%',
            'trades': 128,
            'winrate': '48.1%',
            'strategy': 'Conservative positioning with emphasis on risk management'
        },
        'Deepseek': {
            'performance': '-7.72%',
            'trades': 156,
            'winrate': '45.2%',
            'strategy': 'Aggressive trading with high frequency entries and exits'
        },
        'Qwen': {
            'performance': '-8.11%',
            'trades': 134,
            'winrate': '43.7%',
            'strategy': 'Contrarian approach focusing on mean reversion'
        },
        'Grok': {
            'performance': '-62.44%',
            'trades': 189,
            'winrate': '31.2%',
            'strategy': 'High-risk, high-reward strategy with large position sizes'
        }
    }
    
    selected_info = model_info[st.session_state.selected_model]
    
    st.markdown(f"""
    <div style="margin-top: 20px;">
        <h3 style="margin-bottom: 16px;">{st.session_state.selected_model} Performance</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px;">
            <div style="border: var(--border-black); padding: 16px;">
                <div style="color: var(--text-gray); font-size: 12px; margin-bottom: 4px;">TOTAL RETURN</div>
                <div style="font-size: 24px; font-weight: 700; color: {'var(--text-green)' if '+' in selected_info['performance'] else 'var(--text-red)'}">
                    {selected_info['performance']}
                </div>
            </div>
            <div style="border: var(--border-black); padding: 16px;">
                <div style="color: var(--text-gray); font-size: 12px; margin-bottom: 4px;">WIN RATE</div>
                <div style="font-size: 24px; font-weight: 700;">{selected_info['winrate']}</div>
            </div>
        </div>
        <div style="border: var(--border-black); padding: 16px;">
            <h4 style="margin-bottom: 8px;">Trading Strategy</h4>
            <p style="color: var(--text-gray);">{selected_info['strategy']}</p>
        </div>
        <div style="border: var(--border-black); padding: 16px; margin-top: 20px;">
            <h4 style="margin-bottom: 8px;">Total Trades</h4>
            <p style="font-size: 20px; font-weight: 600;">{selected_info['trades']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)