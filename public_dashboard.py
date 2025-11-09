import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from database import TradingDatabase
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(
    page_title="Alpha Arena - Prediction Intelligence",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh cada 30 segundos
count = st_autorefresh(interval=30000, key="alpha_refresh")

# Initialize session state for persistent data
if 'historical_data_initialized' not in st.session_state:
    st.session_state.historical_data_initialized = False
    st.session_state.historical_data = None
    st.session_state.last_db_check = datetime.now()

# Initialize navigation state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'LIVE'

# Professional Design System - Inspirado en nof1.ai
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* White theme profesional */
    .stApp {
        background: #FFFFFF;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Eliminar padding default - optimizado para Replit */
    .main .block-container {
        padding: 0.75rem 1rem;
        max-width: 100%;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Header profesional - optimizado para Replit */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0 0.75rem 0;
        border-bottom: 1px solid #E5E5E5;
        margin-bottom: 1rem;
    }
    
    .logo {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #111111;
        letter-spacing: -0.02em;
    }
    
    .logo-subtitle {
        font-size: 0.75rem;
        color: #666666;
        font-weight: 400;
        margin-left: 0.5rem;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
        font-size: 0.875rem;
        font-weight: 500;
        color: #111111;
    }
    
    .nav-link {
        cursor: pointer;
        transition: all 0.2s;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
    }
    
    .nav-link:hover {
        color: #666666;
        background: #F5F5F5;
    }
    
    .nav-link.active {
        color: #9747FF;
        font-weight: 600;
    }
    
    /* Chart section */
    .chart-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #111111;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    /* Info panel - optimizado para Replit */
    .info-panel {
        background: #FAFAFA;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        padding: 1rem;
        height: 100%;
    }
    
    .info-section {
        margin-bottom: 1.25rem;
    }
    
    .info-section:last-child {
        margin-bottom: 0;
    }
    
    .info-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #111111;
        margin-bottom: 1rem;
    }
    
    .info-text {
        font-size: 0.8125rem;
        line-height: 1.6;
        color: #444444;
        margin-bottom: 0.75rem;
    }
    
    /* AI Leaderboard */
    .ai-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 6px;
        transition: all 0.2s;
    }
    
    .ai-item:hover {
        border-color: #CCCCCC;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .ai-name-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .ai-color-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    
    .ai-name {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        color: #111111;
    }
    
    .ai-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8125rem;
        font-weight: 500;
        color: #111111;
    }
    
    /* Competition rules */
    .rule-item {
        font-size: 0.8125rem;
        color: #444444;
        margin-bottom: 0.5rem;
        padding-left: 1rem;
        position: relative;
    }
    
    .rule-item:before {
        content: "•";
        position: absolute;
        left: 0;
        color: #111111;
        font-weight: 600;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        padding: 1rem 0;
        font-size: 0.75rem;
        color: #666666;
        border-top: 1px solid #E5E5E5;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    return TradingDatabase()

db = get_database()

# AI Color Palette - Colores vibrantes profesionales
AI_COLORS = {
    'ChatGPT': '#9747FF',      # Morado vibrante
    'Gemini': '#4285F4',       # Azul Google
    'Deepseek': '#FF6B35',     # Naranja
    'Qwen': '#00D9A6',         # Verde esmeralda
    'Grok': '#00BCD4'          # Cyan
}

# Get AI data - SIEMPRE 5 AIs con datos persistentes
def get_ai_historical_data():
    """Get historical data for all 5 AIs - uses simulation for now"""
    # Return cached data if available
    if st.session_state.historical_data is not None:
        return st.session_state.historical_data
    
    # Generate consistent simulation for all AIs
    data = {}
    for ai_name in AI_COLORS.keys():
        data[ai_name] = generate_ai_simulation(ai_name)
    
    # Store in session state (persists across auto-refreshes)
    st.session_state.historical_data = data
    st.session_state.historical_data_initialized = True
    st.session_state.last_db_check = datetime.now()
    
    return data

def generate_ai_simulation(ai_name):
    """Generate consistent simulation for an AI"""
    # Use fixed seed based on AI name only for consistency
    np.random.seed(hash(ai_name) % 10000)
    
    days = 30
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    initial = 10000
    
    # Different performance profiles per AI
    profiles = {
        'ChatGPT': {'trend': 0.015, 'volatility': 0.02},
        'Deepseek': {'trend': 0.01, 'volatility': 0.025},
        'Gemini': {'trend': 0.005, 'volatility': 0.018},
        'Qwen': {'trend': -0.008, 'volatility': 0.022},
        'Grok': {'trend': 0.003, 'volatility': 0.02}
    }
    
    profile = profiles.get(ai_name, {'trend': 0, 'volatility': 0.02})
    
    values = [initial]
    for i in range(1, days):
        change = np.random.normal(profile['trend'], profile['volatility'])
        new_value = values[-1] * (1 + change)
        values.append(new_value)
    
    return {
        'dates': dates,
        'values': values,
        'current': values[-1],
        'pnl_pct': ((values[-1] - initial) / initial) * 100
    }

# Get data
historical_data = get_ai_historical_data()

# HEADER with functional navigation
header_col1, header_col2 = st.columns([3, 2])

with header_col1:
    st.markdown("""
    <div style="display: flex; align-items: baseline; padding: 0.5rem 0;">
        <span class="logo">◐ Alpha Arena</span>
        <span class="logo-subtitle">by nof1.ai</span>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    nav_cols = st.columns(4)
    nav_items = ['LIVE', 'LEADERBOARD', 'BLOG', 'MODELS']
    
    for idx, (col, item) in enumerate(zip(nav_cols, nav_items)):
        with col:
            is_active = st.session_state.current_view == item
            if st.button(
                item,
                key=f"nav_{item}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_view = item
                st.rerun()

st.markdown('<hr style="margin: 0.5rem 0 0.75rem 0; border: none; border-top: 1px solid #E5E5E5;">', unsafe_allow_html=True)

# CONTENT BASED ON VIEW
if st.session_state.current_view == 'LIVE':
    # MAIN LAYOUT: Chart (70%) | Info Panel (30%)
    chart_col, info_col = st.columns([7, 3], gap="medium")

    with chart_col:
        st.markdown('<div class="chart-title">TOTAL ACCOUNT VALUE</div>', unsafe_allow_html=True)
        
        # Create professional multi-line chart
        fig = go.Figure()
        
        # Add line for each AI
        for ai_name, color in AI_COLORS.items():
            data = historical_data[ai_name]
            
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['values'],
                mode='lines',
                name=ai_name,
                line=dict(
                    color=color,
                    width=2.5
                ),
                hovertemplate=(
                    f'<b>{ai_name}</b><br>' +
                    'Date: %{x|%b %d}<br>' +
                    'Value: $%{y:,.2f}<br>' +
                    '<extra></extra>'
                )
            ))
        
        # Add horizontal line at $10,000 (starting capital)
        fig.add_hline(
            y=10000,
            line_dash="dash",
            line_color="#CCCCCC",
            line_width=1,
            annotation_text="Starting Capital: $10,000",
            annotation_position="right",
            annotation_font_size=11,
            annotation_font_color="#666666"
        )
        
        # Professional chart styling - optimizado para Replit
        fig.update_layout(
            height=450,
            margin=dict(l=0, r=0, t=5, b=0),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(
                family='Inter, sans-serif',
                size=12,
                color='#111111'
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='#F0F0F0',
                gridwidth=1,
                showline=True,
                linewidth=1,
                linecolor='#E5E5E5',
                tickfont=dict(size=11, color='#666666')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#F0F0F0',
                gridwidth=1,
                showline=True,
                linewidth=1,
                linecolor='#E5E5E5',
                tickfont=dict(size=11, color='#666666'),
                tickformat='$,.0f'
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#E5E5E5',
                borderwidth=1,
                font=dict(size=11)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter, sans-serif",
                bordercolor="#E5E5E5"
            )
        )
        
        st.plotly_chart(fig, width='stretch', config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        })
        
        # Status text
        st.markdown(
            '<div class="footer-text">Alpha Arena Season 1 is now over, as of Nov 3rd, 2025 5 p.m. EST<br>Season 1.5 coming soon</div>',
            unsafe_allow_html=True
        )

    with info_col:
        st.markdown('<div class="info-panel">', unsafe_allow_html=True)
        
        # A Better Benchmark section
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown('<div class="info-title">A Better Benchmark</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-text"><strong>Alpha Arena</strong> is the first benchmark designed to measure '
            'AI\'s investing abilities. Each model is given <strong>$10,000 of real money</strong>, in real markets, '
            'with <strong>identical prompts and input data</strong>.</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="info-text">Our goal with Alpha Arena is to make benchmarks more like the real world, '
            'and markets are perfect for this. They\'re dynamic, adversarial, open-ended, and endlessly unpredictable.</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="info-text"><strong>Markets are the ultimate test of intelligence.</strong></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="info-text">So we need to train models with new architectures for investing, '
            'or see LLMs good enough let\'s find out.</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # The Contestants section
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown('<div class="info-title">The Contestants</div>', unsafe_allow_html=True)
        
        # Sort AIs by current value
        sorted_ais = sorted(
            historical_data.items(),
            key=lambda x: x[1]['current'],
            reverse=True
        )
        
        for ai_name, data in sorted_ais:
            color = AI_COLORS[ai_name]
            pnl = data['pnl_pct']
            pnl_sign = '+' if pnl >= 0 else ''
            
            st.markdown(f"""
            <div class="ai-item">
                <div class="ai-name-badge">
                    <div class="ai-color-dot" style="background: {color};"></div>
                    <span class="ai-name">{ai_name}</span>
                </div>
                <span class="ai-value">${data['current']:,.0f} ({pnl_sign}{pnl:.1f}%)</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Competition Rules section
        st.markdown('<div class="info-section">', unsafe_allow_html=True)
        st.markdown('<div class="info-title">Competition Rules</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="rule-item"><strong>Starting Capital:</strong> Each model gets $10,000 of real money</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rule-item"><strong>Market:</strong> Crypto perpetuals on Hyperliquid</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rule-item"><strong>Objective:</strong> Maximize risk-adjusted returns</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rule-item"><strong>Transparency:</strong> All model outputs and their corresponding trades are public</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="rule-item"><strong>Autonomy:</strong> Each AI must produce alpha, size trades, and manage risk</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Other views
elif st.session_state.current_view == 'LEADERBOARD':
    st.markdown('<div class="chart-title">AI PERFORMANCE LEADERBOARD</div>', unsafe_allow_html=True)
    
    # Sort AIs by current value
    sorted_ais = sorted(
        historical_data.items(),
        key=lambda x: x[1]['current'],
        reverse=True
    )
    
    for idx, (ai_name, data) in enumerate(sorted_ais):
        color = AI_COLORS[ai_name]
        pnl = data['pnl_pct']
        pnl_sign = '+' if pnl >= 0 else ''
        
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        with col1:
            st.markdown(f'<div style="font-size: 2rem; font-weight: 700; color: #111;">#{idx+1}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="display: flex; align-items: center; gap: 0.5rem;"><div style="width: 16px; height: 16px; border-radius: 50%; background: {color};"></div><span style="font-size: 1.25rem; font-weight: 600;">{ai_name}</span></div>', unsafe_allow_html=True)
        with col3:
            st.metric("Account Value", f"${data['current']:,.0f}")
        with col4:
            st.metric("P&L", f"{pnl_sign}{pnl:.1f}%")
        st.divider()

elif st.session_state.current_view == 'BLOG':
    st.markdown('<div class="chart-title">ALPHA ARENA BLOG</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 2rem;">
        <h2 style="color: #111;">Coming Soon</h2>
        <p style="color: #666; font-size: 1.1rem;">Stay tuned for insights, analysis, and updates on the AI trading competition.</p>
        <ul style="color: #444; font-size: 1rem; line-height: 1.8;">
            <li>Deep dives into AI trading strategies</li>
            <li>Weekly performance analysis</li>
            <li>Market insights and predictions</li>
            <li>Behind the scenes of Alpha Arena</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_view == 'MODELS':
    st.markdown('<div class="chart-title">AI MODELS</div>', unsafe_allow_html=True)
    
    for ai_name, color in AI_COLORS.items():
        data = historical_data[ai_name]
        pnl = data['pnl_pct']
        pnl_sign = '+' if pnl >= 0 else ''
        
        with st.expander(f"**{ai_name}** - ${data['current']:,.0f} ({pnl_sign}{pnl:.1f}%)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Current Performance**")
                st.metric("Account Value", f"${data['current']:,.0f}")
                st.metric("Profit/Loss", f"{pnl_sign}{pnl:.1f}%")
            with col2:
                st.markdown("**Model Info**")
                st.write(f"Color: 🟣" if ai_name == "ChatGPT" else "🔵" if ai_name == "Gemini" else "🟠" if ai_name == "Deepseek" else "🟢" if ai_name == "Qwen" else "🔷")
                st.write(f"Starting Capital: $10,000")
            st.markdown("---")
            st.markdown("**30-Day Performance Chart**")
            mini_fig = go.Figure()
            mini_fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['values'],
                mode='lines',
                line=dict(color=color, width=2),
                fill='tozeroy',
                fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}'
            ))
            mini_fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=True, gridcolor='#F0F0F0'),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            st.plotly_chart(mini_fig, width='stretch')