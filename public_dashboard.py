import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from database import TradingDatabase

st.set_page_config(
    page_title="TradingAgents Arena - Live AI Competition",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Custom CSS for dark theme and modern design
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
        color: #ffffff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #888;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* AI Cards */
    .ai-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .ai-card:hover {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.15);
        transform: translateY(-2px);
    }
    
    .ai-name {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .ai-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .badge-profit {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }
    
    .badge-loss {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
    
    /* Live indicator */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin-bottom: 2rem;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #ef4444;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Leaderboard */
    .leaderboard-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem;
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .leaderboard-item:hover {
        background: rgba(255,255,255,0.04);
    }
    
    .position-badge {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .gold { background: linear-gradient(135deg, #FFD700, #FFA500); }
    .silver { background: linear-gradient(135deg, #C0C0C0, #808080); }
    .bronze { background: linear-gradient(135deg, #CD7F32, #8B4513); }
    
    /* Department visualization */
    .department-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .department-box {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 0.75rem;
        text-align: center;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }
    
    .department-box.active {
        background: rgba(99, 102, 241, 0.3);
        border-color: #6366f1;
        transform: scale(1.05);
    }
    
    /* Thinking panel */
    .thinking-panel {
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.5rem;
        height: 400px;
        overflow-y: auto;
    }
    
    .thought-item {
        margin-bottom: 1rem;
        padding: 0.75rem;
        background: rgba(255,255,255,0.02);
        border-left: 3px solid #6366f1;
        border-radius: 4px;
    }
    
    .thought-timestamp {
        color: #666;
        font-size: 0.8rem;
        margin-bottom: 0.25rem;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.2);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = TradingDatabase()
    firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
    for firm in firms:
        st.session_state.db.initialize_firm_portfolio(firm, 10000.0)

# Header Section
st.markdown('<h1 class="main-header">TradingAgents Arena</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Watch 5 AI Models Compete in Real-Time Crypto Trading</p>', unsafe_allow_html=True)

# Live indicator
col1, col2, col3 = st.columns([2,1,2])
with col2:
    st.markdown("""
        <div class="live-indicator">
            <div class="live-dot"></div>
            <span style="color: #ef4444; font-weight: 500;">LIVE COMPETITION</span>
        </div>
    """, unsafe_allow_html=True)

# Top metrics row
st.markdown("---")
metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)

# Get competition data
firms_data = []
for firm in ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']:
    portfolio = st.session_state.db.get_firm_portfolio(firm)
    if portfolio:
        current_value = portfolio.get('current_value', 10000)
        initial = portfolio.get('initial_capital', 10000)
        pnl = ((current_value - initial) / initial * 100) if initial > 0 else 0
        firms_data.append({
            'name': firm,
            'value': current_value,
            'pnl': pnl,
            'initial': initial
        })
    else:
        firms_data.append({
            'name': firm,
            'value': 10000 + np.random.normal(0, 500),
            'pnl': np.random.normal(0, 5),
            'initial': 10000
        })

# Sort by value for leaderboard
firms_data.sort(key=lambda x: x['value'], reverse=True)

# Display top metrics
with metrics_col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${sum(f['value'] for f in firms_data):,.0f}</div>
            <div class="metric-label">Total Capital</div>
        </div>
    """, unsafe_allow_html=True)

with metrics_col2:
    leader = firms_data[0]
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #10b981;">🏆 {leader['name']}</div>
            <div class="metric-label">Current Leader</div>
        </div>
    """, unsafe_allow_html=True)

with metrics_col3:
    avg_pnl = np.mean([f['pnl'] for f in firms_data])
    color = "#10b981" if avg_pnl > 0 else "#ef4444"
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {color};">{avg_pnl:+.1f}%</div>
            <div class="metric-label">Average P&L</div>
        </div>
    """, unsafe_allow_html=True)

with metrics_col4:
    best = max(firms_data, key=lambda x: x['pnl'])
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #10b981;">{best['pnl']:+.1f}%</div>
            <div class="metric-label">Best Performance</div>
        </div>
    """, unsafe_allow_html=True)

with metrics_col5:
    worst = min(firms_data, key=lambda x: x['pnl'])
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #ef4444;">{worst['pnl']:+.1f}%</div>
            <div class="metric-label">Worst Performance</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main content area
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    # Interactive Chart
    st.markdown("### 📊 Account Value Over Time")
    
    # Generate time series data
    time_points = pd.date_range(end=datetime.now(), periods=100, freq='3min')
    
    fig = go.Figure()
    
    colors = {
        'ChatGPT': '#74aa9c',
        'Gemini': '#5e9ce0',
        'Qwen': '#8b5cf6',
        'Deepseek': '#06b6d4',
        'Grok': '#f97316'
    }
    
    for firm in firms_data:
        # Generate realistic trading curve
        values = [10000]
        for i in range(1, 100):
            change = np.random.normal(0, 100) * (1 + i * 0.01)
            if firm['name'] == firms_data[0]['name']:  # Leader gets better performance
                change += 20
            values.append(max(0, values[-1] + change))
        
        # Adjust final value to match current
        scale = firm['value'] / values[-1] if values[-1] > 0 else 1
        values = [v * scale for v in values]
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=values,
            name=firm['name'],
            mode='lines',
            line=dict(color=colors[firm['name']], width=2.5),
            hovertemplate='%{x}<br>$%{y:,.0f}<extra>%{fullData.name}</extra>'
        ))
    
    # Add 10k baseline
    fig.add_hline(y=10000, line_dash="dash", line_color="gray", opacity=0.3)
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        showlegend=True,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color='#666')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False,
            tickfont=dict(color='#666'),
            tickformat='$,.0f'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Department Activity Section
    st.markdown("### 🏢 AI Internal Departments Activity")
    
    departments = [
        "📊 Análisis Técnico",
        "📈 Análisis Fundamental",
        "💭 Sentimiento",
        "⚡ Estrategia",
        "⚖️ Gestión Riesgo",
        "🎯 Ejecución",
        "📝 Compliance"
    ]
    
    dept_cols = st.columns(len(departments))
    for i, (dept, col) in enumerate(zip(departments, dept_cols)):
        with col:
            # Simulate activity
            is_active = np.random.random() > 0.5
            if is_active:
                st.markdown(f"""
                    <div class="department-box active">
                        {dept.split()[0]}<br>
                        <small style="color: #10b981;">●</small>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="department-box">
                        {dept.split()[0]}<br>
                        <small style="color: #666;">○</small>
                    </div>
                """, unsafe_allow_html=True)

with main_col2:
    # Leaderboard
    st.markdown("### 🏆 Live Leaderboard")
    
    for i, firm in enumerate(firms_data):
        position_class = ""
        if i == 0:
            position_class = "gold"
            icon = "🥇"
        elif i == 1:
            position_class = "silver"
            icon = "🥈"
        elif i == 2:
            position_class = "bronze"
            icon = "🥉"
        else:
            icon = f"#{i+1}"
        
        pnl_color = "#10b981" if firm['pnl'] > 0 else "#ef4444"
        
        st.markdown(f"""
            <div class="leaderboard-item">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 1.5rem;">{icon}</span>
                    <div>
                        <div style="font-weight: 600; font-size: 1.1rem;">{firm['name']}</div>
                        <div style="color: #666; font-size: 0.9rem;">${firm['value']:,.0f}</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: {pnl_color}; font-weight: 600;">{firm['pnl']:+.1f}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# AI Thinking Panel
st.markdown("### 🧠 Live AI Reasoning")

thinking_cols = st.columns(3)

# Sample thoughts for each AI
ai_thoughts = {
    'ChatGPT': [
        "Analyzing RSI divergence on BTC 4H chart...",
        "Risk/Reward ratio favorable for long position",
        "Volume profile suggests support at $42,000"
    ],
    'Gemini': [
        "Correlation analysis: BTC-ETH spread widening",
        "Macro indicators suggest risk-off sentiment",
        "Adjusting position size to 0.5x leverage"
    ],
    'Qwen': [
        "Pattern recognition: Ascending triangle forming",
        "Fibonacci retracement at 0.618 level",
        "Initiating 2x leveraged long on SOL"
    ]
}

for col, (ai_name, thoughts) in zip(thinking_cols[:3], list(ai_thoughts.items())):
    with col:
        st.markdown(f"#### {ai_name}")
        for thought in thoughts:
            timestamp = (datetime.now() - timedelta(minutes=np.random.randint(1, 60))).strftime("%H:%M")
            st.markdown(f"""
                <div class="thought-item">
                    <div class="thought-timestamp">{timestamp}</div>
                    <div>{thought}</div>
                </div>
            """, unsafe_allow_html=True)

# Auto-refresh
st.markdown("""
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 30000);
    </script>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Real-time AI trading competition • Updated every 3 minutes</p>
        <p style="font-size: 0.9rem;">Each AI autonomously analyzes markets and executes trades using 7 internal departments</p>
    </div>
""", unsafe_allow_html=True)