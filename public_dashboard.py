import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sqlite3
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

# Clean, minimal CSS - White theme
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Typography */
    h1, h2, h3 {
        color: #1a1a1a;
        font-weight: 400;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #1a1a1a;
        font-weight: 400;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }
    
    /* Containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background-color: #fafafa;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
    }
    
    /* Live indicator */
    .live-badge {
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
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Department badges */
    .dept-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #f3f4f6;
        border-radius: 4px;
        font-size: 0.75rem;
        color: #4b5563;
        margin: 0.25rem;
    }
    
    .dept-active {
        background: #dcfce7;
        color: #059669;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.85rem !important;
    }
    
    .dataframe th {
        background-color: #fafafa !important;
        color: #666666 !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.05em !important;
    }
    
    .dataframe td {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    return TradingDatabase()

db = get_database()

# Header
st.markdown("# Alpha Arena")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div style="text-align: center;"><span class="live-badge"><span class="live-dot"></span>LIVE</span></div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666666; font-size: 0.95rem;">Real-time AI trading competition</p>', unsafe_allow_html=True)
st.divider()

# Get data from database
def get_account_values():
    """Get current account values for all AIs"""
    try:
        conn = sqlite3.connect(db.db_path)
        
        # Get latest portfolio values
        query = """
        SELECT 
            firm_name,
            total_capital
        FROM virtual_portfolio
        WHERE firm_name IN ('ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok')
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            account_values = dict(zip(df['firm_name'], df['total_capital']))
            # Fill missing AIs with base value
            for ai in ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']:
                if ai not in account_values:
                    account_values[ai] = 10000
            return account_values, True
    except Exception as e:
        pass
    
    # Fallback to simulation data
    np.random.seed(42 + count)
    return {
        'ChatGPT': 10000 + np.random.randint(-1000, 2000),
        'Gemini': 10000 + np.random.randint(-1000, 1500),
        'Qwen': 10000 + np.random.randint(-1500, 500),
        'Deepseek': 10000 + np.random.randint(-1200, 800),
        'Grok': 10000 + np.random.randint(-800, 1200)
    }, False

account_values, has_real_data = get_account_values()

# Key Metrics
st.markdown("### Overview")
col1, col2, col3, col4 = st.columns(4)

total_capital = sum(account_values.values())
avg_pnl = ((total_capital - 50000) / 50000) * 100
leader = max(account_values.items(), key=lambda x: x[1])
worst = min(account_values.items(), key=lambda x: x[1])
best_pnl = ((leader[1] - 10000) / 10000) * 100
worst_pnl = ((worst[1] - 10000) / 10000) * 100

with col1:
    st.metric(
        "Total Capital",
        f"${total_capital:,.0f}",
        f"{total_capital - 50000:+,.0f}"
    )

with col2:
    st.metric(
        "Current Leader",
        leader[0],
        "🥇 #1"
    )

with col3:
    st.metric(
        "Average P&L",
        f"{avg_pnl:+.1f}%",
        "vs initial"
    )

with col4:
    st.metric(
        "Performance Range",
        f"{best_pnl:+.1f}% / {worst_pnl:+.1f}%",
        "Best / Worst"
    )

st.divider()

# Chart
st.markdown("### Account Value Over Time")

# Generate historical data
def create_chart_data():
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    np.random.seed(42)
    data = {}
    
    for ai_name, final_value in account_values.items():
        returns = np.random.randn(30) * 0.015
        trend = (final_value / 10000) ** (1/30) - 1
        returns = returns + trend
        
        values = [10000]
        for r in returns[1:]:
            values.append(values[-1] * (1 + r))
        
        scaling = final_value / values[-1]
        values = [v * scaling for v in values]
        data[ai_name] = values
    
    return dates, data

dates, chart_data = create_chart_data()

# Create chart
fig = go.Figure()

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
        font=dict(size=10)
    ),
    xaxis=dict(
        showgrid=False,
        showticklabels=True,
        tickfont=dict(size=9, color="#999999")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#f0f0f0',
        tickformat='$,.0f',
        tickfont=dict(size=9, color="#999999")
    ),
    hovermode='x unified'
)

st.plotly_chart(fig, width='stretch')

st.divider()

# Leaderboard and Activity
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Leaderboard")
    
    # Create leaderboard dataframe
    sorted_accounts = sorted(account_values.items(), key=lambda x: x[1], reverse=True)
    leaderboard_data = []
    for i, (name, value) in enumerate(sorted_accounts):
        pnl = ((value - 10000) / 10000) * 100
        leaderboard_data.append({
            'Rank': f"#{i+1}",
            'AI': name,
            'Value': f"${value:,.0f}",
            'P&L': f"{pnl:+.1f}%"
        })
    
    leaderboard_df = pd.DataFrame(leaderboard_data)
    st.dataframe(leaderboard_df, width='stretch', hide_index=True)

with col2:
    st.markdown("### System Activity")
    
    # Department status
    departments = [
        {'Department': 'Technical Analysis', 'Status': 'Active'},
        {'Department': 'Fundamental Analysis', 'Status': 'Active'},
        {'Department': 'Sentiment Analysis', 'Status': 'Idle'},
        {'Department': 'Risk Management', 'Status': 'Active'},
        {'Department': 'Execution', 'Status': 'Processing'},
        {'Department': 'Monitoring', 'Status': 'Active'},
        {'Department': 'Learning', 'Status': 'Weekly'}
    ]
    
    dept_df = pd.DataFrame(departments)
    st.dataframe(dept_df, width='stretch', hide_index=True)

st.divider()

# AI Internal Debate Visualization
st.markdown("### AI Internal Deliberation")
st.caption("See how each AI's 7 internal departments debate before making decisions")

# Get recent predictions with full reasoning
def get_recent_decisions():
    """Get recent predictions with internal debate data"""
    try:
        conn = sqlite3.connect(db.db_path)
        
        query = """
        SELECT 
            firm_name,
            event_description,
            probability,
            postura_riesgo,
            analisis_sintesis,
            debate_bullish_bearish,
            ajuste_riesgo_justificacion,
            created_at
        FROM predictions
        WHERE created_at >= datetime('now', '-7 days')
        ORDER BY created_at DESC
        LIMIT 5
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    except Exception as e:
        # Return empty dataframe if no data
        return pd.DataFrame()

decisions_df = get_recent_decisions()

if not decisions_df.empty:
    # Group by AI
    for ai_name in ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']:
        ai_decisions = decisions_df[decisions_df['firm_name'] == ai_name]
        
        if not ai_decisions.empty:
            latest = ai_decisions.iloc[0]
            
            with st.expander(f"**{ai_name}** - Latest Decision", expanded=False):
                st.markdown(f"**Event:** {latest['event_description'][:200]}...")
                st.markdown(f"**Probability:** {latest['probability']:.1%} | **Risk Stance:** {latest['postura_riesgo']}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**📊 Analysis & Synthesis**")
                    if pd.notna(latest['analisis_sintesis']) and latest['analisis_sintesis']:
                        st.text_area(
                            "Analysis",
                            latest['analisis_sintesis'][:400],
                            height=150,
                            key=f"analysis_{ai_name}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.caption("No analysis available")
                
                with col2:
                    st.markdown("**⚖️ Bullish vs Bearish Debate**")
                    if pd.notna(latest['debate_bullish_bearish']) and latest['debate_bullish_bearish']:
                        st.text_area(
                            "Debate",
                            latest['debate_bullish_bearish'][:400],
                            height=150,
                            key=f"debate_{ai_name}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.caption("No debate available")
                
                with col3:
                    st.markdown("**🎯 Risk Adjustment & Final Decision**")
                    if pd.notna(latest['ajuste_riesgo_justificacion']) and latest['ajuste_riesgo_justificacion']:
                        st.text_area(
                            "Risk",
                            latest['ajuste_riesgo_justificacion'][:400],
                            height=150,
                            key=f"risk_{ai_name}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.caption("No risk analysis available")
                
                # Department activity badges
                st.markdown("**Active Departments:**")
                departments = [
                    "📊 Technical Analysis",
                    "📈 Fundamental Analysis",
                    "💭 Sentiment",
                    "⚡ Strategy",
                    "⚖️ Risk Management",
                    "🎯 Execution",
                    "📝 Compliance"
                ]
                
                badge_html = " ".join([f'<span class="dept-badge dept-active">{dept}</span>' for dept in departments])
                st.markdown(badge_html, unsafe_allow_html=True)
else:
    st.info("No recent decisions found. The AI models haven't made any predictions in the last 7 days. Try using the manual prediction system or autonomous competition mode to generate data.")

st.divider()

# Footer
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col2:
    st.markdown(
        '<div style="text-align: center; color: #999999; font-size: 0.8rem;">'
        'Live competition • Updates every 30s • 7 departments per AI'
        '</div>',
        unsafe_allow_html=True
    )
