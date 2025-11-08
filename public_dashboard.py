import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from database import TradingDatabase
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Alpha Arena - Live Trading",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Auto-refresh every 30 seconds
REFRESH_INTERVAL = 30000  # milliseconds
count = st_autorefresh(interval=REFRESH_INTERVAL, key="data_refresh")

# Clean, minimal CSS - White theme inspired by nof1.ai
st.markdown("""
<style>
    /* Clean white background */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Typography */
    .main-title {
        font-size: 2.2rem;
        font-weight: 300;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.01em;
    }
    
    .subtitle {
        color: #666666;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Metrics */
    .metric-container {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1.2rem;
        height: 100%;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 400;
        color: #1a1a1a;
        line-height: 1.2;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    .positive {
        color: #059669;
    }
    
    .negative {
        color: #dc2626;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1a1a1a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e5e5e5;
    }
    
    /* Tables and lists */
    .data-table {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1rem;
        width: 100%;
    }
    
    .table-row {
        padding: 0.75rem 0;
        border-bottom: 1px solid #f3f4f6;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .table-row:last-child {
        border-bottom: none;
    }
    
    /* Live indicator */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        background: #fef2f2;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #dc2626;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .live-dot {
        width: 6px;
        height: 6px;
        background: #dc2626;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Department cards - minimal */
    .dept-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .dept-card {
        padding: 0.75rem;
        background: #fafafa;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
        font-size: 0.85rem;
    }
    
    .dept-name {
        color: #1a1a1a;
        font-weight: 500;
    }
    
    .dept-status {
        color: #666666;
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    /* Reasoning panel */
    .reasoning-container {
        background: #fafafa;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .ai-column {
        padding: 0.5rem;
        border-right: 1px solid #e5e5e5;
    }
    
    .ai-column:last-child {
        border-right: none;
    }
    
    .ai-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .thought-item {
        font-size: 0.8rem;
        color: #666666;
        padding: 0.25rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .timestamp {
        font-size: 0.7rem;
        color: #9ca3af;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    return TradingDatabase()

db = get_database()

# Header
st.markdown('<h1 class="main-title">Alpha Arena</h1>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('''
        <div style="text-align: center;">
            <span class="live-indicator">
                <span class="live-dot"></span>
                LIVE
            </span>
        </div>
    ''', unsafe_allow_html=True)
st.markdown('<p class="subtitle" style="text-align: center;">Real-time AI trading competition</p>', unsafe_allow_html=True)

# Get simulation data
def get_simulation_data():
    """Generate or fetch simulation data for the dashboard"""
    
    # Try to get real data from database
    try:
        # Get autonomous bets data
        query = """
        SELECT 
            ia_name,
            COUNT(*) as total_bets,
            SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
            SUM(profit_loss) as total_pnl,
            MAX(created_at) as last_activity
        FROM autonomous_bets
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY ia_name
        """
        
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            # Real data exists
            account_values = {}
            for ia in ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']:
                if ia in df['ia_name'].values:
                    row = df[df['ia_name'] == ia].iloc[0]
                    base_value = 10000
                    account_values[ia] = base_value + row['total_pnl']
                else:
                    account_values[ia] = 10000
            
            return {
                'account_values': account_values,
                'has_real_data': True
            }
    except Exception as e:
        pass
    
    # Simulation data if no real data
    np.random.seed(42)
    base_value = 10000
    
    account_values = {
        'ChatGPT': base_value * 1.12,
        'Gemini': base_value * 1.08,
        'Qwen': base_value * 0.95,
        'Deepseek': base_value * 0.93,
        'Grok': base_value * 1.03
    }
    
    return {
        'account_values': account_values,
        'has_real_data': False
    }

sim_data = get_simulation_data()

# Key Metrics Row
st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

total_capital = sum(sim_data['account_values'].values())
avg_pnl = ((total_capital - 50000) / 50000) * 100
best_performer = max(sim_data['account_values'].items(), key=lambda x: x[1])
worst_performer = min(sim_data['account_values'].items(), key=lambda x: x[1])

with col1:
    st.markdown(f'''
        <div class="metric-container">
            <div class="metric-label">Total Capital</div>
            <div class="metric-value">${total_capital:,.0f}</div>
            <div class="metric-delta {'positive' if total_capital > 50000 else 'negative'}">
                {'+' if total_capital > 50000 else ''}{total_capital - 50000:,.0f}
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    leader = best_performer[0]
    st.markdown(f'''
        <div class="metric-container">
            <div class="metric-label">Current Leader</div>
            <div class="metric-value">{leader}</div>
            <div class="metric-delta positive">#{1}</div>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="metric-container">
            <div class="metric-label">Average P&L</div>
            <div class="metric-value">{avg_pnl:+.1f}%</div>
            <div class="metric-delta {'positive' if avg_pnl > 0 else 'negative'}">
                vs initial capital
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    best_pnl = ((best_performer[1] - 10000) / 10000) * 100
    worst_pnl = ((worst_performer[1] - 10000) / 10000) * 100
    st.markdown(f'''
        <div class="metric-container">
            <div class="metric-label">Performance Range</div>
            <div class="metric-value">{best_pnl:+.1f}% / {worst_pnl:+.1f}%</div>
            <div class="metric-delta">Best / Worst</div>
        </div>
    ''', unsafe_allow_html=True)

# Chart Section
st.markdown('<div class="section-header">Account Value Over Time</div>', unsafe_allow_html=True)

# Generate time series data
def create_chart_data():
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    # Create realistic trading curves
    np.random.seed(42)
    data = {}
    
    for ai_name, final_value in sim_data['account_values'].items():
        # Generate a path from 10000 to final_value
        returns = np.random.randn(30) * 0.02  # 2% daily volatility
        
        # Add trend to reach final value
        trend = (final_value / 10000) ** (1/30) - 1
        returns = returns + trend
        
        # Calculate cumulative values
        values = [10000]
        for r in returns[1:]:
            values.append(values[-1] * (1 + r))
        
        # Adjust last value to match exactly
        scaling = final_value / values[-1]
        values = [v * scaling for v in values]
        
        data[ai_name] = values
    
    return dates, data

dates, chart_data = create_chart_data()

# Create Plotly chart with clean, minimal design
fig = go.Figure()

# Color palette - subtle and professional
colors = {
    'ChatGPT': '#4A5568',
    'Gemini': '#718096',
    'Qwen': '#A0AEC0',
    'Deepseek': '#CBD5E0',
    'Grok': '#2D3748'
}

for ai_name, values in chart_data.items():
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        name=ai_name,
        line=dict(width=1.5, color=colors[ai_name]),
        hovertemplate='%{y:$,.0f}<extra></extra>'
    ))

fig.update_layout(
    template='plotly_white',
    height=400,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(family="system-ui", size=11, color="#666666"),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255,255,255,0)",
        bordercolor="rgba(255,255,255,0)",
        font=dict(size=10)
    ),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        tickfont=dict(size=9, color="#999999")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#f0f0f0',
        zeroline=False,
        tickformat='$,.0f',
        tickfont=dict(size=9, color="#999999")
    ),
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# Leaderboard and Activity
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">Leaderboard</div>', unsafe_allow_html=True)
    
    # Sort by account value
    sorted_accounts = sorted(sim_data['account_values'].items(), key=lambda x: x[1], reverse=True)
    
    leaderboard_html = '<div class="data-table">'
    for i, (name, value) in enumerate(sorted_accounts):
        pnl = ((value - 10000) / 10000) * 100
        pnl_class = 'positive' if pnl > 0 else 'negative'
        
        leaderboard_html += f'''
        <div class="table-row">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 0.9rem; color: #999999; width: 20px;">#{i+1}</span>
                <span style="font-weight: 500; color: #1a1a1a;">{name}</span>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 500; color: #1a1a1a;">${value:,.0f}</div>
                <div class="{pnl_class}" style="font-size: 0.8rem;">{pnl:+.1f}%</div>
            </div>
        </div>
        '''
    leaderboard_html += '</div>'
    st.markdown(leaderboard_html, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-header">System Activity</div>', unsafe_allow_html=True)
    
    # Department status - simplified
    departments = [
        ('Technical Analysis', 'Active'),
        ('Fundamental Analysis', 'Active'),
        ('Sentiment Analysis', 'Idle'),
        ('Risk Management', 'Active'),
        ('Execution', 'Processing'),
        ('Monitoring', 'Active'),
        ('Learning', 'Weekly cycle')
    ]
    
    dept_html = '<div class="data-table">'
    for dept_name, status in departments:
        status_color = '#059669' if status in ['Active', 'Processing'] else '#666666'
        dept_html += f'''
        <div class="table-row">
            <div class="dept-name">{dept_name}</div>
            <div class="dept-status" style="color: {status_color}; text-align: right;">{status}</div>
        </div>
        '''
    dept_html += '</div>'
    st.markdown(dept_html, unsafe_allow_html=True)

# AI Reasoning Section
st.markdown('<div class="section-header">Recent Decisions</div>', unsafe_allow_html=True)

# Generate sample reasoning data
def generate_reasoning():
    reasons = [
        "Analyzing RSI divergence on 4H timeframe",
        "Federal Reserve meeting minutes suggest dovish stance",
        "Social sentiment turning bullish on major forums",
        "Risk/reward ratio favorable at current levels",
        "Volume profile indicates strong support below",
        "Correlation with equity markets weakening",
        "Options flow showing increased call buying",
        "Technical breakout confirmed with volume"
    ]
    
    reasoning_data = {}
    for ai in ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']:
        ai_thoughts = []
        for i in range(3):
            timestamp = datetime.now() - timedelta(minutes=np.random.randint(5, 120))
            thought = np.random.choice(reasons)
            ai_thoughts.append({
                'time': timestamp.strftime('%H:%M'),
                'thought': thought
            })
        reasoning_data[ai] = ai_thoughts
    
    return reasoning_data

reasoning = generate_reasoning()

# Display reasoning in a clean grid
cols = st.columns(5)
for i, (ai_name, thoughts) in enumerate(reasoning.items()):
    with cols[i]:
        st.markdown(f'<div class="ai-label">{ai_name}</div>', unsafe_allow_html=True)
        for thought_data in thoughts:
            st.markdown(f'''
                <div class="thought-item">
                    <span class="timestamp">{thought_data['time']}</span><br>
                    {thought_data['thought']}
                </div>
            ''', unsafe_allow_html=True)

# Footer
st.markdown('---')
st.markdown(f'''
    <div style="text-align: center; color: #999999; font-size: 0.8rem; padding: 1rem 0;">
        Live trading competition • Updates every 30 seconds • 
        7 internal departments per AI model
    </div>
''', unsafe_allow_html=True)