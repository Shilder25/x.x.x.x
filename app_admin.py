import streamlit as st
import os
from datetime import datetime
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from database import TradingDatabase
from data_collectors import AlphaVantageCollector, YFinanceCollector, RedditSentimentCollector
from llm_clients import FirmOrchestrator
from prompt_system import (
    create_trading_prompt,
    format_technical_report,
    format_fundamental_report,
    format_sentiment_report
)
from opinion_trade_api import OpinionTradeAPI
from recommendation_engine import RecommendationEngine

# Note: st.set_page_config is handled in app.py main entry point

# Premium Dark Design System with Binance Gold
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    
    /* CSS Variables - Design Tokens */
    :root {
        /* Backgrounds */
        --bg-hero: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e293b 100%);
        --bg-surface: #0F172A;
        --bg-card: rgba(30, 41, 59, 0.4);
        --bg-card-hover: rgba(30, 41, 59, 0.6);
        
        /* Binance Gold Accent System */
        --gold-primary: #F0B90B;
        --gold-glow: rgba(240, 185, 11, 0.3);
        --gold-hover: #FCD535;
        
        /* Supporting Colors (max 2-3 total) */
        --accent-teal: #0EA5E9;
        --accent-slate: #334155;
        
        /* Glass Effects */
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glass-gold-border: rgba(240, 185, 11, 0.2);
        
        /* Text Hierarchy */
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
    }
    
    /* Dark Theme Base */
    .stApp {
        background: var(--bg-hero);
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    
    .main .block-container {
        padding: var(--space-md) var(--space-lg);
        max-width: 100%;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }
    
    h1 { font-size: 2.5rem !important; letter-spacing: -0.02em; }
    h2 { font-size: 2rem !important; letter-spacing: -0.02em; }
    h3 { font-size: 1.5rem !important; }
    
    p, span, div, label {
        color: var(--text-primary) !important;
    }
    
    /* Premium Header */
    .admin-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-hover) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        text-shadow: 0 0 30px var(--gold-glow);
        margin-bottom: 0.5rem;
    }
    
    .admin-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Premium Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid var(--glass-border);
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px 12px 0 0;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.875rem;
        padding: 0 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-card-hover);
        color: var(--gold-primary);
        border-color: var(--glass-gold-border);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--bg-card);
        border: 1px solid var(--gold-primary);
        color: var(--gold-primary);
        box-shadow: 0 0 20px var(--gold-glow);
    }
    
    /* Premium Cards */
    .premium-card {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-top: 2px solid var(--gold-primary);
        border-radius: var(--radius-md);
        padding: var(--space-lg);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .premium-card:hover {
        background: var(--bg-card-hover);
        border-top-color: var(--gold-hover);
        box-shadow: 0 8px 30px var(--gold-glow), 0 4px 20px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }
    
    /* Buttons - Gold Primary */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-hover) 100%);
        border: none;
        color: #000000;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: 0 4px 15px var(--gold-glow);
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--gold-hover);
        box-shadow: 0 6px 25px var(--gold-glow);
        transform: translateY(-2px);
    }
    
    .stButton > button[kind="secondary"] {
        background: var(--glass-bg);
        border: 1px solid var(--glass-gold-border);
        color: var(--gold-primary);
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-card);
        border-color: var(--gold-primary);
        box-shadow: 0 0 15px var(--gold-glow);
    }
    
    /* Metrics - Dark Theme */
    .stMetric {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: var(--space-md);
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--gold-primary) !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    
    /* Dividers - Subtle */
    hr {
        border-color: var(--glass-border) !important;
        margin: 2rem 0;
    }
    
    /* Info/Success/Warning Boxes - Minimal */
    .stAlert {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-left: 3px solid var(--gold-primary);
        border-radius: var(--radius-md);
        color: var(--text-primary);
    }
    
    /* Expanders - Dark */
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        color: var(--text-primary) !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-card-hover);
        border-color: var(--glass-gold-border);
    }
    
    /* Dataframes - Dark */
    .stDataFrame {
        background: var(--bg-surface);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
    }
    
    /* Text Inputs - Dark */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        background: var(--bg-surface);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        border-radius: var(--radius-md);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--gold-primary);
        box-shadow: 0 0 10px var(--gold-glow);
    }
    
    /* Selectbox - Dark */
    .stSelectbox > div > div {
        background: var(--bg-surface);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
    }
    
    /* Toggle - Gold Active State */
    .stCheckbox > label {
        color: var(--text-primary) !important;
    }
    
    /* Remove emoji clutter, keep minimal */
    .minimal-icon {
        color: var(--gold-primary);
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state:
    st.session_state.db = TradingDatabase()
    
    firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
    for firm in firms:
        st.session_state.db.initialize_firm_portfolio(firm, 10000.0)

if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = FirmOrchestrator()

if 'recommender' not in st.session_state:
    st.session_state.recommender = RecommendationEngine(st.session_state.db)

if 'predictions' not in st.session_state:
    st.session_state.predictions = {}

if 'technical_data' not in st.session_state:
    st.session_state.technical_data = None

if 'fundamental_data' not in st.session_state:
    st.session_state.fundamental_data = None

if 'sentiment_data' not in st.session_state:
    st.session_state.sentiment_data = None

# Premium Header
st.markdown('<div class="admin-header">⚡ TRADINGAGENTS</div>', unsafe_allow_html=True)
st.markdown('<div class="admin-subtitle">Multi-LLM Prediction Market Framework</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Home",
    "Autonomous Competition",
    "New Prediction",
    "Transparency Panel",
    "Comparative Dashboard",
    "Recommendations",
    "Submit",
    "Results"
])

