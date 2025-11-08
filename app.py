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

st.set_page_config(
    page_title="TradingAgents Framework",
    page_icon="📈",
    layout="wide"
)

if 'db' not in st.session_state:
    st.session_state.db = TradingDatabase()
    
    firms = ['ChatGPT', 'Gemini', 'Qwen', 'Deepseek', 'Grok']
    for firm in firms:
        st.session_state.db.initialize_firm_portfolio(firm, 10000.0)

if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = FirmOrchestrator()

if 'predictions' not in st.session_state:
    st.session_state.predictions = {}

if 'technical_data' not in st.session_state:
    st.session_state.technical_data = None

if 'fundamental_data' not in st.session_state:
    st.session_state.fundamental_data = None

if 'sentiment_data' not in st.session_state:
    st.session_state.sentiment_data = None

st.title("📈 TradingAgents Framework")
st.markdown("### Sistema de 5 Firmas Autónomas de Trading con LLMs")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Nueva Predicción",
    "🔍 Panel de Transparencia",
    "📊 Dashboard Comparativo",
    "📥 Exportar Predicción"
])

with tab1:
    st.header("Configurar Nueva Predicción")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        event_description = st.text_area(
            "Descripción del Evento de Predicción",
            placeholder="Ej: Apple (AAPL) cerrará por encima de $200 el 31/Dic/2025 (TRUE/FALSE)",
            height=100
        )
    
    with col2:
        symbol = st.text_input("Símbolo del Activo", value="AAPL")
    
    st.markdown("---")
    
    st.subheader("📊 Paso 1: Recopilar Datos de Mercado")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔧 Obtener Datos Técnicos", use_container_width=True):
            with st.spinner("Recopilando datos técnicos de Alpha Vantage..."):
                alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "48A9UL94ADQTPIE2")
                collector = AlphaVantageCollector(alpha_vantage_key)
                st.session_state.technical_data = collector.get_technical_indicators(symbol)
                st.success("Datos técnicos obtenidos!")
    
    with col2:
        if st.button("📈 Obtener Datos Fundamentales", use_container_width=True):
            with st.spinner("Recopilando datos fundamentales de yfinance..."):
                collector = YFinanceCollector()
                st.session_state.fundamental_data = collector.get_fundamental_data(symbol)
                st.success("Datos fundamentales obtenidos!")
    
    with col3:
        reddit_configured = os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET")
        
        if st.button("💬 Obtener Sentimiento Reddit", use_container_width=True, disabled=not reddit_configured):
            if reddit_configured:
                with st.spinner("Analizando sentimiento en Reddit..."):
                    collector = RedditSentimentCollector(
                        client_id=os.environ.get("REDDIT_CLIENT_ID"),
                        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
                        user_agent="TradingAgents/1.0"
                    )
                    st.session_state.sentiment_data = collector.analyze_subreddit_sentiment(symbol)
                    st.success("Análisis de sentimiento completado!")
            else:
                st.warning("Reddit API no configurada. Configure REDDIT_CLIENT_ID y REDDIT_CLIENT_SECRET.")
    
    if st.session_state.technical_data or st.session_state.fundamental_data or st.session_state.sentiment_data:
        st.markdown("---")
        st.subheader("📋 Informes Consolidados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.technical_data:
                with st.expander("📊 Informe Técnico", expanded=False):
                    technical_report = format_technical_report(st.session_state.technical_data)
                    st.text(technical_report)
        
        with col2:
            if st.session_state.fundamental_data:
                with st.expander("📈 Informe Fundamental", expanded=False):
                    fundamental_report = format_fundamental_report(st.session_state.fundamental_data)
                    st.text(fundamental_report)
        
        with col3:
            if st.session_state.sentiment_data:
                with st.expander("💬 Informe de Sentimiento", expanded=False):
                    sentiment_report = format_sentiment_report(st.session_state.sentiment_data)
                    st.text(sentiment_report)
    
    st.markdown("---")
    st.subheader("🤖 Paso 2: Ejecutar Análisis de las 5 Firmas")
    
    if st.button("🚀 Ejecutar Análisis Completo", type="primary", use_container_width=True):
        if not event_description:
            st.error("Por favor ingrese la descripción del evento de predicción.")
        elif not (st.session_state.technical_data or st.session_state.fundamental_data or st.session_state.sentiment_data):
            st.error("Por favor recopile al menos un tipo de datos de mercado antes de ejecutar el análisis.")
        else:
            technical_report = format_technical_report(st.session_state.technical_data) if st.session_state.technical_data else "No disponible"
            fundamental_report = format_fundamental_report(st.session_state.fundamental_data) if st.session_state.fundamental_data else "No disponible"
            sentiment_report = format_sentiment_report(st.session_state.sentiment_data) if st.session_state.sentiment_data else "No disponible"
            
            firms = st.session_state.orchestrator.get_all_firms()
            
            st.session_state.predictions = {}
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, (firm_name, firm) in enumerate(firms.items()):
                status_text.text(f"Ejecutando análisis con {firm_name}...")
                
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
                            st.warning(f"Error guardando predicción de {firm_name} en base de datos: {db_error}")
                            st.session_state.predictions[firm_name] = prediction
                    else:
                        st.session_state.predictions[firm_name] = prediction
                
                except Exception as e:
                    st.session_state.predictions[firm_name] = {
                        'error': str(e),
                        'firm_name': firm_name
                    }
                
                progress_bar.progress((i + 1) / len(firms))
            
            status_text.text("¡Análisis completado!")
            st.success("✅ Todas las firmas han completado su análisis. Revisa los resultados en las pestañas de Transparencia y Dashboard.")
            st.balloons()

with tab2:
    st.header("🔍 Panel de Transparencia - Razonamiento de cada IA")
    
    if not st.session_state.predictions:
        st.info("Ejecute primero el análisis en la pestaña 'Nueva Predicción' para ver el razonamiento de cada firma.")
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
                        st.metric("Probabilidad Final", f"{prediction.get('probabilidad_final_prediccion', 0):.2%}")
                    with col2:
                        st.metric("Postura de Riesgo", prediction.get('postura_riesgo', 'N/A'))
                    with col3:
                        st.metric("Nivel de Confianza", f"{prediction.get('nivel_confianza', 0)}/100")
                    
                    st.markdown("---")
                    
                    st.markdown("### 📊 ETAPA I: Síntesis Analítica")
                    st.info(prediction.get('analisis_sintesis', 'No disponible'))
                    
                    st.markdown("### 💭 ETAPA II: Debate Bullish vs Bearish")
                    st.warning(prediction.get('debate_bullish_bearish', 'No disponible'))
                    
                    st.markdown("### ⚖️ ETAPA III: Ajuste de Riesgo y Decisión Final")
                    st.success(prediction.get('ajuste_riesgo_justificacion', 'No disponible'))
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tokens Usados", f"{prediction.get('tokens_used', 0):,}")
                    with col2:
                        st.metric("Costo Estimado", f"${prediction.get('estimated_cost', 0):.4f}")

with tab3:
    st.header("📊 Dashboard Comparativo de Firmas")
    
    if st.session_state.predictions:
        st.subheader("🎯 Predicciones Actuales")
        
        predictions_df = []
        for firm_name, pred in st.session_state.predictions.items():
            if 'error' not in pred:
                predictions_df.append({
                    'Firma': firm_name,
                    'Probabilidad': pred.get('probabilidad_final_prediccion', 0),
                    'Postura': pred.get('postura_riesgo', 'N/A'),
                    'Confianza': pred.get('nivel_confianza', 0),
                    'Dirección': pred.get('direccion_preliminar', 'N/A'),
                    'Tokens': pred.get('tokens_used', 0),
                    'Costo': pred.get('estimated_cost', 0)
                })
        
        if predictions_df:
            df = pd.DataFrame(predictions_df)
            
            fig = px.bar(
                df,
                x='Firma',
                y='Probabilidad',
                color='Postura',
                title='Probabilidades de Predicción por Firma',
                labels={'Probabilidad': 'Probabilidad (0-1)'},
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
                    values='Confianza',
                    names='Firma',
                    title='Distribución de Niveles de Confianza'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                fig3 = px.bar(
                    df,
                    x='Firma',
                    y='Costo',
                    title='Costo Estimado por Firma (USD)',
                    labels={'Costo': 'Costo (USD)'}
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🏆 Rendimiento Histórico de las Firmas")
    
    performances = st.session_state.db.get_all_firm_performances()
    
    if performances:
        perf_df = pd.DataFrame(performances)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Predicciones", sum(p['total_predictions'] for p in performances))
        with col2:
            total_correct = sum(p['correct_predictions'] for p in performances)
            total_preds = sum(p['total_predictions'] for p in performances)
            overall_accuracy = (total_correct / total_preds * 100) if total_preds > 0 else 0
            st.metric("Precisión General", f"{overall_accuracy:.1f}%")
        with col3:
            total_profit = sum(p['total_profit'] for p in performances)
            st.metric("Ganancia Total Simulada", f"${total_profit:,.2f}")
        
        st.dataframe(perf_df, use_container_width=True)
        
        if perf_df['total_predictions'].sum() > 0:
            fig4 = px.bar(
                perf_df,
                x='firm_name',
                y='accuracy',
                title='Precisión Histórica por Firma (%)',
                labels={'firm_name': 'Firma', 'accuracy': 'Precisión (%)'}
            )
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No hay datos históricos aún. Las predicciones se guardarán automáticamente.")

with tab4:
    st.header("📥 Exportar Predicción para Opinion.trade")
    
    if not st.session_state.predictions:
        st.info("Ejecute primero el análisis para poder exportar predicciones.")
    else:
        valid_predictions = {k: v for k, v in st.session_state.predictions.items() if 'error' not in v}
        
        if valid_predictions:
            st.subheader("Seleccione qué predicción enviar")
            
            selected_firm = st.selectbox(
                "Firma",
                options=list(valid_predictions.keys()),
                help="Seleccione la firma cuya predicción desea exportar"
            )
            
            if selected_firm:
                prediction = valid_predictions[selected_firm]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Probabilidad", f"{prediction.get('probabilidad_final_prediccion', 0):.4f}")
                    st.metric("Postura de Riesgo", prediction.get('postura_riesgo', 'N/A'))
                
                with col2:
                    st.metric("Nivel de Confianza", f"{prediction.get('nivel_confianza', 0)}/100")
                    perf = st.session_state.db.get_firm_performance(selected_firm)
                    if perf:
                        st.metric("Precisión Histórica", f"{perf['accuracy']:.1f}%")
                
                st.markdown("---")
                
                export_data = {
                    "firma_generadora": prediction.get('modelo_llm', selected_firm),
                    "fecha_prediccion": prediction.get('fecha_prediccion', datetime.now().strftime('%Y-%m-%d')),
                    "evento_opinion_trade": prediction.get('evento_opinion_trade', ''),
                    "probabilidad_final_prediccion": prediction.get('probabilidad_final_prediccion', 0.5),
                    "postura_riesgo": prediction.get('postura_riesgo', 'NEUTRAL'),
                    "nivel_confianza": prediction.get('nivel_confianza', 50),
                    "analisis_sintesis": prediction.get('analisis_sintesis', ''),
                    "debate_bullish_bearish": prediction.get('debate_bullish_bearish', ''),
                    "ajuste_riesgo_justificacion": prediction.get('ajuste_riesgo_justificacion', ''),
                    "api_key_opinion_trade": os.environ.get("OPINION_TRADE_API_KEY", "")
                }
                
                st.json(export_data)
                
                json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                
                st.download_button(
                    label="💾 Descargar JSON",
                    data=json_str,
                    file_name=f"prediction_{selected_firm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                st.info("""
                **Próximos pasos para enviar a Opinion.trade:**
                1. Descargue el archivo JSON
                2. Revise que los datos sean correctos
                3. Use la API de Opinion.trade para enviar la predicción
                4. Una vez enviada, registre el resultado real para actualizar el rendimiento de la firma
                """)
        else:
            st.warning("No hay predicciones válidas para exportar. Todas las firmas reportaron errores.")

st.sidebar.title("⚙️ Configuración")

with st.sidebar.expander("🔑 API Keys Configuradas"):
    st.write("✅ Alpha Vantage:", "Configurada" if os.environ.get("ALPHA_VANTAGE_API_KEY") else "❌ No configurada")
    st.write("✅ OpenAI (AI Int.):", "Configurada" if os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") else "❌ No configurada")
    st.write("✅ Gemini (AI Int.):", "Configurada" if os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY") else "❌ No configurada")
    st.write("✅ Qwen:", "Configurada" if os.environ.get("QWEN_API_KEY") else "⚠️ Opcional")
    st.write("✅ Deepseek:", "Configurada" if os.environ.get("DEEPSEEK_API_KEY") else "⚠️ Opcional")
    st.write("✅ Grok (xAI):", "Configurada" if os.environ.get("XAI_API_KEY") else "⚠️ Opcional")
    st.write("✅ Reddit:", "Configurada" if (os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET")) else "⚠️ Opcional")
    st.write("✅ Opinion.trade:", "Configurada" if os.environ.get("OPINION_TRADE_API_KEY") else "⚠️ Pendiente")

st.sidebar.markdown("---")
st.sidebar.info("""
**TradingAgents Framework v1.0**

Sistema autónomo de predicciones de mercado con 5 firmas de LLMs compitiendo.

Cada firma simula 7 roles internos para generar predicciones optimizadas.
""")
