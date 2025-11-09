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

# Alpha Arena 2.0 - Premium Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    
    /* CSS Variables - Design Tokens */
    :root {
        /* Gradients & Backgrounds */
        --bg-hero: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e293b 100%);
        --bg-surface: #1C2536;
        --bg-surface-alt: #151B28;
        --bg-card: rgba(31, 41, 55, 0.6);
        --bg-card-hover: rgba(31, 41, 55, 0.8);
        
        /* Glass Effects */
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        
        /* Accent Colors */
        --accent-red: #F2555A;
        --accent-orange: #FFB545;
        --accent-cyan: #4FD1C5;
        --accent-purple: #8B5CF6;
        --accent-blue: #38BDF8;
        
        /* Text Colors */
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-tertiary: #64748B;
        
        /* Spacing */
        --space-xs: 0.5rem;
        --space-sm: 0.75rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        
        /* Border Radius */
        --radius-sm: 6px;
        --radius-md: 12px;
        --radius-lg: 16px;
        
        /* Typography Scale */
        --text-xs: 0.75rem;
        --text-sm: 0.875rem;
        --text-base: 1rem;
        --text-lg: 1.125rem;
        --text-xl: 1.25rem;
        --text-2xl: 1.5rem;
        --text-3xl: 1.875rem;
        --text-4xl: 2.25rem;
    }
    
    /* Dark Theme Base */
    .stApp {
        background: var(--bg-hero);
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    
    /* Layout Optimization */
    .main .block-container {
        padding: var(--space-md) var(--space-lg);
        max-width: 100%;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Override Streamlit Metrics for Dark Theme */
    .stMetric label, .stMetric-label {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: var(--text-xs) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    .stMetric .metric-value, [data-testid="stMetricValue"], .stMetric-value {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: var(--text-2xl) !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    .stMetric .metric-delta, [data-testid="stMetricDelta"], .stMetric-delta {
        color: var(--text-tertiary) !important;
    }
    
    /* Text Elements */
    p, span, div {
        color: var(--text-primary);
    }
    
    /* Logo - Space Grotesk */
    .logo {
        font-family: 'Space Grotesk', sans-serif;
        font-size: var(--text-3xl);
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
    }
    
    .logo-subtitle {
        font-size: var(--text-sm);
        color: var(--text-secondary);
        font-weight: 500;
        margin-left: var(--space-sm);
    }
    
    /* Live Status Indicator */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--space-xs);
        padding: 0.375rem 0.75rem;
        background: rgba(79, 209, 197, 0.1);
        border: 1px solid rgba(79, 209, 197, 0.3);
        border-radius: 20px;
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--accent-cyan);
    }
    
    .live-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent-cyan);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Navigation Pills with Glassmorphism */
    .nav-pill {
        padding: 0.5rem 1rem;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-secondary);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .nav-pill:hover {
        background: var(--bg-card-hover);
        border-color: rgba(255, 255, 255, 0.15);
        color: var(--text-primary);
        transform: translateY(-1px);
    }
    
    .nav-pill.active {
        background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
        border-color: transparent;
        color: white;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.4);
    }
    
    /* Premium Card with Glass Effect */
    .premium-card {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        backdrop-filter: blur(20px);
        box-shadow: var(--glass-shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .premium-card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
    }
    
    /* Chart Title */
    .chart-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: var(--text-xs);
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: var(--space-md);
    }
    
    /* Performance Capsule */
    .performance-capsule {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: var(--space-md);
        margin-bottom: var(--space-md);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    
    .performance-capsule::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-purple), transparent);
    }
    
    /* AI Name Badge */
    .ai-name-badge {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    .ai-color-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        box-shadow: 0 0 12px currentColor;
    }
    
    .ai-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: var(--text-base);
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Leaderboard Card Premium */
    .leaderboard-card {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        margin-bottom: var(--space-md);
        backdrop-filter: blur(20px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .leaderboard-card::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
        transform: translate(-50%, -50%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .leaderboard-card:hover::before {
        opacity: 1;
    }
    
    .leaderboard-card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(139, 92, 246, 0.4);
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 12px 48px rgba(139, 92, 246, 0.2);
    }
    
    /* Info Panel */
    .info-panel {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        backdrop-filter: blur(20px);
    }
    
    .info-section {
        margin-bottom: var(--space-lg);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: var(--space-lg);
    }
    
    .info-section:last-child {
        margin-bottom: 0;
        border-bottom: none;
        padding-bottom: 0;
    }
    
    .info-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: var(--text-lg);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-md);
    }
    
    .info-text {
        font-size: var(--text-sm);
        line-height: 1.7;
        color: var(--text-secondary);
        margin-bottom: var(--space-sm);
    }
    
    /* AI Item */
    .ai-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--space-sm);
        margin-bottom: var(--space-xs);
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-sm);
        transition: all 0.2s;
    }
    
    .ai-item:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    .ai-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Competition Rules */
    .rule-item {
        font-size: var(--text-sm);
        color: var(--text-secondary);
        margin-bottom: var(--space-sm);
        padding-left: var(--space-md);
        position: relative;
        line-height: 1.6;
    }
    
    .rule-item:before {
        content: "▸";
        position: absolute;
        left: 0;
        color: var(--accent-purple);
        font-weight: 700;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        padding: var(--space-lg) 0;
        font-size: var(--text-xs);
        color: var(--text-tertiary);
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: var(--space-xl);
    }
    
    /* Glow Effects */
    .glow-purple {
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
    }
    
    .glow-cyan {
        box-shadow: 0 0 20px rgba(79, 209, 197, 0.5);
    }
    
    /* Smooth Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
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

# Get AI data - REAL DATA from database
def get_ai_historical_data():
    """Get historical data for all 5 AIs from real database"""
    # Check if we should refresh data (every 30 seconds with auto-refresh)
    now = datetime.now()
    should_refresh = (
        st.session_state.historical_data is None or
        (now - st.session_state.last_db_check).total_seconds() > 30
    )
    
    if not should_refresh:
        return st.session_state.historical_data
    
    # Load real data from database for all AIs
    data = {}
    for ai_name in AI_COLORS.keys():
        data[ai_name] = get_ai_real_data(ai_name)
    
    # Store in session state (persists across auto-refreshes)
    st.session_state.historical_data = data
    st.session_state.historical_data_initialized = True
    st.session_state.last_db_check = now
    
    return data

def get_ai_real_data(ai_name):
    """Get real historical data for an AI from database"""
    initial_bankroll = 10000.0
    days = 30
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    try:
        # Get all bets for this AI
        bets = db.get_autonomous_bets(firm_name=ai_name, limit=1000)
        
        if not bets:
            # No bets yet, return initial bankroll
            return {
                'dates': dates,
                'values': [initial_bankroll] * days,
                'current': initial_bankroll,
                'pnl_pct': 0.0,
                'total_bets': 0,
                'total_pnl': 0.0
            }
        
        # Calculate account value over time
        values = []
        current_value = initial_bankroll
        
        # Convert bets to DataFrame for easier processing
        bets_df = pd.DataFrame(bets)
        bets_df['execution_timestamp'] = pd.to_datetime(bets_df['execution_timestamp'])
        bets_df = bets_df.sort_values('execution_timestamp')
        
        for date in dates:
            # Get bets up to this date
            bets_until_date = bets_df[bets_df['execution_timestamp'] <= date]
            
            if len(bets_until_date) == 0:
                values.append(initial_bankroll)
            else:
                # Separate resolved vs active bets
                resolved_bets = bets_until_date[bets_until_date['actual_result'].notna()]
                active_bets = bets_until_date[bets_until_date['actual_result'].isna()]
                
                # For resolved bets: contribution = profit_loss - bet_size
                # (profit_loss includes stake return, so subtract bet to get net gain/loss)
                # Win: profit_loss=$180, bet=$100 → contribution=+$80
                # Loss: profit_loss=$0, bet=$100 → contribution=-$100
                resolved_contribution = (
                    resolved_bets['profit_loss'].fillna(0) - resolved_bets['bet_size']
                ).sum()
                
                # For active bets: lock the bet_size
                active_locked = active_bets['bet_size'].sum()
                
                # Account value = initial + net gains from resolved - active locked funds
                account_value = initial_bankroll + resolved_contribution - active_locked
                values.append(max(0, account_value))  # Can't go below 0
        
        current = values[-1]
        total_pnl = current - initial_bankroll
        pnl_pct = (total_pnl / initial_bankroll) * 100
        
        return {
            'dates': dates,
            'values': values,
            'current': current,
            'pnl_pct': pnl_pct,
            'total_bets': len(bets),
            'total_pnl': total_pnl
        }
        
    except Exception as e:
        # Fallback to initial bankroll if there's an error
        print(f"Error loading data for {ai_name}: {e}")
        return {
            'dates': dates,
            'values': [initial_bankroll] * days,
            'current': initial_bankroll,
            'pnl_pct': 0.0,
            'total_bets': 0,
            'total_pnl': 0.0
        }

# Get data
historical_data = get_ai_historical_data()

# HEADER 2.0 - Premium with glassmorphism
header_col1, header_col2, header_col3 = st.columns([2, 3, 1])

with header_col1:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; padding: 0.75rem 0;">
        <span class="logo">◐ ALPHA ARENA</span>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # Navigation pills with glassmorphism effect
    st.markdown("""
    <style>
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            color: var(--text-secondary) !important;
            border-radius: 20px !important;
            font-weight: 600 !important;
            font-size: var(--text-sm) !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            backdrop-filter: blur(10px) !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
            background: var(--bg-card-hover) !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
            color: var(--text-primary) !important;
            transform: translateY(-1px) !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button[kind="primary"] {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue)) !important;
            border-color: transparent !important;
            color: white !important;
            box-shadow: 0 4px 16px rgba(139, 92, 246, 0.4) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    nav_cols = st.columns(4)
    nav_items = ['LIVE', 'LEADERBOARD', 'POSITIONS', 'MODELS']
    
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

with header_col3:
    # Live status indicator with pulsing animation
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; align-items: center; padding: 0.75rem 0;">
        <div class="live-indicator">
            <div class="live-dot"></div>
            <span>LIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="margin: 0.75rem 0; height: 1px; background: rgba(255, 255, 255, 0.05);"></div>', unsafe_allow_html=True)

# CONTENT BASED ON VIEW
if st.session_state.current_view == 'LIVE':
    # MAIN LAYOUT: Chart (60%) | Performance Capsules (40%)
    chart_col, info_col = st.columns([6, 4], gap="large")

    with chart_col:
        # Premium card wrapper for chart
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">30-DAY PORTFOLIO PERFORMANCE</div>', unsafe_allow_html=True)
        
        # Create premium dark-themed chart with glow effects
        fig = go.Figure()
        
        # Add line for each AI with thicker lines and glow
        for ai_name, color in AI_COLORS.items():
            data = historical_data[ai_name]
            
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['values'],
                mode='lines',
                name=ai_name,
                line=dict(
                    color=color,
                    width=3.5
                ),
                fill='tonexty' if list(AI_COLORS.keys()).index(ai_name) > 0 else None,
                fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.05])}',
                hovertemplate=(
                    f'<b>{ai_name}</b><br>' +
                    'Date: %{x|%b %d, %Y}<br>' +
                    'Value: $%{y:,.0f}<br>' +
                    '<extra></extra>'
                )
            ))
        
        # Add horizontal line at $10,000 (starting capital)
        fig.add_hline(
            y=10000,
            line_dash="dot",
            line_color="rgba(148, 163, 184, 0.3)",
            line_width=2,
            annotation_text="Starting Capital",
            annotation_position="right",
            annotation_font_size=10,
            annotation_font_color="#94A3B8"
        )
        
        # Dark theme styling with glassmorphism
        fig.update_layout(
            height=500,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='IBM Plex Mono, monospace',
                size=12,
                color='#94A3B8'
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.05)',
                gridwidth=1,
                showline=False,
                zeroline=False,
                tickfont=dict(size=10, color='#64748B', family='Space Grotesk, sans-serif')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.05)',
                gridwidth=1,
                showline=False,
                zeroline=False,
                tickfont=dict(size=11, color='#94A3B8', family='IBM Plex Mono, monospace'),
                tickformat='$,.0f'
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                bgcolor='rgba(31, 41, 55, 0.8)',
                bordercolor='rgba(255, 255, 255, 0.1)',
                borderwidth=1,
                font=dict(size=11, color='#F8FAFC', family='Space Grotesk, sans-serif')
            ),
            hoverlabel=dict(
                bgcolor="rgba(31, 41, 55, 0.95)",
                font_size=12,
                font_family="IBM Plex Mono, monospace",
                font_color="#F8FAFC",
                bordercolor="rgba(139, 92, 246, 0.5)"
            )
        )
        
        st.plotly_chart(fig, width='stretch', config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        })
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Status text
        st.markdown(
            '<div class="footer-text">Season 1 completed Nov 3rd, 2025 • Season 1.5 launching soon</div>',
            unsafe_allow_html=True
        )

    with info_col:
        # Performance Capsules - Top Performers
        st.markdown('<div class="chart-title">LIVE RANKINGS</div>', unsafe_allow_html=True)
        
        # Sort AIs by current value
        sorted_ais = sorted(
            historical_data.items(),
            key=lambda x: x[1]['current'],
            reverse=True
        )
        
        # Show each AI as a premium performance capsule
        for idx, (ai_name, data) in enumerate(sorted_ais):
            color = AI_COLORS[ai_name]
            pnl = data['pnl_pct']
            pnl_sign = '+' if pnl >= 0 else ''
            pnl_color = '#4FD1C5' if pnl >= 0 else '#F2555A'
            
            st.markdown(f"""
            <div class="performance-capsule" style="border-left: 3px solid {color};">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-tertiary); font-family: 'Space Grotesk', sans-serif;">#{idx+1}</div>
                        <div>
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                                <div class="ai-color-dot" style="background: {color};"></div>
                                <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 1rem; color: var(--text-primary);">{ai_name}</span>
                            </div>
                            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: var(--text-tertiary);">AI Prediction Agent</div>
                        </div>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                    <div>
                        <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; font-family: 'Space Grotesk', sans-serif;">Account Value</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">${data['current']:,.0f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; font-family: 'Space Grotesk', sans-serif;">30D Return</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: {pnl_color}; font-family: 'IBM Plex Mono', monospace;">{pnl_sign}{pnl:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # About section
        st.markdown("""
        <div class="info-panel" style="margin-top: 1.5rem;">
            <div class="info-title">About Alpha Arena</div>
            <div class="info-text">
                The first benchmark designed to measure AI investing abilities in real markets with real capital.
            </div>
            <div class="info-text">
                Each model starts with <strong>$10,000</strong> and identical data access. Performance is measured purely on risk-adjusted returns.
            </div>
            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(79, 209, 197, 0.1); border: 1px solid rgba(79, 209, 197, 0.2); border-radius: 8px;">
                <div style="font-size: 0.75rem; font-weight: 600; color: var(--accent-cyan); font-family: 'Space Grotesk', sans-serif;">MARKET</div>
                <div style="font-size: 0.875rem; color: var(--text-primary); margin-top: 0.25rem;">Prediction Markets • Opinion.trade on BNB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Other views
elif st.session_state.current_view == 'LEADERBOARD':
    st.markdown('<div class="chart-title">AI PERFORMANCE LEADERBOARD</div>', unsafe_allow_html=True)
    st.markdown('<div style="margin-bottom: 1.5rem; font-size: 0.875rem; color: var(--text-secondary);">Ranked by current account value • Updated in real-time</div>', unsafe_allow_html=True)
    
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
        pnl_color = '#4FD1C5' if pnl >= 0 else '#F2555A'
        
        # Premium leaderboard cards with glassmorphism
        st.markdown(f"""
        <div class="leaderboard-card">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 2rem;">
                <div style="display: flex; align-items: center; gap: 1.5rem; flex: 1;">
                    <div style="min-width: 4rem; text-align: center;">
                        <div style="font-size: 2.5rem; font-weight: 700; color: var(--text-primary); font-family: 'Space Grotesk', sans-serif; line-height: 1;">#{idx+1}</div>
                        <div style="font-size: 0.65rem; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem;">RANK</div>
                    </div>
                    <div style="width: 20px; height: 20px; border-radius: 50%; background: {color}; box-shadow: 0 0 16px {color}; flex-shrink: 0;"></div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 600; color: var(--text-primary); font-family: 'Space Grotesk', sans-serif; margin-bottom: 0.25rem;">{ai_name}</div>
                        <div style="font-size: 0.75rem; color: var(--text-tertiary); font-family: 'Manrope', sans-serif;">AI Prediction Agent • 30-day competition</div>
                    </div>
                </div>
                <div style="display: flex; gap: 3rem; align-items: center;">
                    <div style="text-align: right;">
                        <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; font-family: 'Space Grotesk', sans-serif;">ACCOUNT VALUE</div>
                        <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">${data['current']:,.0f}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; font-family: 'Space Grotesk', sans-serif;">30D RETURN</div>
                        <div style="font-size: 2rem; font-weight: 700; color: {pnl_color}; font-family: 'IBM Plex Mono', monospace;">{pnl_sign}{pnl:.1f}%</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_view == 'POSITIONS':
    st.markdown('<div class="chart-title">ACTIVE PREDICTIONS</div>', unsafe_allow_html=True)
    st.markdown('<div style="margin-bottom: 2rem; font-size: 0.875rem; color: var(--text-secondary);">Real-time tracking of all AI predictions and their outcomes</div>', unsafe_allow_html=True)
    
    # Get all autonomous bets from database
    all_bets = db.get_autonomous_bets(firm_name=None, limit=100)
    
    if not all_bets:
        st.markdown("""
        <div class="premium-card" style="padding: 2rem; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 600; color: var(--text-tertiary); margin-bottom: 1rem;">No active predictions yet</div>
            <div style="font-size: 1rem; color: var(--text-secondary);">AIs will start making predictions once the autonomous system is activated</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Separate active and resolved bets, sort by execution timestamp (newest first)
        active_bets = sorted(
            [bet for bet in all_bets if bet.get('actual_result') is None],
            key=lambda x: x.get('execution_timestamp', ''),
            reverse=True
        )
        resolved_bets = sorted(
            [bet for bet in all_bets if bet.get('actual_result') is not None],
            key=lambda x: x.get('resolution_timestamp', '') or x.get('execution_timestamp', ''),
            reverse=True
        )
        
        # Stats summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Bets", len(all_bets))
        with col2:
            st.metric("Active", len(active_bets))
        with col3:
            st.metric("Resolved", len(resolved_bets))
        with col4:
            total_locked = sum(bet.get('bet_size', 0) for bet in active_bets)
            st.metric("Capital Locked", f"${total_locked:,.0f}")
        
        st.markdown('<div style="margin: 1.5rem 0; height: 1px; background: rgba(255, 255, 255, 0.05);"></div>', unsafe_allow_html=True)
        
        # Tabs for active vs resolved
        tab1, tab2 = st.tabs(["🟢 ACTIVE", "✅ RESOLVED"])
        
        with tab1:
            if not active_bets:
                st.info("No active predictions at the moment")
            else:
                for bet in active_bets[:20]:  # Show latest 20
                    firm_name = bet.get('firm_name', 'Unknown')
                    color = AI_COLORS.get(firm_name, '#666666')
                    category = bet.get('category', 'general')
                    bet_size = bet.get('bet_size', 0)
                    probability = bet.get('probability', 0.5)
                    confidence = bet.get('confidence', 50)
                    event_desc = bet.get('event_description', '')[:100] + '...' if len(bet.get('event_description', '')) > 100 else bet.get('event_description', '')
                    timestamp = bet.get('execution_timestamp', '')
                    
                    st.markdown(f"""
                    <div class="premium-card" style="margin-bottom: 1rem; padding: 1.25rem; border-left: 3px solid {color};">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <div style="width: 12px; height: 12px; border-radius: 50%; background: {color}; box-shadow: 0 0 12px {color};"></div>
                                <span style="font-weight: 600; font-size: 1rem; color: var(--text-primary); font-family: 'Space Grotesk', sans-serif;">{firm_name}</span>
                                <span style="padding: 0.25rem 0.5rem; background: rgba(79, 209, 197, 0.15); border: 1px solid rgba(79, 209, 197, 0.3); border-radius: 4px; font-size: 0.65rem; font-weight: 600; color: var(--accent-cyan); text-transform: uppercase;">{category}</span>
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-tertiary); font-family: 'IBM Plex Mono', monospace;">{timestamp[:16] if timestamp else 'N/A'}</div>
                        </div>
                        <div style="margin-bottom: 0.75rem; font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">{event_desc}</div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                            <div>
                                <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 0.25rem;">BET SIZE</div>
                                <div style="font-size: 1rem; font-weight: 700; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">${bet_size:,.2f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 0.25rem;">PROBABILITY</div>
                                <div style="font-size: 1rem; font-weight: 700; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">{probability:.1%}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 0.25rem;">CONFIDENCE</div>
                                <div style="font-size: 1rem; font-weight: 700; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">{confidence}%</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            if not resolved_bets:
                st.info("No resolved predictions yet")
            else:
                for bet in resolved_bets[:20]:  # Show latest 20
                    firm_name = bet.get('firm_name', 'Unknown')
                    color = AI_COLORS.get(firm_name, '#666666')
                    category = bet.get('category', 'general')
                    bet_size = bet.get('bet_size', 0)
                    probability = bet.get('probability', 0.5)
                    profit_loss = bet.get('profit_loss', 0)
                    actual_result = bet.get('actual_result', 0)
                    event_desc = bet.get('event_description', '')[:100] + '...' if len(bet.get('event_description', '')) > 100 else bet.get('event_description', '')
                    timestamp = bet.get('execution_timestamp', '')
                    resolution_time = bet.get('resolution_timestamp', '')
                    
                    won = actual_result == 1
                    pnl_color = '#4FD1C5' if profit_loss > 0 else '#F2555A'
                    status_text = "WON" if won else "LOST"
                    status_color = '#4FD1C5' if won else '#F2555A'
                    
                    st.markdown(f"""
                    <div class="premium-card" style="margin-bottom: 1rem; padding: 1.25rem; border-left: 3px solid {color};">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <div style="width: 12px; height: 12px; border-radius: 50%; background: {color}; box-shadow: 0 0 12px {color};"></div>
                                <span style="font-weight: 600; font-size: 1rem; color: var(--text-primary); font-family: 'Space Grotesk', sans-serif;">{firm_name}</span>
                                <span style="padding: 0.25rem 0.5rem; background: rgba(79, 209, 197, 0.15); border: 1px solid rgba(79, 209, 197, 0.3); border-radius: 4px; font-size: 0.65rem; font-weight: 600; color: var(--accent-cyan); text-transform: uppercase;">{category}</span>
                                <span style="padding: 0.25rem 0.5rem; background: rgba{tuple(list(int(status_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.15])}; border: 1px solid {status_color}; border-radius: 4px; font-size: 0.65rem; font-weight: 600; color: {status_color};">{status_text}</span>
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-tertiary); font-family: 'IBM Plex Mono', monospace;">{timestamp[:16] if timestamp else 'N/A'}</div>
                        </div>
                        <div style="margin-bottom: 0.75rem; font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">{event_desc}</div>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                            <div>
                                <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 0.25rem;">BET SIZE</div>
                                <div style="font-size: 1rem; font-weight: 700; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">${bet_size:,.2f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 0.25rem;">PROBABILITY</div>
                                <div style="font-size: 1rem; font-weight: 700; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">{probability:.1%}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 0.25rem;">P&L</div>
                                <div style="font-size: 1rem; font-weight: 700; color: {pnl_color}; font-family: 'IBM Plex Mono', monospace;">${profit_loss:,.2f}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.65rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; margin-bottom: 0.25rem;">RESOLVED</div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); font-family: 'IBM Plex Mono', monospace;">{resolution_time[:16] if resolution_time else 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

elif st.session_state.current_view == 'MODELS':
    st.markdown('<div class="chart-title">AI PREDICTION MODELS</div>', unsafe_allow_html=True)
    st.markdown('<div style="margin-bottom: 2rem; font-size: 0.875rem; color: var(--text-secondary);">Detailed performance analysis for each competing model</div>', unsafe_allow_html=True)
    
    for ai_name, color in AI_COLORS.items():
        data = historical_data[ai_name]
        pnl = data['pnl_pct']
        pnl_sign = '+' if pnl >= 0 else ''
        pnl_color = '#4FD1C5' if pnl >= 0 else '#F2555A'
        
        with st.expander(f"**{ai_name}** • ${data['current']:,.0f} ({pnl_sign}{pnl:.1f}%)", expanded=False):
            # Header with AI info
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background: {color}; box-shadow: 0 0 20px {color};"></div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); font-family: 'Space Grotesk', sans-serif;">{ai_name}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">AI Prediction Agent • Real-time competition</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">CURRENT PERFORMANCE</div>', unsafe_allow_html=True)
                st.metric("Account Value", f"${data['current']:,.0f}")
                st.metric("30-Day Return", f"{pnl_sign}{pnl:.1f}%")
            with col2:
                st.markdown('<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">MODEL INFO</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="padding: 0.75rem; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 0.25rem;">Starting Capital</div>
                    <div style="font-size: 1rem; font-weight: 600; color: var(--text-primary); font-family: 'IBM Plex Mono', monospace;">$10,000</div>
                </div>
                <div style="padding: 0.75rem; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 0.25rem;">Model Color</div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background: {color};"></div>
                        <div style="font-size: 1rem; font-weight: 600; color: var(--text-primary);">{color}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div style="margin: 1.5rem 0; height: 1px; background: rgba(255, 255, 255, 0.05);"></div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.75rem; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">30-DAY PERFORMANCE CHART</div>', unsafe_allow_html=True)
            
            mini_fig = go.Figure()
            mini_fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['values'],
                mode='lines',
                line=dict(color=color, width=3),
                fill='tozeroy',
                fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.15])}'
            ))
            mini_fig.update_layout(
                height=250,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.05)',
                    showticklabels=True,
                    tickfont=dict(size=9, color='#64748B')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.05)',
                    tickformat='$,.0f',
                    tickfont=dict(size=10, color='#94A3B8', family='IBM Plex Mono')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8')
            )
            st.plotly_chart(mini_fig, width='stretch')