with tab1:
    st.markdown("## System Modes")
    st.markdown("Choose how you want to use the framework")
    
    st.markdown("")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #F0B90B; margin-bottom: 0.5rem;">Manual System</h3>
            <p style="color: #94A3B8; margin-bottom: 1.5rem; font-size: 0.9rem;">For analysts who want full control</p>
            
            <div style="margin-bottom: 1.5rem;">
                <p style="font-weight: 600; margin-bottom: 0.75rem; font-size: 0.875rem;">FEATURES</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Generate predictions with all 5 AIs</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Analyze technical, fundamental, sentiment data</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Visualize complete reasoning</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Compare performance and consensus</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Submit to Opinion.trade</p>
            </div>
            
            <div style="padding: 1rem; background: rgba(240, 185, 11, 0.1); border-left: 2px solid #F0B90B; border-radius: 6px; margin-bottom: 1.5rem;">
                <p style="margin: 0; font-size: 0.85rem; color: #F0B90B;">Ideal for detailed analysis and personalized decisions</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("Access Manual System", use_container_width=True, type="primary", key="goto_manual"):
            st.info("Navigate to the 'New Prediction' tab")
    
    with col2:
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #F0B90B; margin-bottom: 0.5rem;">Autonomous Competition</h3>
            <p style="color: #94A3B8; margin-bottom: 1.5rem; font-size: 0.9rem;">For observers who want to see AIs compete</p>
            
            <div style="margin-bottom: 1.5rem;">
                <p style="font-weight: 600; margin-bottom: 0.75rem; font-size: 0.875rem;">FEATURES</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ 5 AIs competing in real-time</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Each AI analyzes events automatically</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Different bankroll strategies</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Continuous adaptation system</p>
                <p style="margin: 0.5rem 0; font-size: 0.85rem;">→ Weekly learning and leaderboard</p>
            </div>
            
            <div style="padding: 1rem; background: rgba(240, 185, 11, 0.1); border-left: 2px solid #F0B90B; border-radius: 6px; margin-bottom: 1.5rem;">
                <p style="margin: 0; font-size: 0.85rem; color: #F0B90B;">Ideal for observing strategies and autonomous evolution</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        if st.button("Access Competition", use_container_width=True, type="primary", key="goto_auto"):
            st.info("Navigate to the 'Autonomous Competition' tab")
    
    st.divider()
    
    st.markdown("### Comparison")
    
    comparison_col1, comparison_col2, comparison_col3 = st.columns(3)
    
    with comparison_col1:
        st.markdown("**Control Level**")
        st.markdown("Manual: Full control")
        st.markdown("Autonomous: Observe only")
    
    with comparison_col2:
        st.markdown("**Time Required**")
        st.markdown("Manual: Active participation")
        st.markdown("Autonomous: Fully automatic")
    
    with comparison_col3:
        st.markdown("**Primary Goal**")
        st.markdown("Manual: Precise predictions")
        st.markdown("Autonomous: Research & competition")

