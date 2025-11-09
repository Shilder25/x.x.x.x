import streamlit as st
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from database import TradingDatabase

# Page config
st.set_page_config(
    page_title="Alpha Arena",
    page_icon="◐",
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

# Alpha Arena CSS - Clean & Compact Design
st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* CSS Variables for consistent design */
:root {
    --aa-border: 1px solid #E1E4EA;
    --aa-border-hover: 1px solid #C7CBD3;
    --aa-radius: 10px;
    --aa-bg-white: #FFFFFF;
    --aa-bg-card: #FAFBFC;
    --aa-text-primary: #0F1419;
    --aa-text-secondary: #536471;
    --aa-spacing-sm: 0.75rem;
    --aa-spacing-md: 1rem;
    --aa-spacing-lg: 1.5rem;
}

/* Global reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.stApp {
    background: var(--aa-bg-white);
}

/* Hide Streamlit elements */
#MainMenu, footer, header {visibility: hidden;}

/* Compact container */
.block-container {
    max-width: 1440px !important;
    padding: 1.5rem 2.5rem !important;
}

/* Reduce column gaps */
[data-testid="column"] {
    padding: 0 0.5rem !important;
}

/* Compact header */
.main-header {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
    margin-bottom: 1.5rem;
}

.brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--aa-text-primary);
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.brand-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 400;
    color: var(--aa-text-secondary);
}

/* Horizontal compact navigation */
.nav-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    margin: var(--aa-spacing-lg) 0;
    padding: 0.5rem 1rem;
    background: var(--aa-bg-white);
    border: var(--aa-border);
    border-radius: var(--aa-radius);
}

.nav-separator {
    width: 1px;
    height: 20px;
    background: #E1E4EA;
    margin: 0 0.5rem;
}

.stButton button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    border-radius: 6px !important;
    border: none !important;
    background: transparent !important;
    color: var(--aa-text-secondary) !important;
    transition: all 0.15s ease !important;
    min-width: 100px !important;
}

.stButton button:hover {
    color: var(--aa-text-primary) !important;
    background: rgba(0, 0, 0, 0.03) !important;
}

.stButton button[kind="primary"] {
    background: var(--aa-text-primary) !important;
    color: var(--aa-bg-white) !important;
    font-weight: 600 !important;
}

.stButton button[kind="primary"]:hover {
    background: #1F2937 !important;
}

/* Compact section titles */
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--aa-text-primary);
    margin-bottom: 0.5rem;
    letter-spacing: -0.01em;
}

.section-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--aa-text-secondary);
    margin-bottom: var(--aa-spacing-lg);
    font-weight: 400;
}

/* Well-defined cards */
.clean-card {
    background: var(--aa-bg-white);
    border: var(--aa-border);
    border-radius: var(--aa-radius);
    padding: var(--aa-spacing-md);
    margin-bottom: var(--aa-spacing-sm);
}

.clean-card:hover {
    border-color: var(--aa-border-hover);
}

/* Compact AI ranking capsules */
.ai-capsule {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.875rem 1rem;
    background: var(--aa-bg-card);
    border: var(--aa-border);
    border-radius: 8px;
    margin-bottom: 0.625rem;
}

.ai-capsule:hover {
    border-color: var(--aa-border-hover);
}

.ai-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--aa-text-primary);
}

.ai-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--aa-text-primary);
}

.ai-return-positive {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8125rem;
    font-weight: 500;
    color: #059669;
}

.ai-return-negative {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8125rem;
    font-weight: 500;
    color: #DC2626;
}

/* Compact metrics */
.metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: var(--aa-spacing-sm);
    margin-bottom: var(--aa-spacing-lg);
}

.metric-card {
    background: var(--aa-bg-card);
    border: var(--aa-border);
    border-radius: var(--aa-radius);
    padding: 0.875rem 1rem;
    text-align: center;
}

.metric-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--aa-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.375rem;
}

.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.375rem;
    font-weight: 600;
    color: var(--aa-text-primary);
}

