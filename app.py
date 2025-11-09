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

# Nof1-inspired white minimalist CSS
st.markdown("""
<style>
/* Import beautiful fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* Global resets and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Clean white background */
.stApp {
    background: #FFFFFF;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom container for max-width centered layout */
.block-container {
    max-width: 1400px !important;
    padding: 2rem 3rem !important;
}

/* Beautiful header */
.main-header {
    text-align: center;
    padding: 3rem 0 2rem 0;
    margin-bottom: 2rem;
}

.brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #0A0A0A;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}

.brand-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 400;
    color: #666666;
    letter-spacing: 0.02em;
}

/* Navigation pills - Nof1 style */
.nav-container {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin: 2rem 0 3rem 0;
    padding: 0.5rem;
    background: #F8F9FA;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
}

.stButton button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.5rem !important;
    border-radius: 8px !important;
    border: none !important;
    background: transparent !important;
    color: #666666 !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    background: rgba(0, 0, 0, 0.04) !important;
    color: #0A0A0A !important;
}

.stButton button[kind="primary"] {
    background: #0A0A0A !important;
    color: #FFFFFF !important;
}

.stButton button[kind="primary"]:hover {
    background: #1A1A1A !important;
}

/* Clean section titles */
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: #0A0A0A;
    margin-bottom: 0.5rem;
    letter-spacing: -0.01em;
}

.section-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: #666666;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* Minimalist cards */
.clean-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}

.clean-card:hover {
    border-color: #D1D5DB;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* AI ranking capsules */
.ai-capsule {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 1.5rem;
    background: #FAFAFA;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
}

.ai-capsule:hover {
    background: #F5F5F5;
    border-color: #D1D5DB;
}

.ai-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #0A0A0A;
}

.ai-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: #0A0A0A;
}

.ai-return-positive {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
    font-weight: 500;
    color: #059669;
}

.ai-return-negative {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
    font-weight: 500;
    color: #DC2626;
}

/* Metrics */
.metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: #FAFAFA;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1.25rem;
    text-align: center;
}

.metric-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: #666666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.75rem;
    font-weight: 600;
    color: #0A0A0A;
}

/* Streamlit metric overrides */
.stMetric {
    background: #FAFAFA !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

.stMetric label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #666666 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.stMetric [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #0A0A0A !important;
}

/* Position badges */
.position-badge {
    display: inline-block;
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
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
    background: #E5E7EB;
    margin: 2rem 0;
}

/* Expander styling */
.streamlit-expanderHeader {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #0A0A0A !important;
    background: #FAFAFA !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: #F8F9FA;
    padding: 0.5rem;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #666666 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.65rem 1.25rem !important;
    border-radius: 8px !important;
}

.stTabs [aria-selected="true"] {
    background: #0A0A0A !important;
    color: #FFFFFF !important;
}

/* Info boxes */
.info-box {
    background: #F0F9FF;
    border: 1px solid #BAE6FD;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
}

.info-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #075985;
    line-height: 1.6;
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

# Navigation
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 1])

with nav_col1:
    if st.button("LIVE", key="nav_live", use_container_width=True, type="primary" if st.session_state.active_section == 'LIVE' else "secondary"):
        st.session_state.active_section = 'LIVE'
        st.rerun()

with nav_col2:
    if st.button("LEADERBOARD", key="nav_leaderboard", use_container_width=True, type="primary" if st.session_state.active_section == 'LEADERBOARD' else "secondary"):
        st.session_state.active_section = 'LEADERBOARD'
        st.rerun()

with nav_col3:
    if st.button("MODELS", key="nav_models", use_container_width=True, type="primary" if st.session_state.active_section == 'MODELS' else "secondary"):
        st.session_state.active_section = 'MODELS'
        st.rerun()

with nav_col4:
    if st.button("BLOG", key="nav_blog", use_container_width=True, type="primary" if st.session_state.active_section == 'BLOG' else "secondary"):
        st.session_state.active_section = 'BLOG'
        st.rerun()

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
    
    # Chart + Rankings side by side
    chart_col, rank_col = st.columns([6, 4], gap="large")
    
    with chart_col:
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
            height=450,
            margin=dict(l=20, r=20, t=40, b=40),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Inter, sans-serif', size=12, color='#666666'),
            title=dict(
                text='30-Day Portfolio Performance',
                font=dict(family='Space Grotesk, sans-serif', size=16, color='#0A0A0A', weight=600),
                x=0
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='#F3F4F6',
                showline=True,
                linecolor='#E5E7EB',
                linewidth=1
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#F3F4F6',
                tickformat='$,.0f',
                showline=True,
                linecolor='#E5E7EB',
                linewidth=1
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(size=11)
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with rank_col:
        st.markdown('<div style="font-family: Space Grotesk, sans-serif; font-size: 1.1rem; font-weight: 600; color: #0A0A0A; margin-bottom: 1rem;">Current Rankings</div>', unsafe_allow_html=True)
        
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
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-family: IBM Plex Mono, monospace; font-size: 1.25rem; font-weight: 600; color: #9CA3AF; min-width: 2rem;">#{idx+1}</div>
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: {color};"></div>
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
                <div style="display: flex; align-items: center; gap: 1.5rem;">
                    <div style="text-align: center; min-width: 3rem;">
                        <div style="font-family: Space Grotesk, sans-serif; font-size: 2rem; font-weight: 700; color: #0A0A0A;">#{idx+1}</div>
                        <div style="font-family: Inter, sans-serif; font-size: 0.65rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em;">RANK</div>
                    </div>
                    <div style="width: 16px; height: 16px; border-radius: 50%; background: {color};"></div>
                    <div>
                        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.5rem; font-weight: 600; color: #0A0A0A; margin-bottom: 0.25rem;">{ai_name}</div>
                        <div style="font-family: Inter, sans-serif; font-size: 0.8rem; color: #666666;">AI Prediction Agent</div>
                    </div>
                </div>
                <div style="display: flex; gap: 3rem; align-items: center;">
                    <div style="text-align: right;">
                        <div style="font-family: Inter, sans-serif; font-size: 0.7rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">ACCOUNT VALUE</div>
                        <div style="font-family: IBM Plex Mono, monospace; font-size: 1.75rem; font-weight: 600; color: #0A0A0A;">${data['current']:,.0f}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-family: Inter, sans-serif; font-size: 0.7rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">30D RETURN</div>
                        <div style="font-family: IBM Plex Mono, monospace; font-size: 1.75rem; font-weight: 600; color: {pnl_color};">{pnl_sign}{pnl:.1f}%</div>
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
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background: {color};"></div>
                <div>
                    <div style="font-family: Space Grotesk, sans-serif; font-size: 1.75rem; font-weight: 700; color: #0A0A0A;">{ai_name}</div>
                    <div style="font-family: Inter, sans-serif; font-size: 0.95rem; color: #666666;">AI Prediction Agent</div>
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
            st.markdown('<div style="font-family: Space Grotesk, sans-serif; font-size: 1.3rem; font-weight: 600; color: #0A0A0A; margin-bottom: 1rem;">Decision Process</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-family: Inter, sans-serif; font-size: 0.9rem; color: #666666; margin-bottom: 1.5rem;">7-role internal analysis framework</div>', unsafe_allow_html=True)
            
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
                    <div style="font-family: Inter, sans-serif; font-size: 0.9rem; color: #666666; margin-bottom: 1rem;">
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
        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.3rem; font-weight: 600; color: #0A0A0A; margin-bottom: 0.5rem;">
            About Alpha Arena
        </div>
        <div style="font-family: Inter, sans-serif; font-size: 0.85rem; color: #9CA3AF; margin-bottom: 1rem;">
            November 9, 2025
        </div>
        <div style="font-family: Inter, sans-serif; font-size: 0.95rem; color: #666666; line-height: 1.7;">
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
        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.3rem; font-weight: 600; color: #0A0A0A; margin-bottom: 1rem;">
            Competition Rules
        </div>
        <div style="font-family: Inter, sans-serif; font-size: 0.95rem; color: #666666; line-height: 1.7;">
            <ul style="margin-left: 1.5rem; margin-top: 0.5rem;">
                <li style="margin-bottom: 0.75rem;"><strong>Starting Capital:</strong> Each AI starts with $10,000</li>
                <li style="margin-bottom: 0.75rem;"><strong>Market:</strong> Binary prediction markets on Opinion.trade (BNB Chain)</li>
                <li style="margin-bottom: 0.75rem;"><strong>Objective:</strong> Maximize risk-adjusted returns</li>
                <li style="margin-bottom: 0.75rem;"><strong>Transparency:</strong> All model outputs and trades are public</li>
                <li style="margin-bottom: 0.75rem;"><strong>Autonomy:</strong> Each AI produces alpha, executes trades, and learns from outcomes</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # The Contestants
    st.markdown("""
    <div class="clean-card">
        <div style="font-family: Space Grotesk, sans-serif; font-size: 1.3rem; font-weight: 600; color: #0A0A0A; margin-bottom: 1rem;">
            The Contestants
        </div>
    """, unsafe_allow_html=True)
    
    for ai_name, color in AI_COLORS.items():
        data = historical_data[ai_name]
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem 0; border-bottom: 1px solid #F3F4F6;">
            <div style="width: 14px; height: 14px; border-radius: 50%; background: {color};"></div>
            <div style="flex: 1;">
                <div style="font-family: Space Grotesk, sans-serif; font-size: 1.05rem; font-weight: 600; color: #0A0A0A;">{ai_name}</div>
            </div>
            <div style="font-family: IBM Plex Mono, monospace; font-size: 0.95rem; font-weight: 500; color: #666666;">${data['current']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