with tab2:
    st.markdown("## Autonomous Competition")
    st.markdown("Automated betting system with continuous adaptation and weekly learning")
    
    if 'autonomous_engine' not in st.session_state:
        from autonomous_engine import AutonomousEngine
        st.session_state.autonomous_engine = AutonomousEngine(
            database=st.session_state.db,
            initial_bankroll_per_firm=1000.0,
            simulation_mode=True
        )
    
    engine = st.session_state.autonomous_engine
    status = engine.get_competition_status()
    
    st.divider()
    
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        with st.container():
            st.markdown("### Control Panel")
            
            # System ON/OFF toggle
            if 'system_enabled' not in st.session_state:
                st.session_state.system_enabled = False
            
            system_enabled = st.toggle(
                "System Status",
                value=st.session_state.system_enabled,
                key="system_enabled_toggle",
                help="Enable/disable the autonomous prediction system to control API usage"
            )
            st.session_state.system_enabled = system_enabled
            
            if system_enabled:
                st.markdown('<div style="padding: 0.75rem; background: rgba(34, 197, 94, 0.1); border-left: 3px solid #22C55E; border-radius: 6px; margin: 1rem 0;"><p style="margin: 0; color: #22C55E; font-weight: 600;">SYSTEM ACTIVE</p><p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">AIs can place predictions</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border-left: 3px solid #EF4444; border-radius: 6px; margin: 1rem 0;"><p style="margin: 0; color: #EF4444; font-weight: 600;">SYSTEM DISABLED</p><p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">No API calls will be made</p></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Simulation mode toggle (only if system is enabled)
            simulation_mode = st.toggle(
                "Simulation Mode",
                value=engine.simulation_mode,
                key="sim_mode_toggle",
                help="In simulation mode, real bets are not executed",
                disabled=not system_enabled
            )
            engine.simulation_mode = simulation_mode
            
            if simulation_mode:
                st.markdown('<div style="padding: 0.75rem; background: rgba(14, 165, 233, 0.1); border-left: 3px solid #0EA5E9; border-radius: 6px; margin: 1rem 0;"><p style="margin: 0; color: #0EA5E9; font-weight: 600;">SIMULATION MODE</p><p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">Safe testing environment</p></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border-left: 3px solid #EF4444; border-radius: 6px; margin: 1rem 0;"><p style="margin: 0; color: #EF4444; font-weight: 600;">LIVE MODE</p><p style="margin: 0; font-size: 0.85rem; color: #94A3B8;">Real bets will be executed</p></div>', unsafe_allow_html=True)
            
            st.markdown("")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("Run Cycle", use_container_width=True, type="primary", disabled=not system_enabled):
                    with st.spinner("Analyzing events and executing bets..."):
                        try:
                            result = engine.run_daily_cycle()
                            st.success(f"{result.get('total_bets_placed')} bets placed successfully")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col_btn2:
                if st.button("Refresh", use_container_width=True):
                    st.rerun()
        
        st.markdown("")
        
        with st.container():
            st.markdown("### Global Summary")
            
            total_bankroll = sum([
                firm_status['bankroll'].get('current_bankroll', 0)
                for firm_status in status.get('firms', {}).values()
            ])
            
            total_initial = sum([
                firm_status['bankroll'].get('initial_bankroll', 0)
                for firm_status in status.get('firms', {}).values()
            ])
            
            total_profit = total_bankroll - total_initial
            total_return = (total_profit / total_initial * 100) if total_initial > 0 else 0
            
            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                st.metric(
                    "Total Capital",
                    f"${total_bankroll:.2f}",
                    delta=f"${total_profit:+.2f}"
                )
            
            with metric_col2:
                st.metric(
                    "Global Return",
                    f"{total_return:+.1f}%",
                    delta=f"${total_profit:+.2f}"
                )
            
            all_bets = st.session_state.db.get_autonomous_bets(limit=1000)
            total_bets_placed = len(all_bets)
            
            resolved_bets = [b for b in all_bets if b['actual_result'] is not None]
            wins = len([b for b in resolved_bets if b['actual_result'] == 1])
            global_win_rate = (wins / len(resolved_bets) * 100) if resolved_bets else 0
            
            metric_col3, metric_col4 = st.columns(2)
            
            with metric_col3:
                st.metric("Total Bets", total_bets_placed)
            
            with metric_col4:
                st.metric("Global Win Rate", f"{global_win_rate:.1f}%")
    
    with right_col:
        with st.container():
            st.markdown("### AI Leaderboard")
            
            leaderboard = status.get('leaderboard', [])
            
            if leaderboard:
                for i, entry in enumerate(leaderboard[:5]):
                    position_display = {1: "#1", 2: "#2", 3: "#3"}.get(entry['position'], f"#{entry['position']}")
                    
                    with st.container():
                        col_pos, col_firm, col_metrics = st.columns([0.5, 1.5, 2])
                        
                        with col_pos:
                            st.markdown(f'<div style="font-size: 1.5rem; font-weight: 700; color: #F0B90B;">{position_display}</div>', unsafe_allow_html=True)
                        
                        with col_firm:
                            st.markdown(f"**{entry['firm_name']}**")
                            risk_colors = {"normal": "#22C55E", "caution": "#F59E0B", "alert": "#F97316", "critical": "#EF4444"}
                            risk_color = risk_colors.get(entry['risk_level'], "#64748B")
                            st.markdown(f'<p style="color: {risk_color}; font-size: 0.75rem; margin: 0;">{entry["risk_level"].upper()}</p>', unsafe_allow_html=True)
                        
                        with col_metrics:
                            m1, m2, m3 = st.columns(3)
                            with m1:
                                st.metric("Bankroll", f"${entry['current_bankroll']:.0f}", delta=f"${entry['total_profit']:+.0f}")
                            with m2:
                                st.metric("ROI", f"{entry['return_pct']:+.1f}%")
                            with m3:
                                st.metric("Win%", f"{entry['win_rate']:.0f}%")
                        
                        if i < len(leaderboard) - 1:
                            st.markdown("")
            else:
                st.info("Run a cycle to view the leaderboard")
    
    st.divider()
    
    with st.container():
        st.markdown("### Detailed AI Status")
        
        for firm_name, firm_status in status.get('firms', {}).items():
            with st.expander(f"{firm_name}", expanded=False):
                risk_status = firm_status['risk']
                bankroll_status = firm_status['bankroll']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    risk_level = risk_status.get('risk_level', 'normal')
                    st.metric("Status", risk_level.upper())
                
                with col2:
                    adaptation_level = risk_status.get('adaptation_level', 0)
                    st.metric("Adaptation", f"Level {adaptation_level}")
                
                with col3:
                    bankroll = bankroll_status.get('current_bankroll', 0)
                    initial = bankroll_status.get('initial_bankroll', 1000)
                    delta = bankroll - initial
                    st.metric("Bankroll", f"${bankroll:.2f}", delta=f"{delta:+.2f}")
                
                with col4:
                    win_rate = bankroll_status.get('win_rate', 0)
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                st.markdown("**Risk Parameters:**")
                current_params = risk_status.get('current_limits', {})
                
                p1, p2, p3 = st.columns(3)
                with p1:
                    st.caption(f"Max Bet: {current_params.get('max_bet_size_pct', 0)*100:.1f}%")
                with p2:
                    st.caption(f"Max Concurrent: {current_params.get('max_concurrent_bets', 0)}")
                with p3:
                    st.caption(f"Consecutive losses: {risk_status.get('consecutive_losses', 0)}")
    
    st.divider()
    
    with st.container():
        st.markdown("### Bet History")
    
        filter_firm = st.selectbox("Filter by Firm", ["All"] + list(status.get('firms', {}).keys()))
        
        if filter_firm == "All":
            bets = st.session_state.db.get_autonomous_bets(limit=50)
        else:
            bets = st.session_state.db.get_autonomous_bets(firm_name=filter_firm, limit=50)
        
        if bets:
            bets_data = []
            for bet in bets:
                result_status = "WON" if bet['actual_result'] == 1 else "LOST" if bet['actual_result'] == 0 else "PENDING"
                
                bets_data.append({
                    'Firm': bet['firm_name'],
                    'Event': bet['event_description'][:50] + "..." if len(bet['event_description']) > 50 else bet['event_description'],
                    'Amount': f"${bet['bet_size']:.2f}",
                    'Prob': f"{bet['probability']:.0%}",
                    'EV': f"{bet['expected_value']:.2f}" if bet['expected_value'] else "N/A",
                    'Status': result_status,
                    'P/L': f"${bet['profit_loss']:.2f}" if bet['profit_loss'] else "-",
                    'Date': bet['execution_timestamp'][:10]
                })
            
            df_bets = pd.DataFrame(bets_data)
            st.dataframe(df_bets, use_container_width=True, hide_index=True, height=300)
        else:
            st.info("No bets recorded. Run a cycle to begin.")
    
    st.divider()
    
    with st.container():
        st.markdown("### Strategy Adaptations")
        
        adaptations = st.session_state.db.get_strategy_adaptations()
        
        if adaptations:
            for adapt in adaptations[:5]:
                with st.expander(f"{adapt['firm_name']} - Level {adapt['adaptation_level']} ({adapt['adaptation_timestamp'][:10]})", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Bankroll", f"${adapt.get('bankroll_at_adaptation', 0):.2f}")
                    with col2:
                        st.metric("Loss", f"{adapt.get('loss_percentage', 0):.1f}%")
                    with col3:
                        st.metric("Level", adapt['adaptation_level'])
                    
                    st.markdown(f"**Reason:** {adapt['trigger_reason']}")
                    
                    if adapt.get('changes_applied'):
                        st.markdown("**Changes:**")
                        for change in adapt.get('changes_applied', []):
                            st.caption(f"• {change}")
        else:
            st.info("No adaptations recorded yet.")
    
    st.divider()
    
    with st.container():
        st.markdown("### Performance Charts")
        
        tab_chart1, tab_chart2, tab_chart3 = st.tabs(["Bankroll", "Win Rate", "Risk"])
        
        with tab_chart1:
            fig = go.Figure()
            
            for firm_name, firm_status in status.get('firms', {}).items():
                bankroll_status = firm_status['bankroll']
                fig.add_trace(go.Scatter(
                    x=[0, 1],
                    y=[bankroll_status['initial_bankroll'], bankroll_status['current_bankroll']],
                    mode='lines+markers',
                    name=firm_name,
                    line=dict(width=3),
                    marker=dict(size=10)
                ))
            
            fig.update_layout(
                title="Bankroll Evolution",
                xaxis_title="Time",
                yaxis_title="Bankroll ($)",
                hovermode='x unified',
                height=350,
                showlegend=True,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15,23,42,0.6)',
                font=dict(color='#F8FAFC', family='Manrope'),
                title_font=dict(color='#F0B90B', size=18)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_chart2:
            win_rates_data = []
            
            for firm_name, firm_status in status.get('firms', {}).items():
                bankroll_status = firm_status['bankroll']
                win_rates_data.append({
                    'Firm': firm_name,
                    'Win Rate': bankroll_status.get('win_rate', 0)
                })
            
            df_wr = pd.DataFrame(win_rates_data)
            
            fig = px.bar(df_wr, x='Firm', y='Win Rate', 
                         title="Success Rate",
                         color='Win Rate',
                         color_continuous_scale=[[0, '#EF4444'], [0.5, '#F0B90B'], [1, '#22C55E']],
                         height=350)
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15,23,42,0.6)',
                font=dict(color='#F8FAFC', family='Manrope'),
                title_font=dict(color='#F0B90B', size=18)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_chart3:
            risk_data = []
            
            for firm_name, firm_status in status.get('firms', {}).items():
                risk_status = firm_status['risk']
                risk_level = risk_status.get('risk_level', 'normal')
                
                risk_score = {'normal': 1, 'caution': 2, 'alert': 3, 'critical': 4}.get(risk_level, 1)
                
                risk_data.append({
                    'Firm': firm_name,
                    'Level': risk_level.upper(),
                    'Score': risk_score
                })
            
            df_risk = pd.DataFrame(risk_data)
            
            fig = px.bar(df_risk, x='Firm', y='Score', 
                         title="Risk Levels",
                         color='Level',
                         height=350,
                         color_discrete_map={
                         'NORMAL': '#22C55E',
                         'CAUTION': '#F59E0B',
                         'ALERT': '#F97316',
                         'CRITICAL': '#EF4444'
                     })
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15,23,42,0.6)',
                font=dict(color='#F8FAFC', family='Manrope'),
                title_font=dict(color='#F0B90B', size=18)
            )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("## Manual Prediction System")
    st.markdown("Generate predictions using the 5 LLM analysis firms")
    
    st.divider()
    
    with st.container():
        st.markdown("### Step 1: Event Configuration")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            event_description = st.text_area(
                "Prediction Event Description",
                placeholder="Ex: Apple (AAPL) will close above $200 on Dec 31, 2025 (TRUE/FALSE)",
                height=100,
                help="Clearly describe the event you want to predict"
            )
        
        with col2:
            symbol = st.text_input(
                "Symbol",
                value="AAPL",
                help="Asset ticker to analyze"
            )
            
            data_collected = sum([
                bool(st.session_state.technical_data),
                bool(st.session_state.fundamental_data),
                bool(st.session_state.sentiment_data)
            ])
            st.metric("Data Collected", f"{data_collected}/3")
    
    st.divider()
    
    with st.container():
        st.markdown("### Step 2: Market Data Collection")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.markdown("#### Technical Data")
                st.caption("Indicators and technical analysis")
                if st.session_state.technical_data:
                    st.success("✓ Data loaded")
                else:
                    st.info("Pending")
                
                if st.button("Get Technical Data", use_container_width=True, type="secondary"):
                    with st.spinner("Collecting..."):
                        alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
                        if not alpha_vantage_key:
                            st.error("⚠️ Alpha Vantage API Key not configured. Please configure it in secrets.")
                        else:
                            collector = AlphaVantageCollector(alpha_vantage_key)
                            st.session_state.technical_data = collector.get_technical_indicators(symbol)
                            st.rerun()
        
        with col2:
            with st.container():
                st.markdown("#### Fundamental Data")
                st.caption("Financials and valuation")
                if st.session_state.fundamental_data:
                    st.success("✓ Data loaded")
                else:
                    st.info("Pending")
                
                if st.button("Get Fundamental Data", use_container_width=True, type="secondary"):
                    with st.spinner("Collecting..."):
                        collector = YFinanceCollector()
                        st.session_state.fundamental_data = collector.get_fundamental_data(symbol)
                        st.rerun()
        
        with col3:
            with st.container():
                st.markdown("#### Social Sentiment")
                st.caption("Reddit analysis")
                reddit_configured = os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET")
                
                if st.session_state.sentiment_data:
                    st.success("✓ Data loaded")
                elif not reddit_configured:
                    st.warning("API not configured")
                else:
                    st.info("Pending")
                
                if st.button("Get Sentiment Data", use_container_width=True, type="secondary", disabled=not reddit_configured):
                    if reddit_configured:
                        with st.spinner("Analyzing..."):
                            collector = RedditSentimentCollector(
                                client_id=os.environ.get("REDDIT_CLIENT_ID", ""),
                                client_secret=os.environ.get("REDDIT_CLIENT_SECRET", ""),
                                user_agent="TradingAgents/1.0"
                            )
                            st.session_state.sentiment_data = collector.analyze_subreddit_sentiment(symbol)
                            st.rerun()
    
    if st.session_state.technical_data or st.session_state.fundamental_data or st.session_state.sentiment_data:
        st.divider()
        
        with st.container():
            st.markdown("### 📋 Collected Data Reports")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.technical_data:
                    with st.expander("📊 View Technical Report", expanded=False):
                        technical_report = format_technical_report(st.session_state.technical_data)
                        st.text(technical_report)
            
            with col2:
                if st.session_state.fundamental_data:
                    with st.expander("📈 View Fundamental Report", expanded=False):
                        fundamental_report = format_fundamental_report(st.session_state.fundamental_data)
                        st.text(fundamental_report)
            
            with col3:
                if st.session_state.sentiment_data:
                    with st.expander("💬 View Sentiment Report", expanded=False):
                        sentiment_report = format_sentiment_report(st.session_state.sentiment_data)
                        st.text(sentiment_report)
    
    st.divider()
    
    with st.container():
        st.markdown("### 🚀 Step 3: Run Complete Analysis")
        st.caption("All 5 firms will analyze the event with the collected data")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Run Analysis with All 5 Firms", type="primary", use_container_width=True):
                if not event_description:
                    st.error("⚠️ Please enter the event description")
                elif not (st.session_state.technical_data or st.session_state.fundamental_data or st.session_state.sentiment_data):
                    st.error("⚠️ Collect at least one type of data before continuing")
                else:
                    technical_report = format_technical_report(st.session_state.technical_data) if st.session_state.technical_data else "Not available"
                    fundamental_report = format_fundamental_report(st.session_state.fundamental_data) if st.session_state.fundamental_data else "Not available"
                    sentiment_report = format_sentiment_report(st.session_state.sentiment_data) if st.session_state.sentiment_data else "Not available"
                    
                    firms = st.session_state.orchestrator.get_all_firms()
                    
                    st.session_state.predictions = {}
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, (firm_name, firm) in enumerate(firms.items()):
                        status_text.text(f"🔄 Running analysis with {firm_name}...")
                        
                        prompt = create_trading_prompt(
                            event_description=event_description,
                            technical_report=technical_report,
                            fundamental_report=fundamental_report,
                            sentiment_report=sentiment_report,
                            firm_name=firm_name
                        )
                        
                        try:
                            prediction = firm.generate_prediction(prompt)
                            
                            if 'error' not in prediction:
                                prediction['firm_name'] = firm_name
                                prediction['event_description'] = event_description
                                prediction['prediction_date'] = datetime.now().strftime('%Y-%m-%d')
                                
                                try:
                                    prediction_data = {
                                        'firm_name': firm_name,
                                        'event_description': event_description,
                                        'prediction_date': prediction.get('fecha_prediccion', datetime.now().strftime('%Y-%m-%d')),
                                        'probability': float(prediction.get('probabilidad_final_prediccion', 0.5)),
                                        'postura_riesgo': prediction.get('postura_riesgo', 'NEUTRAL'),
                                        'analisis_sintesis': prediction.get('analisis_sintesis', ''),
                                        'debate_bullish_bearish': prediction.get('debate_bullish_bearish', ''),
                                        'ajuste_riesgo_justificacion': prediction.get('ajuste_riesgo_justificacion', ''),
                                        'tokens_used': prediction.get('tokens_used', 0),
                                        'estimated_cost': prediction.get('estimated_cost', 0.0)
                                    }
                                    
                                    st.session_state.db.save_prediction(prediction_data)
                                    st.session_state.predictions[firm_name] = prediction
                                except Exception as db_error:
                                    st.warning(f"Error saving prediction from {firm_name}: {db_error}")
                                    st.session_state.predictions[firm_name] = prediction
                            else:
                                st.session_state.predictions[firm_name] = prediction
                        
                        except Exception as e:
                            st.session_state.predictions[firm_name] = {
                                'error': str(e),
                                'firm_name': firm_name
                            }
                        
                        progress_bar.progress((i + 1) / len(firms))
                    
                    status_text.empty()
                    progress_bar.empty()
                    st.success("✅ Analysis completed! Review the results in the following tabs")
                    st.balloons()