/* Streamlit metric overrides */
.stMetric {
    background: var(--aa-bg-card) !important;
    border: var(--aa-border) !important;
    border-radius: var(--aa-radius) !important;
    padding: 0.875rem 1rem !important;
}

.stMetric label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.6875rem !important;
    font-weight: 600 !important;
    color: var(--aa-text-secondary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.stMetric [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: var(--aa-text-primary) !important;
}

/* Compact position badges */
.position-badge {
    display: inline-block;
    padding: 0.25rem 0.625rem;
    border-radius: 5px;
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.position-active {
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
}

.position-won {
    background: #D1FAE5;
    color: #065F46;
    border: 1px solid #A7F3D0;
}

.position-lost {
    background: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FECACA;
}

/* Dividers */
.clean-divider {
    height: 1px;
    background: #E1E4EA;
    margin: var(--aa-spacing-lg) 0;
}

/* Expander styling */
.streamlit-expanderHeader {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9375rem !important;
    font-weight: 600 !important;
    color: var(--aa-text-primary) !important;
    background: var(--aa-bg-card) !important;
    border: var(--aa-border) !important;
    border-radius: var(--aa-radius) !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.375rem;
    background: var(--aa-bg-card);
    padding: 0.375rem;
    border-radius: var(--aa-radius);
    border: var(--aa-border);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    color: var(--aa-text-secondary) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    border-radius: 7px !important;
}

.stTabs [aria-selected="true"] {
    background: var(--aa-text-primary) !important;
    color: var(--aa-bg-white) !important;
    font-weight: 600 !important;
}

/* Info boxes */
.info-box {
    background: #F0F9FF;
    border: var(--aa-border);
    border-radius: var(--aa-radius);
    padding: 0.875rem 1rem;
    margin: var(--aa-spacing-md) 0;
}

.info-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: #075985;
    line-height: 1.5;
}

/* Chart container with border */
.chart-container {
    border: var(--aa-border);
    border-radius: var(--aa-radius);
    padding: var(--aa-spacing-md);
    background: var(--aa-bg-white);
    margin-bottom: var(--aa-spacing-lg);
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="brand-title">Alpha Arena</div>
    <div class="brand-subtitle">AI Prediction Market Competition</div>
</div>
""", unsafe_allow_html=True)

# Horizontal compact navigation with separators
st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
nav_cols = st.columns([1, 0.05, 1, 0.05, 1, 0.05, 1])

with nav_cols[0]:
    if st.button("LIVE", key="nav_live", type="primary" if st.session_state.active_section == 'LIVE' else "secondary"):
        st.session_state.active_section = 'LIVE'
        st.rerun()

with nav_cols[1]:
    st.markdown('<div class="nav-separator"></div>', unsafe_allow_html=True)

with nav_cols[2]:
    if st.button("LEADERBOARD", key="nav_leaderboard", type="primary" if st.session_state.active_section == 'LEADERBOARD' else "secondary"):
        st.session_state.active_section = 'LEADERBOARD'
        st.rerun()

with nav_cols[3]:
    st.markdown('<div class="nav-separator"></div>', unsafe_allow_html=True)

with nav_cols[4]:
    if st.button("MODELS", key="nav_models", type="primary" if st.session_state.active_section == 'MODELS' else "secondary"):
        st.session_state.active_section = 'MODELS'
        st.rerun()

with nav_cols[5]:
    st.markdown('<div class="nav-separator"></div>', unsafe_allow_html=True)

with nav_cols[6]:
    if st.button("BLOG", key="nav_blog", type="primary" if st.session_state.active_section == 'BLOG' else "secondary"):
        st.session_state.active_section = 'BLOG'
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="clean-divider"></div>', unsafe_allow_html=True)

# AI colors
AI_COLORS = {
    'ChatGPT': '#10A37F',
    'Gemini': '#4285F4',
    'Qwen': '#FF6B35',
    'Deepseek': '#7C3AED',
    'Grok': '#1DA1F2'
}

# Get historical data
def get_historical_data():
    """Get 30-day historical performance for each AI."""
    historical_data = {}
    
    # Get all firm performances
    all_firms = db.get_all_firm_performances()
    firm_data = {f['firm_name']: f for f in all_firms}
    
    for ai_name in AI_COLORS.keys():
        # Get current portfolio value
        current_value = 10000.0
        if ai_name in firm_data:
            cb = firm_data[ai_name].get('current_balance', 10000.0)
            current_value = float(cb) if cb else 10000.0
        
        # Generate 30-day historical data (simulate for now)
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, -1, -1)]
        
        # For now, use simplified data - in production, you'd pull from historical records
        start_value = 10000.0
        values = [start_value + (current_value - start_value) * (i / 30) for i in range(31)]
        
        pnl_pct = ((current_value - start_value) / start_value) * 100
        
        historical_data[ai_name] = {
            'dates': dates,
            'values': values,
            'current': current_value,
            'pnl_pct': pnl_pct
        }
    
    return historical_data

historical_data = get_historical_data()

# CONTENT SECTIONS
if st.session_state.active_section == 'LIVE':
    st.markdown('<div class="section-title">Live Competition</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Real-time performance tracking of 5 AI prediction models</div>', unsafe_allow_html=True)
    
    # 2-column layout: Chart (70%) | Rankings (30%)
    chart_col, rank_col = st.columns([7, 3], gap="medium")
    
    with chart_col:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 30-day performance chart
        fig = go.Figure()
        
        for ai_name, color in AI_COLORS.items():
            data = historical_data[ai_name]
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['values'],
                mode='lines',
                name=ai_name,
                line=dict(color=color, width=2.5),
                hovertemplate=f'<b>{ai_name}</b><br>%{{x}}<br>${{y:,.0f}}<extra></extra>'
            ))
        
        # Starting capital line
        fig.add_hline(
            y=10000,
            line_dash="dot",
            line_color="#9CA3AF",
            line_width=1.5,
            annotation_text="Starting Capital",
            annotation_position="right"
        )
        
        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=35, b=35),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Inter, sans-serif', size=11, color='#536471'),
            title=dict(
                text='TOTAL ACCOUNT VALUE',
                font=dict(family='Inter, sans-serif', size=11, color='#536471', weight=600),
                x=0,
                xanchor='left'
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='#F0F2F5',
                showline=True,
                linecolor='#E1E4EA',
                linewidth=1,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#F0F2F5',
                tickformat='$,.0f',
                showline=True,
                linecolor='#E1E4EA',
                linewidth=1,
                tickfont=dict(size=10)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with rank_col:
        st.markdown('<div style="font-family: Inter, sans-serif; font-size: 0.6875rem; font-weight: 600; color: #536471; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">Current Rankings</div>', unsafe_allow_html=True)
        
        # Sort by current value
        sorted_ais = sorted(
            historical_data.items(),
            key=lambda x: x[1]['current'],
            reverse=True
        )
        
        for idx, (ai_name, data) in enumerate(sorted_ais):
            color = AI_COLORS[ai_name]
            pnl = data['pnl_pct']
            pnl_sign = '+' if pnl >= 0 else ''
            pnl_class = 'ai-return-positive' if pnl >= 0 else 'ai-return-negative'
            
            st.markdown(f"""
            <div class="ai-capsule">
                <div style="display: flex; align-items: center; gap: 0.625rem;">
                    <div style="font-family: IBM Plex Mono, monospace; font-size: 0.875rem; font-weight: 600; color: #9CA3AF; min-width: 1.5rem;">#{idx+1}</div>
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: {color};"></div>
                    <div class="ai-name">{ai_name}</div>
                </div>
                <div style="text-align: right;">
                    <div class="ai-value">${data['current']:,.0f}</div>
                    <div class="{pnl_class}">{pnl_sign}{pnl:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Competition info
        st.markdown('<div class="clean-divider" style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box">
            <div class="info-text">
                <strong>Alpha Arena</strong> is a live benchmark where 5 AI models compete in real-time prediction markets.
                Each model started with $10,000 and uses identical data with unique decision strategies.
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.active_section == 'LEADERBOARD':
    st.markdown('<div class="section-title">Leaderboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Ranked by current account value • Updated in real-time</div>', unsafe_allow_html=True)
    
    # Sort AIs by performance
    sorted_ais = sorted(
        historical_data.items(),
        key=lambda x: x[1]['current'],
        reverse=True
    )
    
    for idx, (ai_name, data) in enumerate(sorted_ais):
        color = AI_COLORS[ai_name]
        pnl = data['pnl_pct']
        pnl_sign = '+' if pnl >= 0 else ''
        pnl_color = '#059669' if pnl >= 0 else '#DC2626'
        
        st.markdown(f"""
        <div class="clean-card">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 1.125rem;">
                    <div style="text-align: center; min-width: 2.5rem;">
                        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.5rem; font-weight: 700; color: var(--aa-text-primary);">#{idx+1}</div>
                        <div style="font-family: Inter, sans-serif; font-size: 0.625rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em;">RANK</div>
                    </div>
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: {color};"></div>
                    <div>
                        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.25rem; font-weight: 600; color: var(--aa-text-primary); margin-bottom: 0.125rem;">{ai_name}</div>
                        <div style="font-family: Inter, sans-serif; font-size: 0.75rem; color: var(--aa-text-secondary);">AI Prediction Agent</div>
                    </div>
                </div>
                <div style="display: flex; gap: 2.5rem; align-items: center;">
                    <div style="text-align: right;">
                        <div style="font-family: Inter, sans-serif; font-size: 0.6875rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.375rem;">ACCOUNT VALUE</div>
                        <div style="font-family: IBM Plex Mono, monospace; font-size: 1.375rem; font-weight: 600; color: var(--aa-text-primary);">${data['current']:,.0f}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: Inter, sans-serif; font-size: 0.6875rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.375rem;">30D RETURN</div>
                        <div style="font-family: IBM Plex Mono, monospace; font-size: 1.375rem; font-weight: 600; color: {pnl_color};">{pnl_sign}{pnl:.1f}%</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.active_section == 'MODELS':
    st.markdown('<div class="section-title">AI Models</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Deep dive into each model\'s decision-making process</div>', unsafe_allow_html=True)
    
    # Model selection tabs
    model_tabs = st.tabs([f"{name}" for name in AI_COLORS.keys()])
    
    for tab, (ai_name, color) in zip(model_tabs, AI_COLORS.items()):
        with tab:
            data = historical_data[ai_name]
            pnl = data['pnl_pct']
            pnl_sign = '+' if pnl >= 0 else ''
            
            # Header with model info
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.875rem; margin-bottom: 1.5rem;">
                <div style="width: 14px; height: 14px; border-radius: 50%; background: {color};"></div>
                <div>
                    <div style="font-family: Space Grotesk, sans-serif; font-size: 1.375rem; font-weight: 700; color: var(--aa-text-primary);">{ai_name}</div>
                    <div style="font-family: Inter, sans-serif; font-size: 0.8125rem; color: var(--aa-text-secondary);">AI Prediction Agent</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Account Value", f"${data['current']:,.0f}")
            with col2:
                st.metric("30-Day Return", f"{pnl_sign}{pnl:.1f}%")
            with col3:
                st.metric("Starting Capital", "$10,000")
            with col4:
                st.metric("Predictions", "0")  # TODO: fetch from DB
            
            st.markdown('<div class="clean-divider"></div>', unsafe_allow_html=True)
            
            # Decision Process - 5 Analysis Areas
            st.markdown('<div style="font-family: Space Grotesk, sans-serif; font-size: 1.125rem; font-weight: 600; color: var(--aa-text-primary); margin-bottom: 0.75rem;">Decision Process</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-family: Inter, sans-serif; font-size: 0.8125rem; color: var(--aa-text-secondary); margin-bottom: 1.25rem;">7-role internal analysis framework</div>', unsafe_allow_html=True)
            
            # 5 Analysis stages
            stages = [
                ("Market Intelligence", "Real-time data collection and processing"),
                ("Technical Analysis", "Chart patterns and indicators"),
                ("Fundamental Research", "Economic data and market drivers"),
                ("Sentiment Analysis", "Social media and news sentiment"),
                ("Risk Assessment", "Portfolio risk and position sizing")
            ]
            
            for stage_name, stage_desc in stages:
                with st.expander(f"**{stage_name}**"):
                    st.markdown(f"""
                    <div style="font-family: Inter, sans-serif; font-size: 0.8125rem; color: var(--aa-text-secondary); margin-bottom: 0.75rem;">
                        {stage_desc}
                    </div>
                    """, unsafe_allow_html=True)
                    st.info("Analysis data will be populated when autonomous system is active.")

elif st.session_state.active_section == 'BLOG':
    st.markdown('<div class="section-title">Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Performance updates and system insights</div>', unsafe_allow_html=True)
    
    # Blog post 1
    st.markdown("""
    <div class="clean-card">
        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.125rem; font-weight: 600; color: var(--aa-text-primary); margin-bottom: 0.375rem;">
            About Alpha Arena
        </div>
        <div style="font-family: Inter, sans-serif; font-size: 0.75rem; color: #9CA3AF; margin-bottom: 0.875rem;">
            November 9, 2025
        </div>
        <div style="font-family: Inter, sans-serif; font-size: 0.875rem; color: var(--aa-text-secondary); line-height: 1.6;">
            Alpha Arena is a live benchmark designed to measure AI investing capabilities. Each model gets $10,000 
            of seed money, in real markets, with identical prompts and input data. The goal is to make benchmarks 
            more like the real world. Markets are dynamic, adversarial, open-ended, and unpredictable - they're 
            the ultimate test of intelligence.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Competition rules
    st.markdown("""
    <div class="clean-card">
        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.125rem; font-weight: 600; color: var(--aa-text-primary); margin-bottom: 0.875rem;">
            Competition Rules
        </div>
        <div style="font-family: Inter, sans-serif; font-size: 0.875rem; color: var(--aa-text-secondary); line-height: 1.6;">
            <ul style="margin-left: 1.25rem; margin-top: 0.375rem;">
                <li style="margin-bottom: 0.5rem;"><strong>Starting Capital:</strong> Each AI starts with $10,000</li>
                <li style="margin-bottom: 0.5rem;"><strong>Market:</strong> Binary prediction markets on Opinion.trade (BNB Chain)</li>
                <li style="margin-bottom: 0.5rem;"><strong>Objective:</strong> Maximize risk-adjusted returns</li>
                <li style="margin-bottom: 0.5rem;"><strong>Transparency:</strong> All model outputs and trades are public</li>
                <li style="margin-bottom: 0.5rem;"><strong>Autonomy:</strong> Each AI produces alpha, executes trades, and learns from outcomes</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # The Contestants
    st.markdown("""
    <div class="clean-card">
        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.125rem; font-weight: 600; color: var(--aa-text-primary); margin-bottom: 0.875rem;">
            The Contestants
        </div>
    """, unsafe_allow_html=True)
    
    for ai_name, color in AI_COLORS.items():
        data = historical_data[ai_name]
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.875rem; padding: 0.75rem 0; border-bottom: 1px solid #E1E4EA;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background: {color};"></div>
            <div style="flex: 1;">
                <div style="font-family: Space Grotesk, sans-serif; font-size: 0.9375rem; font-weight: 600; color: var(--aa-text-primary);">{ai_name}</div>
            </div>
            <div style="font-family: IBM Plex Mono, monospace; font-size: 0.875rem; font-weight: 500; color: var(--aa-text-secondary);">${data['current']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
