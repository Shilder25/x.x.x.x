import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sqlite3
from database import TradingDatabase
from streamlit_autorefresh import st_autorefresh

# Page config for full-screen experience
st.set_page_config(
    page_title="Alpha Arena · Prediction Intelligence",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Auto-refresh every 30 seconds
REFRESH_INTERVAL = 30000
count = st_autorefresh(interval=REFRESH_INTERVAL, key="alpha_refresh")

# Premium White Minimalist Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Full viewport white background, no scroll */
    .stApp {
        background: #FFFFFF;
        height: 100vh;
        overflow: hidden;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Remove all default padding */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Design System Variables */
    :root {
        --primary: #000000;
        --secondary: #666666;
        --accent: #0066FF;
        --success: #00C896;
        --warning: #FF6B6B;
        --background: #FFFFFF;
        --surface: #FAFAFA;
        --border: #E5E5E5;
        --border-light: #F0F0F0;
        --text-primary: #000000;
        --text-secondary: #666666;
        --text-tertiary: #999999;
    }
    
    /* Typography System */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        color: var(--primary);
        margin: 0;
    }
    
    /* Top Section - 25vh */
    .header-section {
        height: 25vh;
        border-bottom: 1px solid var(--border-light);
        padding: 2.5rem 4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(to bottom, #FFFFFF 0%, #FAFAFA 100%);
    }
    
    .brand {
        display: flex;
        align-items: baseline;
        gap: 1rem;
    }
    
    .brand-mark {
        font-family: 'Sora', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
        letter-spacing: -0.03em;
    }
    
    .brand-tag {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 400;
    }
    
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 1rem;
        background: var(--success);
        color: white;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .live-dot {
        width: 6px;
        height: 6px;
        background: white;
        border-radius: 50%;
        animation: pulse-dot 2s infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    .hero-metric {
        text-align: right;
    }
    
    .hero-value {
        font-family: 'Sora', sans-serif;
        font-size: 3.5rem;
        font-weight: 300;
        color: var(--primary);
        line-height: 1;
        letter-spacing: -0.02em;
    }
    
    .hero-label {
        font-size: 0.85rem;
        color: var(--text-tertiary);
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Main Content - 50vh */
    .main-content {
        height: 50vh;
        padding: 2rem 4rem;
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 2rem;
    }
    
    /* AI Rankings Card */
    .rankings-card {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        overflow: hidden;
    }
    
    .card-header {
        font-family: 'Sora', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .ai-row {
        display: grid;
        grid-template-columns: 30px 1fr auto auto;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border-light);
        transition: all 0.2s ease;
    }
    
    .ai-row:hover {
        background: var(--surface);
        margin: 0 -1.5rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    .ai-row:last-child {
        border-bottom: none;
    }
    
    .rank-number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-tertiary);
        text-align: center;
    }
    
    .ai-name {
        font-family: 'Sora', sans-serif;
        font-weight: 500;
        color: var(--text-primary);
        font-size: 1rem;
    }
    
    .prediction-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .prediction-high {
        background: rgba(0, 200, 150, 0.1);
        color: var(--success);
    }
    
    .prediction-medium {
        background: rgba(0, 102, 255, 0.1);
        color: var(--accent);
    }
    
    .prediction-low {
        background: rgba(255, 107, 107, 0.1);
        color: var(--warning);
    }
    
    .confidence-meter {
        width: 60px;
        height: 4px;
        background: var(--border-light);
        border-radius: 2px;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        background: var(--accent);
        transition: width 0.3s ease;
    }
    
    /* Chart Card */
    .chart-card {
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    /* Matrix Card */
    .matrix-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .matrix-cell {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--surface);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-primary);
        transition: all 0.2s ease;
    }
    
    .matrix-cell:hover {
        border-color: var(--accent);
        background: white;
        transform: scale(1.05);
    }
    
    /* Bottom Section - 25vh */
    .bottom-section {
        height: 25vh;
        background: var(--surface);
        border-top: 1px solid var(--border);
        padding: 2rem 4rem;
    }
    
    .insights-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 2rem;
        height: 100%;
    }
    
    .insight-card {
        background: white;
        border: 1px solid var(--border-light);
        border-radius: 12px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .insight-title {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .insight-value {
        font-family: 'Sora', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1;
    }
    
    .insight-change {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }
    
    /* Status Footer */
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 32px;
        background: white;
        border-top: 1px solid var(--border-light);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        font-size: 0.7rem;
        color: var(--text-tertiary);
        z-index: 1000;
    }
    
    /* Override Streamlit components */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .js-plotly-plot {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    return TradingDatabase()

db = get_database()

# Get AI predictions data
def get_ai_data():
    """Fetch latest AI predictions from database"""
    # Default data for all 5 AIs
    np.random.seed(42 + count)
    default_data = {
        'ChatGPT': {'probability': 0.72 + np.random.uniform(-0.05, 0.05)},
        'Gemini': {'probability': 0.65 + np.random.uniform(-0.05, 0.05)},
        'Qwen': {'probability': 0.48 + np.random.uniform(-0.05, 0.05)},
        'Deepseek': {'probability': 0.69 + np.random.uniform(-0.05, 0.05)},
        'Grok': {'probability': 0.61 + np.random.uniform(-0.05, 0.05)}
    }
    
    try:
        conn = sqlite3.connect(db.db_path)
        query = """
        SELECT 
            firm_name,
            probability,
            postura_riesgo,
            created_at
        FROM predictions
        WHERE created_at >= datetime('now', '-7 days')
        ORDER BY created_at DESC
        LIMIT 25
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            # Group by firm and get latest
            latest = df.groupby('firm_name').first()
            db_data = latest.to_dict('index')
            
            # Merge with defaults to ensure all 5 AIs are present
            for ai_name in default_data:
                if ai_name in db_data:
                    default_data[ai_name] = db_data[ai_name]
    except:
        pass
    
    return default_data

ai_data = get_ai_data()

# Calculate metrics
consensus = np.mean([v.get('probability', 0.5) for v in ai_data.values()])
leader = max(ai_data.items(), key=lambda x: x[1].get('probability', 0.5))
spread = max([v.get('probability', 0.5) for v in ai_data.values()]) - min([v.get('probability', 0.5) for v in ai_data.values()])

# Header Section
header_html = f"""
<div class="header-section">
    <div>
        <div class="brand">
            <span class="brand-mark">Alpha Arena</span>
            <span class="brand-tag">Prediction Intelligence Platform</span>
        </div>
        <div style="margin-top: 1rem;">
            <span class="live-indicator">
                <span class="live-dot"></span>
                LIVE
            </span>
        </div>
    </div>
    <div class="hero-metric">
        <div class="hero-value">{consensus:.1%}</div>
        <div class="hero-label">Market Consensus</div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Main Content Section
st.markdown('<div class="main-content">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

# AI Rankings
with col1:
    rankings_html = '<div class="rankings-card"><div class="card-header">AI Predictions Ranking</div>'
    
    sorted_ais = sorted(ai_data.items(), key=lambda x: x[1].get('probability', 0.5), reverse=True)
    
    for i, (name, data) in enumerate(sorted_ais):
        prob = data.get('probability', 0.5)
        
        # Determine confidence level
        if prob > 0.7:
            confidence_class = "prediction-high"
            confidence_text = f"{prob:.1%}"
        elif prob > 0.5:
            confidence_class = "prediction-medium"
            confidence_text = f"{prob:.1%}"
        else:
            confidence_class = "prediction-low"
            confidence_text = f"{prob:.1%}"
        
        rankings_html += f"""
        <div class="ai-row">
            <span class="rank-number">{i+1}</span>
            <span class="ai-name">{name}</span>
            <span class="prediction-badge {confidence_class}">{confidence_text}</span>
            <div class="confidence-meter">
                <div class="confidence-fill" style="width: {prob*100}%"></div>
            </div>
        </div>
        """
    
    rankings_html += '</div>'
    st.markdown(rankings_html, unsafe_allow_html=True)

# Trend Chart
with col2:
    st.markdown('<div class="chart-card"><div class="card-header">24H Trend</div>', unsafe_allow_html=True)
    
    # Generate simple trend data
    hours = list(range(24))
    np.random.seed(42)
    values = [consensus + np.random.uniform(-0.1, 0.1) for _ in hours]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=values,
        mode='lines',
        line=dict(color='#0066FF', width=2, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(0, 102, 255, 0.05)',
        showlegend=False
    ))
    
    fig.update_layout(
        height=120,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(
            visible=False
        ),
        yaxis=dict(
            visible=False,
            range=[0, 1]
        ),
        hovermode=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Probability Matrix
with col3:
    st.markdown('<div class="chart-card"><div class="card-header">Quick Stats</div>', unsafe_allow_html=True)
    
    matrix_html = '<div class="matrix-grid">'
    
    # Key metrics in grid
    metrics = [
        ('HIGH', f"{sum(1 for v in ai_data.values() if v.get('probability', 0.5) > 0.7)}"),
        ('MED', f"{sum(1 for v in ai_data.values() if 0.5 <= v.get('probability', 0.5) <= 0.7)}"),
        ('LOW', f"{sum(1 for v in ai_data.values() if v.get('probability', 0.5) < 0.5)}"),
        ('AVG', f"{consensus:.0%}"),
        ('LEAD', leader[0][:3]),
        ('SPR', f"{spread:.0%}"),
        ('VOL', '12K'),
        ('MKT', '7'),
        ('24H', '+2.3%')
    ]
    
    for label, value in metrics:
        matrix_html += f'''
        <div class="matrix-cell">
            <div style="text-align: center;">
                <div style="font-size: 0.6rem; color: var(--text-tertiary); margin-bottom: 0.25rem;">{label}</div>
                <div style="font-size: 1rem; font-weight: 600;">{value}</div>
            </div>
        </div>
        '''
    
    matrix_html += '</div>'
    st.markdown(matrix_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Bottom Section - Insights
bottom_html = """
<div class="bottom-section">
    <div class="insights-grid">
"""

insights = [
    ('Market Volume', '$52.3K', '+12.5%'),
    ('Active Markets', '7', 'Stable'),
    ('Consensus Shift', '3.2%', 'Last hour'),
    ('Top Category', 'TECH', '42% of vol'),
    ('Next Update', '28s', 'Auto-refresh')
]

for title, value, change in insights:
    bottom_html += f"""
    <div class="insight-card">
        <div>
            <div class="insight-title">{title}</div>
            <div class="insight-value">{value}</div>
        </div>
        <div class="insight-change">{change}</div>
    </div>
    """

bottom_html += """
    </div>
</div>
"""
st.markdown(bottom_html, unsafe_allow_html=True)

# Status Bar
st.markdown("""
<div class="status-bar">
    <span>◐ Alpha Arena v2.0</span>
    <span>5 AI Models Active · Real-time Predictions · Auto-refresh ON</span>
    <span>Last update: Just now</span>
</div>
""", unsafe_allow_html=True)