with tab4:
    st.header("🔍 Transparency Panel - Reasoning from Each AI")
    
    if not st.session_state.predictions:
        st.info("First run the analysis in the 'New Prediction' tab to see each firm's reasoning.")
    else:
        for firm_name, prediction in st.session_state.predictions.items():
            with st.expander(f"🏢 {firm_name}", expanded=False):
                if 'error' in prediction:
                    st.error(f"Error: {prediction['error']}")
                    if 'note' in prediction:
                        st.warning(prediction['note'])
                else:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Final Probability", f"{prediction.get('probabilidad_final_prediccion', 0):.2%}")
                    with col2:
                        st.metric("Risk Posture", prediction.get('postura_riesgo', 'N/A'))
                    with col3:
                        st.metric("Confidence Level", f"{prediction.get('nivel_confianza', 0)}/100")
                    
                    st.markdown("---")
                    
                    st.markdown("### 📊 STAGE I: Analytical Synthesis")
                    st.info(prediction.get('analisis_sintesis', 'Not available'))
                    
                    st.markdown("### 💭 STAGE II: Bullish vs Bearish Debate")
                    st.warning(prediction.get('debate_bullish_bearish', 'Not available'))
                    
                    st.markdown("### ⚖️ STAGE III: Risk Adjustment and Final Decision")
                    st.success(prediction.get('ajuste_riesgo_justificacion', 'Not available'))
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tokens Used", f"{prediction.get('tokens_used', 0):,}")
                    with col2:
                        st.metric("Estimated Cost", f"${prediction.get('estimated_cost', 0):.4f}")

