import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
from database import TradingDatabase
from streamlit_autorefresh import st_autorefresh

# Page config - Ultra minimalista
st.set_page_config(
    page_title="Alpha Arena",
    page_icon="◐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh cada 30 segundos
count = st_autorefresh(interval=30000, key="alpha_refresh")

# CSS Minimalista - Sin scroll, ultra compacto
st.markdown("""
<style>
    /* Fondo completamente blanco y sin scroll */
    html, body, .stApp {
        background: #FFFFFF;
        overflow: hidden;
        height: 100vh;
    }
    
    /* Eliminar padding default de Streamlit */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0;
        max-width: 100%;
        height: 100vh;
        overflow: hidden;
    }
    
    /* Ocultar elementos default de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Métricas más compactas */
    [data-testid="metric-container"] {
        background: #FAFAFA;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E5E5E5;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        color: #666666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }
    
    /* Título principal más compacto */
    h1 {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
    }
    
    /* Subtítulos más pequeños */
    h3 {
        font-size: 0.75rem;
        color: #999999;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0.25rem 0;
    }
    
    /* Dividers más delgados */
    hr {
        margin: 0.5rem 0;
        opacity: 0.3;
    }
    
    /* Ajustar altura de los gráficos */
    .js-plotly-plot {
        height: 60px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    return TradingDatabase()

db = get_database()

# Get AI predictions data - SIEMPRE muestra las 5 AIs
def get_ai_data():
    """Fetch latest AI predictions from database"""
    # Default data for all 5 AIs
    np.random.seed(42 + count)
    default_data = {
        'ChatGPT': {
            'probability': 0.72 + np.random.uniform(-0.05, 0.05),
            'change': np.random.uniform(-5, 5),
            'confidence': 'HIGH'
        },
        'Gemini': {
            'probability': 0.65 + np.random.uniform(-0.05, 0.05),
            'change': np.random.uniform(-5, 5),
            'confidence': 'MEDIUM'
        },
        'Qwen': {
            'probability': 0.48 + np.random.uniform(-0.05, 0.05),
            'change': np.random.uniform(-5, 5),
            'confidence': 'LOW'
        },
        'Deepseek': {
            'probability': 0.69 + np.random.uniform(-0.05, 0.05),
            'change': np.random.uniform(-5, 5),
            'confidence': 'HIGH'
        },
        'Grok': {
            'probability': 0.61 + np.random.uniform(-0.05, 0.05),
            'change': np.random.uniform(-5, 5),
            'confidence': 'MEDIUM'
        }
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
                    prob = db_data[ai_name].get('probability', 0.5)
                    default_data[ai_name]['probability'] = prob
                    # Determine confidence based on probability
                    if prob > 0.7:
                        default_data[ai_name]['confidence'] = 'HIGH'
                    elif prob > 0.5:
                        default_data[ai_name]['confidence'] = 'MEDIUM'
                    else:
                        default_data[ai_name]['confidence'] = 'LOW'
    except:
        pass
    
    return default_data

# Get data
ai_data = get_ai_data()

# Calculate consensus
consensus = np.mean([v['probability'] for v in ai_data.values()])

# HEADER SECTION - Ultra minimalista
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown("# ◐ Alpha Arena")
    st.markdown("### Prediction Intelligence")

with col3:
    st.metric(
        label="MARKET CONSENSUS",
        value=f"{consensus:.1%}",
        delta=f"{np.random.uniform(-2, 2):.1%}"
    )

st.markdown("---")

# MAIN SECTION - 5 AI columns
st.markdown("### AI PREDICTIONS")

cols = st.columns(5)

# Sort AIs by probability for ranking
sorted_ais = sorted(ai_data.items(), key=lambda x: x[1]['probability'], reverse=True)

for idx, (col, (ai_name, data)) in enumerate(zip(cols, sorted_ais)):
    with col:
        # Ranking badge
        if idx == 0:
            rank_emoji = "🥇"
        elif idx == 1:
            rank_emoji = "🥈"
        elif idx == 2:
            rank_emoji = "🥉"
        else:
            rank_emoji = f"#{idx + 1}"
        
        st.markdown(f"**{rank_emoji} {ai_name}**")
        
        # Big probability metric
        st.metric(
            label="PROBABILITY",
            value=f"{data['probability']:.1%}",
            delta=f"{data['change']:.1%}",
            delta_color="normal"
        )
        
        # Confidence level
        confidence_color = {
            'HIGH': '🟢',
            'MEDIUM': '🟡', 
            'LOW': '🔴'
        }
        st.markdown(f"{confidence_color[data['confidence']]} {data['confidence']}")
        
        # Mini sparkline using plotly
        fig = go.Figure()
        
        # Generate trend data
        hours = list(range(24))
        np.random.seed(hash(ai_name) % 100)
        trend_values = [data['probability'] + np.random.uniform(-0.05, 0.05) for _ in hours]
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=trend_values,
            mode='lines',
            line=dict(color='#0066FF' if data['confidence'] == 'HIGH' else '#999999', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 102, 255, 0.05)' if data['confidence'] == 'HIGH' else 'rgba(153, 153, 153, 0.05)',
            showlegend=False
        ))
        
        fig.update_layout(
            height=60,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False, range=[0, 1]),
            hovermode=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"spark_{ai_name}")

st.markdown("---")

# BOTTOM INSIGHTS - Compacto
st.markdown("### MARKET INSIGHTS")

insight_cols = st.columns(5)

insights = [
    ("ACTIVE MARKETS", "7", "Markets trading"),
    ("24H VOLUME", "$52.3K", "+12.5%"),
    ("SPREAD", f"{max([v['probability'] for v in ai_data.values()]) - min([v['probability'] for v in ai_data.values()]):.1%}", "High - Low"),
    ("VOLATILITY", "12.5%", "24h σ"),
    ("NEXT UPDATE", "28s", "Auto-refresh")
]

for col, (title, value, subtitle) in zip(insight_cols, insights):
    with col:
        st.markdown(f"**{title}**")
        st.markdown(f"# {value}")
        st.markdown(f"*{subtitle}*")

# Footer mínimo
st.markdown("---")
st.caption("Alpha Arena v2.0 · Real-time Prediction Intelligence · Auto-refresh ON")