with tab5:
    st.header("📊 Comparative Firm Dashboard")
    
    if st.session_state.predictions:
        st.subheader("🎯 Current Predictions")
        
        predictions_df = []
        for firm_name, pred in st.session_state.predictions.items():
            if 'error' not in pred:
                predictions_df.append({
                    'Firm': firm_name,
                    'Probability': pred.get('probabilidad_final_prediccion', 0),
                    'Posture': pred.get('postura_riesgo', 'N/A'),
                    'Confidence': pred.get('nivel_confianza', 0),
                    'Direction': pred.get('direccion_preliminar', 'N/A'),
                    'Tokens': pred.get('tokens_used', 0),
                    'Cost': pred.get('estimated_cost', 0)
                })
        
        if predictions_df:
            df = pd.DataFrame(predictions_df)
            
            fig = px.bar(
                df,
                x='Firm',
                y='Probability',
                color='Posture',
                title='Prediction Probabilities by Firm',
                labels={'Probability': 'Probability (0-1)'},
                color_discrete_map={
                    'AGRESIVA': '#ff4b4b',
                    'NEUTRAL': '#ffa500',
                    'CONSERVADORA': '#4b7bff'
                }
            )
            fig.update_layout(yaxis_range=[0, 1])
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig2 = px.pie(
                    df,
                    values='Confidence',
                    names='Firm',
                    title='Confidence Level Distribution'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                fig3 = px.bar(
                    df,
                    x='Firm',
                    y='Cost',
                    title='Estimated Cost per Firm (USD)',
                    labels={'Cost': 'Cost (USD)'}
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🏆 Historical Firm Performance")
    
    performances = st.session_state.db.get_all_firm_performances()
    
    if performances:
        perf_df = pd.DataFrame(performances)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Predictions", sum(p['total_predictions'] for p in performances))
        with col2:
            total_correct = sum(p['correct_predictions'] for p in performances)
            total_preds = sum(p['total_predictions'] for p in performances)
            overall_accuracy = (total_correct / total_preds * 100) if total_preds > 0 else 0
            st.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
        with col3:
            total_profit = sum(p['total_profit'] for p in performances)
            st.metric("Total Simulated Profit", f"${total_profit:,.2f}")
        
        st.dataframe(perf_df, use_container_width=True)
        
        if perf_df['total_predictions'].sum() > 0:
            fig4 = px.bar(
                perf_df,
                x='firm_name',
                y='accuracy',
                title='Historical Accuracy by Firm (%)',
                labels={'firm_name': 'Firm', 'accuracy': 'Accuracy (%)'}
            )
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No historical data yet. Predictions will be saved automatically.")

with tab6:
    st.header("🤖 Recommendations & Prediction Consensus")
    
    if not st.session_state.predictions:
        st.info("First run the analysis to get recommendations.")
    else:
        st.subheader("🎯 Firm Recommendation Based on Historical Data")
        
        recommendation = st.session_state.recommender.get_best_firm_recommendation()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Recommended Firm", recommendation['recommended_firm'])
        with col2:
            st.metric("Confidence", recommendation['confidence'])
        with col3:
            if 'accuracy' in recommendation:
                st.metric("Historical Accuracy", f"{recommendation['accuracy']:.1f}%")
        
        st.info(f"**Reason:** {recommendation['reason']}")
        
        if recommendation.get('alternatives'):
            st.markdown(f"**Alternatives:** {', '.join(recommendation['alternatives'])}")
        
        st.markdown("---")
        
        st.subheader("🤝 Weighted Consensus Prediction")
        
        consensus = st.session_state.recommender.calculate_consensus_prediction(st.session_state.predictions)
        
        if consensus['participating_firms']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Consensus Probability", f"{consensus['consensus_probability']:.2%}")
                st.metric("Agreement Level", f"{consensus['confidence']:.1f}%")
            
            with col2:
                st.markdown("**Participating Firms:**")
                for firm in consensus['participating_firms']:
                    weight = consensus['weights'].get(firm, 0)
                    prob = consensus['individual_probabilities'].get(firm, 0)
                    st.write(f"- {firm}: {prob:.2%} (weight: {weight:.2%})")
            
            st.markdown("---")
            
            st.markdown("**Interpretation:**")
            if consensus['confidence'] > 70:
                st.success("✅ High level of agreement among firms. Reliable consensus prediction.")
            elif consensus['confidence'] > 40:
                st.warning("⚠️ Moderate level of agreement. Some divergence among firms.")
            else:
                st.error("❌ Low level of agreement. Firms have very different opinions.")
            
            st.markdown("---")
            
            st.subheader("📊 Consensus Visualization")
            
            if consensus['individual_probabilities']:
                firms = list(consensus['individual_probabilities'].keys())
                probs = [consensus['individual_probabilities'][f] for f in firms]
                weights = [consensus['weights'][f] * 100 for f in firms]
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=firms,
                    y=probs,
                    name='Individual Probability',
                    marker_color='lightblue'
                ))
                
                fig.add_trace(go.Scatter(
                    x=firms,
                    y=[consensus['consensus_probability']] * len(firms),
                    name='Weighted Consensus',
                    mode='lines+markers',
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    title='Individual Probabilities vs. Consensus',
                    yaxis_title='Probability',
                    yaxis_range=[0, 1],
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid predictions to calculate consensus.")
        
        st.markdown("---")
        
        st.subheader("📈 Reasoning Pattern Analysis")
        
        pattern_analysis = st.session_state.recommender.analyze_reasoning_patterns()
        
        if pattern_analysis['total_analyzed'] > 0:
            st.write(f"**Total Analyzed:** {pattern_analysis['total_analyzed']} resolved predictions")
            
            if pattern_analysis['patterns']:
                patterns_df = pd.DataFrame(pattern_analysis['patterns'])
                
                fig = px.bar(
                    patterns_df,
                    x='pattern_value',
                    y='accuracy',
                    color='total_profit',
                    title='Accuracy by Risk Posture',
                    labels={
                        'pattern_value': 'Risk Posture',
                        'accuracy': 'Accuracy (%)',
                        'total_profit': 'Total Profit'
                    },
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(patterns_df[['pattern_value', 'occurrences', 'accuracy', 'total_profit', 'avg_profit']], 
                            use_container_width=True)
            else:
                st.info("No patterns detected yet.")
        else:
            st.info("No resolved predictions to analyze patterns.")
        
        st.markdown("---")
        
        st.subheader("🏆 Detailed Attribution Report")
        
        attribution = st.session_state.recommender.get_firm_attribution_report()
        
        if attribution:
            attr_df = pd.DataFrame(attribution)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                wins = len(attr_df[attr_df['correct'] == True])
                st.metric("Wins", wins)
            with col2:
                losses = len(attr_df[attr_df['correct'] == False])
                st.metric("Losses", losses)
            with col3:
                total_profit = attr_df['profit_loss'].sum()
                st.metric("Total P/L", f"${total_profit:,.2f}")
            with col4:
                best_firm = attr_df.groupby('firm_name')['profit_loss'].sum().idxmax()
                st.metric("Best Firm", best_firm)
            
            st.markdown("**Detail by Firm:**")
            
            firm_summary = attr_df.groupby('firm_name').agg({
                'correct': lambda x: (x == True).sum(),
                'prediction_id': 'count',
                'profit_loss': 'sum'
            }).reset_index()
            
            firm_summary.columns = ['Firm', 'Wins', 'Total', 'Profit']
            firm_summary['Accuracy (%)'] = (firm_summary['Wins'] / firm_summary['Total'] * 100).round(1)
            
            st.dataframe(firm_summary, use_container_width=True)
            
            with st.expander("View all attributions", expanded=False):
                display_attr = attr_df[['firm_name', 'event_description', 'predicted_probability', 
                                        'actual_result', 'correct', 'profit_loss', 'impact']]
                display_attr.columns = ['Firm', 'Event', 'Predicted Prob.', 'Result', 
                                       'Correct', 'P/L', 'Impact']
                st.dataframe(display_attr, use_container_width=True, height=400)
        else:
            st.info("No attribution data available. Record results to view this report.")

with tab7:
    st.header("📤 Submit Prediction to Opinion.trade")
    
    if not st.session_state.predictions:
        st.info("First run the analysis in the 'New Prediction' tab to submit predictions.")
    else:
        valid_predictions = {k: v for k, v in st.session_state.predictions.items() if 'error' not in v}
        
        if valid_predictions:
            st.subheader("📊 Select Which Prediction to Submit")
            
            selected_firm = st.selectbox(
                "Firm",
                options=list(valid_predictions.keys()),
                help="Select the firm whose prediction you want to submit to Opinion.trade",
                key="submit_firm_selector"
            )
            
            if selected_firm:
                prediction = valid_predictions[selected_firm]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Probability", f"{prediction.get('probabilidad_final_prediccion', 0):.2%}")
                with col2:
                    st.metric("Risk Posture", prediction.get('postura_riesgo', 'N/A'))
                with col3:
                    perf = st.session_state.db.get_firm_performance(selected_firm)
                    if perf and perf['total_predictions'] > 0:
                        st.metric("Historical Accuracy", f"{perf['accuracy']:.1f}%")
                    else:
                        st.metric("Historical Accuracy", "No history")
                
                st.markdown("---")
                
                with st.expander("📝 View complete reasoning", expanded=False):
                    st.markdown("**Analytical Synthesis:**")
                    st.info(prediction.get('analisis_sintesis', 'Not available'))
                    st.markdown("**Debate Conclusion:**")
                    st.warning(prediction.get('debate_bullish_bearish', 'Not available')[:300] + "...")
                
                st.markdown("---")
                st.subheader("🎯 Submission Configuration")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    event_id = st.text_input(
                        "Event ID on Opinion.trade",
                        placeholder="event_123abc",
                        help="Enter the event ID on Opinion.trade"
                    )
                
                with col2:
                    bet_amount = st.number_input(
                        "Bet Amount (USD)",
                        min_value=1.0,
                        max_value=1000.0,
                        value=10.0,
                        step=1.0,
                        help="Amount to bet on this prediction"
                    )
                
                st.markdown("---")
                
                if st.button("🚀 Submit Prediction to Opinion.trade", type="primary", use_container_width=True):
                    if not event_id:
                        st.error("Please enter the event ID")
                    else:
                        with st.spinner("Submitting prediction to Opinion.trade..."):
                            api = OpinionTradeAPI()
                            
                            submission_data = {
                                'event_id': event_id,
                                'probability': prediction.get('probabilidad_final_prediccion', 0.5),
                                'amount': bet_amount,
                                'firm_name': selected_firm,
                                'reasoning': prediction.get('analisis_sintesis', ''),
                                'risk_posture': prediction.get('postura_riesgo', 'NEUTRAL')
                            }
                            
                            result = api.submit_prediction(submission_data)
                            
                            if result.get('success'):
                                st.success(f"✅ Prediction submitted successfully!")
                                st.info(f"**Prediction ID:** {result.get('prediction_id', 'N/A')}")
                                st.balloons()
                                
                                st.markdown("---")
                                st.info("""
                                **Next steps:**
                                1. Note the prediction ID shown above
                                2. Once the event resolves, go to the "Record Results" tab
                                3. Enter the actual result (TRUE/FALSE) to update the firm's metrics
                                """)
                            else:
                                st.error(f"❌ Error submitting prediction: {result.get('message', 'Unknown error')}")
                                st.warning(f"Details: {result.get('error', '')}")
                
                st.markdown("---")
                
                with st.expander("💾 Download JSON (optional)", expanded=False):
                    export_data = {
                        "firma_generadora": selected_firm,
                        "fecha_prediccion": prediction.get('fecha_prediccion', datetime.now().strftime('%Y-%m-%d')),
                        "evento_opinion_trade": prediction.get('evento_opinion_trade', ''),
                        "probabilidad_final_prediccion": prediction.get('probabilidad_final_prediccion', 0.5),
                        "postura_riesgo": prediction.get('postura_riesgo', 'NEUTRAL'),
                        "nivel_confianza": prediction.get('nivel_confianza', 50),
                        "analisis_sintesis": prediction.get('analisis_sintesis', ''),
                        "debate_bullish_bearish": prediction.get('debate_bullish_bearish', ''),
                        "ajuste_riesgo_justificacion": prediction.get('ajuste_riesgo_justificacion', '')
                    }
                    
                    st.json(export_data)
                    
                    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_str,
                        file_name=f"prediction_{selected_firm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.warning("No valid predictions to submit. All firms reported errors.")

with tab8:
    st.header("📝 Record Prediction Results")
    
    st.markdown("""
    Use this interface to record the actual results of submitted predictions.
    This updates the performance metrics of each firm.
    """)
    
    st.markdown("---")
    
    recent_predictions = st.session_state.db.get_recent_predictions(limit=50)
    
    unresolved_predictions = [p for p in recent_predictions if p['actual_result'] is None]
    
    if not unresolved_predictions:
        st.info("✅ No pending predictions to resolve. All recent predictions already have recorded results.")
    else:
        st.subheader(f"📋 Pending Predictions ({len(unresolved_predictions)})")
        
        for pred in unresolved_predictions:
            with st.expander(f"🏢 {pred['firm_name']} - {pred['event_description'][:60]}...", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Predicted Probability", f"{pred['probability']:.2%}")
                with col2:
                    st.metric("Date", pred['prediction_date'])
                with col3:
                    st.metric("ID", f"#{pred['id']}")
                
                st.markdown("**Event:**")
                st.write(pred['event_description'])
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                profit_loss = 0.0
                
                with col1:
                    actual_result = st.radio(
                        "What was the actual result?",
                        options=[None, 1, 0],
                        format_func=lambda x: "Select..." if x is None else "TRUE (Event occurred)" if x == 1 else "FALSE (Event did not occur)",
                        key=f"result_{pred['id']}"
                    )
                
                with col2:
                    if actual_result is not None:
                        profit_loss = st.number_input(
                            "Profit/Loss (USD)",
                            value=0.0,
                            step=0.01,
                            key=f"pl_{pred['id']}",
                            help="Enter profit (positive) or loss (negative) in USD"
                        )
                
                with col3:
                    if actual_result is not None:
                        if st.button("💾 Save Result", key=f"save_{pred['id']}", type="primary"):
                            st.session_state.db.update_prediction_result(
                                pred['id'],
                                actual_result,
                                profit_loss
                            )
                            st.success("✅ Result saved successfully!")
                            st.rerun()
    
    st.markdown("---")
    st.subheader("📊 Complete Prediction History")
    
    all_predictions = st.session_state.db.get_recent_predictions(limit=100)
    
    if all_predictions:
        df = pd.DataFrame(all_predictions)
        
        df['resultado'] = df['actual_result'].apply(
            lambda x: 'Pending' if x is None else ('TRUE' if x == 1 else 'FALSE')
        )
        
        df['correcto'] = df.apply(
            lambda row: 'N/A' if row['actual_result'] is None else 
            ('✅' if (row['probability'] >= 0.5 and row['actual_result'] == 1) or 
                    (row['probability'] < 0.5 and row['actual_result'] == 0) else '❌'),
            axis=1
        )
        
        display_df = df[['id', 'firm_name', 'event_description', 'probability', 
                         'prediction_date', 'resultado', 'profit_loss', 'correcto']]
        
        display_df.columns = ['ID', 'Firm', 'Event', 'Probability', 'Date', 
                              'Actual Result', 'P/L (USD)', 'Correct']
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        col1, col2, col3 = st.columns(3)
        
        resolved = df[df['actual_result'].notna()]
        if len(resolved) > 0:
            with col1:
                st.metric("Resolved Predictions", len(resolved))
            with col2:
                total_pl = resolved['profit_loss'].sum()
                st.metric("Total P/L", f"${total_pl:,.2f}")
            with col3:
                accuracy = (resolved['correcto'] == '✅').sum() / len(resolved) * 100
                st.metric("Overall Accuracy", f"{accuracy:.1f}%")
    else:
        st.info("No predictions recorded yet.")

st.sidebar.title("⚙️ Configuration")

with st.sidebar.expander("🔑 Configured API Keys"):
    st.write("✅ Alpha Vantage:", "Configured" if os.environ.get("ALPHA_VANTAGE_API_KEY") else "❌ Not configured")
    st.write("✅ OpenAI (AI Int.):", "Configured" if os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") else "❌ Not configured")
    st.write("✅ Gemini (AI Int.):", "Configured" if os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY") else "❌ Not configured")
    st.write("✅ Qwen:", "Configured" if os.environ.get("QWEN_API_KEY") else "⚠️ Optional")
    st.write("✅ Deepseek:", "Configured" if os.environ.get("DEEPSEEK_API_KEY") else "⚠️ Optional")
    st.write("✅ Grok (xAI):", "Configured" if os.environ.get("XAI_API_KEY") else "⚠️ Optional")
    st.write("✅ Reddit:", "Configured" if (os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET")) else "⚠️ Optional")
    st.write("✅ Opinion.trade:", "Configured" if os.environ.get("OPINION_TRADE_API_KEY") else "⚠️ Pending")

st.sidebar.markdown("---")
st.sidebar.info("""
**TradingAgents Framework v1.0**

Autonomous market prediction system with 5 competing LLM firms.

Each firm simulates 7 internal roles to generate optimized predictions.
""")
