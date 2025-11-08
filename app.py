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

st.title("📈 TradingAgents Framework")
st.markdown("### Sistema de 5 Firmas Autónomas de Trading con LLMs")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 Nueva Predicción",
    "🔍 Panel de Transparencia",
    "📊 Dashboard Comparativo",
    "🤖 Recomendaciones & Consenso",
    "📤 Enviar a Opinion.trade",
    "📝 Registrar Resultados",
    "🤖 Competencia Autónoma"
])

with tab1:
    st.markdown("## 🎯 Sistema Manual de Predicciones")
    st.markdown("##### Genera predicciones utilizando las 5 firmas de análisis con LLM")
    
    st.divider()
    
    with st.container():
        st.markdown("### 📝 Paso 1: Configuración del Evento")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            event_description = st.text_area(
                "Descripción del Evento de Predicción",
                placeholder="Ej: Apple (AAPL) cerrará por encima de $200 el 31/Dic/2025 (TRUE/FALSE)",
                height=100,
                help="Describe claramente el evento que quieres predecir"
            )
        
        with col2:
            symbol = st.text_input(
                "Símbolo",
                value="AAPL",
                help="Ticker del activo a analizar"
            )
            
            data_collected = sum([
                bool(st.session_state.technical_data),
                bool(st.session_state.fundamental_data),
                bool(st.session_state.sentiment_data)
            ])
            st.metric("Datos Recopilados", f"{data_collected}/3")
    
    st.divider()
    
    with st.container():
        st.markdown("### 📊 Paso 2: Recopilación de Datos de Mercado")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.markdown("#### 🔧 Datos Técnicos")
                st.caption("Indicadores y análisis técnico")
                if st.session_state.technical_data:
                    st.success("✓ Datos cargados")
                else:
                    st.info("Pendiente")
                
                if st.button("Obtener Técnicos", use_container_width=True, type="secondary"):
                    with st.spinner("Recopilando..."):
                        alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "48A9UL94ADQTPIE2")
                        collector = AlphaVantageCollector(alpha_vantage_key)
                        st.session_state.technical_data = collector.get_technical_indicators(symbol)
                        st.rerun()
        
        with col2:
            with st.container():
                st.markdown("#### 📈 Datos Fundamentales")
                st.caption("Financieros y valuación")
                if st.session_state.fundamental_data:
                    st.success("✓ Datos cargados")
                else:
                    st.info("Pendiente")
                
                if st.button("Obtener Fundamentales", use_container_width=True, type="secondary"):
                    with st.spinner("Recopilando..."):
                        collector = YFinanceCollector()
                        st.session_state.fundamental_data = collector.get_fundamental_data(symbol)
                        st.rerun()
        
        with col3:
            with st.container():
                st.markdown("#### 💬 Sentimiento Social")
                st.caption("Análisis de Reddit")
                reddit_configured = os.environ.get("REDDIT_CLIENT_ID") and os.environ.get("REDDIT_CLIENT_SECRET")
                
                if st.session_state.sentiment_data:
                    st.success("✓ Datos cargados")
                elif not reddit_configured:
                    st.warning("API no configurada")
                else:
                    st.info("Pendiente")
                
                if st.button("Obtener Sentimiento", use_container_width=True, type="secondary", disabled=not reddit_configured):
                    if reddit_configured:
                        with st.spinner("Analizando..."):
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
            st.markdown("### 📋 Informes de Datos Recopilados")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.technical_data:
                    with st.expander("📊 Ver Informe Técnico", expanded=False):
                        technical_report = format_technical_report(st.session_state.technical_data)
                        st.text(technical_report)
            
            with col2:
                if st.session_state.fundamental_data:
                    with st.expander("📈 Ver Informe Fundamental", expanded=False):
                        fundamental_report = format_fundamental_report(st.session_state.fundamental_data)
                        st.text(fundamental_report)
            
            with col3:
                if st.session_state.sentiment_data:
                    with st.expander("💬 Ver Informe de Sentimiento", expanded=False):
                        sentiment_report = format_sentiment_report(st.session_state.sentiment_data)
                        st.text(sentiment_report)
    
    st.divider()
    
    with st.container():
        st.markdown("### 🚀 Paso 3: Ejecutar Análisis Completo")
        st.caption("Las 5 firmas analizarán el evento con los datos recopilados")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Ejecutar Análisis de las 5 Firmas", type="primary", use_container_width=True):
                if not event_description:
                    st.error("⚠️ Por favor ingrese la descripción del evento")
                elif not (st.session_state.technical_data or st.session_state.fundamental_data or st.session_state.sentiment_data):
                    st.error("⚠️ Recopile al menos un tipo de datos antes de continuar")
                else:
                    technical_report = format_technical_report(st.session_state.technical_data) if st.session_state.technical_data else "No disponible"
                    fundamental_report = format_fundamental_report(st.session_state.fundamental_data) if st.session_state.fundamental_data else "No disponible"
                    sentiment_report = format_sentiment_report(st.session_state.sentiment_data) if st.session_state.sentiment_data else "No disponible"
                    
                    firms = st.session_state.orchestrator.get_all_firms()
                    
                    st.session_state.predictions = {}
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, (firm_name, firm) in enumerate(firms.items()):
                        status_text.text(f"🔄 Ejecutando análisis con {firm_name}...")
                        
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
                                    st.warning(f"Error guardando predicción de {firm_name}: {db_error}")
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
                    st.success("✅ ¡Análisis completado! Revisa los resultados en las siguientes pestañas")
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
    st.header("🤖 Recomendaciones & Consenso de Predicción")
    
    if not st.session_state.predictions:
        st.info("Ejecute primero el análisis para obtener recomendaciones.")
    else:
        st.subheader("🎯 Recomendación de Firma Basada en Histórico")
        
        recommendation = st.session_state.recommender.get_best_firm_recommendation()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Firma Recomendada", recommendation['recommended_firm'])
        with col2:
            st.metric("Confianza", recommendation['confidence'])
        with col3:
            if 'accuracy' in recommendation:
                st.metric("Precisión Histórica", f"{recommendation['accuracy']:.1f}%")
        
        st.info(f"**Razón:** {recommendation['reason']}")
        
        if recommendation.get('alternatives'):
            st.markdown(f"**Alternativas:** {', '.join(recommendation['alternatives'])}")
        
        st.markdown("---")
        
        st.subheader("🤝 Predicción por Consenso Ponderado")
        
        consensus = st.session_state.recommender.calculate_consensus_prediction(st.session_state.predictions)
        
        if consensus['participating_firms']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Probabilidad de Consenso", f"{consensus['consensus_probability']:.2%}")
                st.metric("Nivel de Acuerdo", f"{consensus['confidence']:.1f}%")
            
            with col2:
                st.markdown("**Firmas Participantes:**")
                for firm in consensus['participating_firms']:
                    weight = consensus['weights'].get(firm, 0)
                    prob = consensus['individual_probabilities'].get(firm, 0)
                    st.write(f"- {firm}: {prob:.2%} (peso: {weight:.2%})")
            
            st.markdown("---")
            
            st.markdown("**Interpretación:**")
            if consensus['confidence'] > 70:
                st.success("✅ Alto nivel de acuerdo entre las firmas. Predicción consensuada confiable.")
            elif consensus['confidence'] > 40:
                st.warning("⚠️ Nivel moderado de acuerdo. Hay cierta divergencia entre las firmas.")
            else:
                st.error("❌ Bajo nivel de acuerdo. Las firmas tienen opiniones muy diferentes.")
            
            st.markdown("---")
            
            st.subheader("📊 Visualización de Consenso")
            
            if consensus['individual_probabilities']:
                firms = list(consensus['individual_probabilities'].keys())
                probs = [consensus['individual_probabilities'][f] for f in firms]
                weights = [consensus['weights'][f] * 100 for f in firms]
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=firms,
                    y=probs,
                    name='Probabilidad Individual',
                    marker_color='lightblue'
                ))
                
                fig.add_trace(go.Scatter(
                    x=firms,
                    y=[consensus['consensus_probability']] * len(firms),
                    name='Consenso Ponderado',
                    mode='lines+markers',
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    title='Probabilidades Individuales vs. Consenso',
                    yaxis_title='Probabilidad',
                    yaxis_range=[0, 1],
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay predicciones válidas para calcular consenso.")
        
        st.markdown("---")
        
        st.subheader("📈 Análisis de Patrones de Razonamiento")
        
        pattern_analysis = st.session_state.recommender.analyze_reasoning_patterns()
        
        if pattern_analysis['total_analyzed'] > 0:
            st.write(f"**Total Analizado:** {pattern_analysis['total_analyzed']} predicciones resueltas")
            
            if pattern_analysis['patterns']:
                patterns_df = pd.DataFrame(pattern_analysis['patterns'])
                
                fig = px.bar(
                    patterns_df,
                    x='pattern_value',
                    y='accuracy',
                    color='total_profit',
                    title='Precisión por Postura de Riesgo',
                    labels={
                        'pattern_value': 'Postura de Riesgo',
                        'accuracy': 'Precisión (%)',
                        'total_profit': 'Ganancia Total'
                    },
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(patterns_df[['pattern_value', 'occurrences', 'accuracy', 'total_profit', 'avg_profit']], 
                            use_container_width=True)
            else:
                st.info("No hay patrones detectados aún.")
        else:
            st.info("No hay predicciones resueltas para analizar patrones.")
        
        st.markdown("---")
        
        st.subheader("🏆 Reporte de Atribución Detallado")
        
        attribution = st.session_state.recommender.get_firm_attribution_report()
        
        if attribution:
            attr_df = pd.DataFrame(attribution)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                wins = len(attr_df[attr_df['correct'] == True])
                st.metric("Victorias", wins)
            with col2:
                losses = len(attr_df[attr_df['correct'] == False])
                st.metric("Derrotas", losses)
            with col3:
                total_profit = attr_df['profit_loss'].sum()
                st.metric("P/L Total", f"${total_profit:,.2f}")
            with col4:
                best_firm = attr_df.groupby('firm_name')['profit_loss'].sum().idxmax()
                st.metric("Mejor Firma", best_firm)
            
            st.markdown("**Detalle por Firma:**")
            
            firm_summary = attr_df.groupby('firm_name').agg({
                'correct': lambda x: (x == True).sum(),
                'prediction_id': 'count',
                'profit_loss': 'sum'
            }).reset_index()
            
            firm_summary.columns = ['Firma', 'Victorias', 'Total', 'Ganancia']
            firm_summary['Precisión (%)'] = (firm_summary['Victorias'] / firm_summary['Total'] * 100).round(1)
            
            st.dataframe(firm_summary, use_container_width=True)
            
            with st.expander("Ver todas las atribuciones", expanded=False):
                display_attr = attr_df[['firm_name', 'event_description', 'predicted_probability', 
                                        'actual_result', 'correct', 'profit_loss', 'impact']]
                display_attr.columns = ['Firma', 'Evento', 'Prob. Predicha', 'Resultado', 
                                       'Correcto', 'P/L', 'Impacto']
                st.dataframe(display_attr, use_container_width=True, height=400)
        else:
            st.info("No hay datos de atribución disponibles. Registre resultados para ver este reporte.")

with tab5:
    st.header("📤 Enviar Predicción a Opinion.trade")
    
    if not st.session_state.predictions:
        st.info("Ejecute primero el análisis en la pestaña 'Nueva Predicción' para poder enviar predicciones.")
    else:
        valid_predictions = {k: v for k, v in st.session_state.predictions.items() if 'error' not in v}
        
        if valid_predictions:
            st.subheader("📊 Seleccione qué predicción enviar")
            
            selected_firm = st.selectbox(
                "Firma",
                options=list(valid_predictions.keys()),
                help="Seleccione la firma cuya predicción desea enviar a Opinion.trade",
                key="submit_firm_selector"
            )
            
            if selected_firm:
                prediction = valid_predictions[selected_firm]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Probabilidad", f"{prediction.get('probabilidad_final_prediccion', 0):.2%}")
                with col2:
                    st.metric("Postura de Riesgo", prediction.get('postura_riesgo', 'N/A'))
                with col3:
                    perf = st.session_state.db.get_firm_performance(selected_firm)
                    if perf and perf['total_predictions'] > 0:
                        st.metric("Precisión Histórica", f"{perf['accuracy']:.1f}%")
                    else:
                        st.metric("Precisión Histórica", "Sin historial")
                
                st.markdown("---")
                
                with st.expander("📝 Ver razonamiento completo", expanded=False):
                    st.markdown("**Síntesis Analítica:**")
                    st.info(prediction.get('analisis_sintesis', 'No disponible'))
                    st.markdown("**Conclusión del Debate:**")
                    st.warning(prediction.get('debate_bullish_bearish', 'No disponible')[:300] + "...")
                
                st.markdown("---")
                st.subheader("🎯 Configuración del Envío")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    event_id = st.text_input(
                        "ID del Evento en Opinion.trade",
                        placeholder="event_123abc",
                        help="Ingrese el ID del evento en Opinion.trade"
                    )
                
                with col2:
                    bet_amount = st.number_input(
                        "Cantidad a Apostar (USD)",
                        min_value=1.0,
                        max_value=1000.0,
                        value=10.0,
                        step=1.0,
                        help="Monto a apostar en esta predicción"
                    )
                
                st.markdown("---")
                
                if st.button("🚀 Enviar Predicción a Opinion.trade", type="primary", use_container_width=True):
                    if not event_id:
                        st.error("Por favor ingrese el ID del evento")
                    else:
                        with st.spinner("Enviando predicción a Opinion.trade..."):
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
                                st.success(f"✅ Predicción enviada exitosamente!")
                                st.info(f"**ID de Predicción:** {result.get('prediction_id', 'N/A')}")
                                st.balloons()
                                
                                st.markdown("---")
                                st.info("""
                                **Próximos pasos:**
                                1. Anote el ID de predicción mostrado arriba
                                2. Una vez que el evento se resuelva, vaya a la pestaña "Registrar Resultados"
                                3. Ingrese el resultado real (TRUE/FALSE) para actualizar las métricas de la firma
                                """)
                            else:
                                st.error(f"❌ Error al enviar predicción: {result.get('message', 'Error desconocido')}")
                                st.warning(f"Detalles: {result.get('error', '')}")
                
                st.markdown("---")
                
                with st.expander("💾 Descargar JSON (opcional)", expanded=False):
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
                        label="💾 Descargar JSON",
                        data=json_str,
                        file_name=f"prediction_{selected_firm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.warning("No hay predicciones válidas para enviar. Todas las firmas reportaron errores.")

with tab6:
    st.header("📝 Registrar Resultados de Predicciones")
    
    st.markdown("""
    Use esta interfaz para registrar los resultados reales de las predicciones enviadas.
    Esto actualiza las métricas de rendimiento de cada firma.
    """)
    
    st.markdown("---")
    
    recent_predictions = st.session_state.db.get_recent_predictions(limit=50)
    
    unresolved_predictions = [p for p in recent_predictions if p['actual_result'] is None]
    
    if not unresolved_predictions:
        st.info("✅ No hay predicciones pendientes de resolución. Todas las predicciones recientes ya tienen resultados registrados.")
    else:
        st.subheader(f"📋 Predicciones Pendientes ({len(unresolved_predictions)})")
        
        for pred in unresolved_predictions:
            with st.expander(f"🏢 {pred['firm_name']} - {pred['event_description'][:60]}...", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Probabilidad Predicha", f"{pred['probability']:.2%}")
                with col2:
                    st.metric("Fecha", pred['prediction_date'])
                with col3:
                    st.metric("ID", f"#{pred['id']}")
                
                st.markdown("**Evento:**")
                st.write(pred['event_description'])
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                profit_loss = 0.0
                
                with col1:
                    actual_result = st.radio(
                        "¿Cuál fue el resultado real?",
                        options=[None, 1, 0],
                        format_func=lambda x: "Seleccionar..." if x is None else "TRUE (Evento ocurrió)" if x == 1 else "FALSE (Evento no ocurrió)",
                        key=f"result_{pred['id']}"
                    )
                
                with col2:
                    if actual_result is not None:
                        profit_loss = st.number_input(
                            "Ganancia/Pérdida (USD)",
                            value=0.0,
                            step=0.01,
                            key=f"pl_{pred['id']}",
                            help="Ingrese la ganancia (positivo) o pérdida (negativo) en USD"
                        )
                
                with col3:
                    if actual_result is not None:
                        if st.button("💾 Guardar Resultado", key=f"save_{pred['id']}", type="primary"):
                            st.session_state.db.update_prediction_result(
                                pred['id'],
                                actual_result,
                                profit_loss
                            )
                            st.success("✅ Resultado guardado exitosamente!")
                            st.rerun()
    
    st.markdown("---")
    st.subheader("📊 Historial Completo de Predicciones")
    
    all_predictions = st.session_state.db.get_recent_predictions(limit=100)
    
    if all_predictions:
        df = pd.DataFrame(all_predictions)
        
        df['resultado'] = df['actual_result'].apply(
            lambda x: 'Pendiente' if x is None else ('TRUE' if x == 1 else 'FALSE')
        )
        
        df['correcto'] = df.apply(
            lambda row: 'N/A' if row['actual_result'] is None else 
            ('✅' if (row['probability'] >= 0.5 and row['actual_result'] == 1) or 
                    (row['probability'] < 0.5 and row['actual_result'] == 0) else '❌'),
            axis=1
        )
        
        display_df = df[['id', 'firm_name', 'event_description', 'probability', 
                         'prediction_date', 'resultado', 'profit_loss', 'correcto']]
        
        display_df.columns = ['ID', 'Firma', 'Evento', 'Probabilidad', 'Fecha', 
                              'Resultado Real', 'P/L (USD)', 'Correcto']
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        col1, col2, col3 = st.columns(3)
        
        resolved = df[df['actual_result'].notna()]
        if len(resolved) > 0:
            with col1:
                st.metric("Predicciones Resueltas", len(resolved))
            with col2:
                total_pl = resolved['profit_loss'].sum()
                st.metric("P/L Total", f"${total_pl:,.2f}")
            with col3:
                accuracy = (resolved['correcto'] == '✅').sum() / len(resolved) * 100
                st.metric("Precisión General", f"{accuracy:.1f}%")
    else:
        st.info("No hay predicciones registradas aún.")

with tab7:
    st.markdown("## 🤖 Competencia Autónoma de Trading")
    st.markdown("##### Sistema de apuestas automáticas con adaptación continua y aprendizaje semanal")
    
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
            st.markdown("### 🎮 Panel de Control")
            
            simulation_mode = st.toggle(
                "🧪 Modo Simulación",
                value=engine.simulation_mode,
                key="sim_mode_toggle",
                help="En modo simulación no se ejecutan apuestas reales"
            )
            engine.simulation_mode = simulation_mode
            
            if simulation_mode:
                st.success("✓ Modo simulación activo - Entorno seguro")
            else:
                st.error("⚠️ MODO REAL - Las apuestas afectarán tu cuenta")
            
            st.markdown("")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("▶️ Ejecutar Ciclo", use_container_width=True, type="primary"):
                    with st.spinner("Analizando eventos y ejecutando apuestas..."):
                        try:
                            result = engine.run_daily_cycle()
                            st.success(f"✅ {result.get('total_bets_placed')} apuestas colocadas")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col_btn2:
                if st.button("🔄 Actualizar", use_container_width=True):
                    st.rerun()
        
        st.markdown("")
        
        with st.container():
            st.markdown("### 📊 Resumen Global")
            
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
                    "Capital Total",
                    f"${total_bankroll:.2f}",
                    delta=f"${total_profit:+.2f}"
                )
            
            with metric_col2:
                st.metric(
                    "Retorno Global",
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
                st.metric("Total Apuestas", total_bets_placed)
            
            with metric_col4:
                st.metric("Win Rate Global", f"{global_win_rate:.1f}%")
    
    with right_col:
        with st.container():
            st.markdown("### 🏆 Leaderboard de IAs")
            
            leaderboard = status.get('leaderboard', [])
            
            if leaderboard:
                for i, entry in enumerate(leaderboard[:5]):
                    position_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry['position'], f"#{entry['position']}")
                    
                    with st.container():
                        col_pos, col_firm, col_metrics = st.columns([0.5, 1.5, 2])
                        
                        with col_pos:
                            st.markdown(f"## {position_emoji}")
                        
                        with col_firm:
                            st.markdown(f"**{entry['firm_name']}**")
                            risk_emoji = {"normal": "🟢", "caution": "🟡", "alert": "🟠", "critical": "🔴"}.get(entry['risk_level'], "⚪")
                            st.caption(f"{risk_emoji} {entry['risk_level'].upper()}")
                        
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
                st.info("Ejecuta un ciclo para ver el leaderboard")
    
    st.divider()
    
    with st.container():
        st.markdown("### 📈 Estado Detallado de las IAs")
        
        for firm_name, firm_status in status.get('firms', {}).items():
            with st.expander(f"🏢 {firm_name}", expanded=False):
                risk_status = firm_status['risk']
                bankroll_status = firm_status['bankroll']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    risk_level = risk_status.get('risk_level', 'normal')
                    risk_emoji = {"normal": "🟢", "caution": "🟡", "alert": "🟠", "critical": "🔴"}.get(risk_level, "⚪")
                    st.metric("Estado", f"{risk_emoji} {risk_level.upper()}")
                
                with col2:
                    adaptation_level = risk_status.get('adaptation_level', 0)
                    st.metric("Adaptación", f"Nivel {adaptation_level}")
                
                with col3:
                    bankroll = bankroll_status.get('current_bankroll', 0)
                    initial = bankroll_status.get('initial_bankroll', 1000)
                    delta = bankroll - initial
                    st.metric("Bankroll", f"${bankroll:.2f}", delta=f"{delta:+.2f}")
                
                with col4:
                    win_rate = bankroll_status.get('win_rate', 0)
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                st.markdown("**Parámetros de Riesgo:**")
                current_params = risk_status.get('current_limits', {})
                
                p1, p2, p3 = st.columns(3)
                with p1:
                    st.caption(f"Max Bet: {current_params.get('max_bet_size_pct', 0)*100:.1f}%")
                with p2:
                    st.caption(f"Max Concurrent: {current_params.get('max_concurrent_bets', 0)}")
                with p3:
                    st.caption(f"Pérdidas consecutivas: {risk_status.get('consecutive_losses', 0)}")
    
    st.divider()
    
    with st.container():
        st.markdown("### 📜 Historial de Apuestas")
    
        filter_firm = st.selectbox("Filtrar por Firma", ["Todas"] + list(status.get('firms', {}).keys()))
        
        if filter_firm == "Todas":
            bets = st.session_state.db.get_autonomous_bets(limit=50)
        else:
            bets = st.session_state.db.get_autonomous_bets(firm_name=filter_firm, limit=50)
        
        if bets:
            bets_data = []
            for bet in bets:
                result_emoji = "✅" if bet['actual_result'] == 1 else "❌" if bet['actual_result'] == 0 else "⏳"
                
                bets_data.append({
                    'Firma': bet['firm_name'],
                    'Evento': bet['event_description'][:50] + "..." if len(bet['event_description']) > 50 else bet['event_description'],
                    'Monto': f"${bet['bet_size']:.2f}",
                    'Prob': f"{bet['probability']:.0%}",
                    'EV': f"{bet['expected_value']:.2f}" if bet['expected_value'] else "N/A",
                    'Estado': result_emoji,
                    'P/L': f"${bet['profit_loss']:.2f}" if bet['profit_loss'] else "-",
                    'Fecha': bet['execution_timestamp'][:10]
                })
            
            df_bets = pd.DataFrame(bets_data)
            st.dataframe(df_bets, use_container_width=True, hide_index=True, height=300)
        else:
            st.info("No hay apuestas registradas. Ejecuta un ciclo para comenzar.")
    
    st.divider()
    
    with st.container():
        st.markdown("### 🔄 Adaptaciones de Estrategia")
        
        adaptations = st.session_state.db.get_strategy_adaptations()
        
        if adaptations:
            for adapt in adaptations[:5]:
                with st.expander(f"🔧 {adapt['firm_name']} - Nivel {adapt['adaptation_level']} ({adapt['adaptation_timestamp'][:10]})", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Bankroll", f"${adapt.get('bankroll_at_adaptation', 0):.2f}")
                    with col2:
                        st.metric("Pérdida", f"{adapt.get('loss_percentage', 0):.1f}%")
                    with col3:
                        st.metric("Nivel", adapt['adaptation_level'])
                    
                    st.markdown(f"**Razón:** {adapt['trigger_reason']}")
                    
                    if adapt.get('changes_applied'):
                        st.markdown("**Cambios:**")
                        for change in adapt.get('changes_applied', []):
                            st.caption(f"• {change}")
        else:
            st.info("No hay adaptaciones registradas aún.")
    
    st.divider()
    
    with st.container():
        st.markdown("### 📊 Gráficas de Performance")
        
        tab_chart1, tab_chart2, tab_chart3 = st.tabs(["💰 Bankroll", "🎯 Win Rate", "⚠️ Riesgo"])
        
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
                title="Evolución del Bankroll",
                xaxis_title="Tiempo",
                yaxis_title="Bankroll ($)",
                hovermode='x unified',
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_chart2:
            win_rates_data = []
            
            for firm_name, firm_status in status.get('firms', {}).items():
                bankroll_status = firm_status['bankroll']
                win_rates_data.append({
                    'Firma': firm_name,
                    'Win Rate': bankroll_status.get('win_rate', 0)
                })
            
            df_wr = pd.DataFrame(win_rates_data)
            
            fig = px.bar(df_wr, x='Firma', y='Win Rate', 
                         title="Tasa de Éxito",
                         color='Win Rate',
                         color_continuous_scale='RdYlGn',
                         height=350)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_chart3:
            risk_data = []
            
            for firm_name, firm_status in status.get('firms', {}).items():
                risk_status = firm_status['risk']
                risk_level = risk_status.get('risk_level', 'normal')
                
                risk_score = {'normal': 1, 'caution': 2, 'alert': 3, 'critical': 4}.get(risk_level, 1)
                
                risk_data.append({
                    'Firma': firm_name,
                    'Nivel': risk_level.upper(),
                    'Score': risk_score
                })
            
            df_risk = pd.DataFrame(risk_data)
            
            fig = px.bar(df_risk, x='Firma', y='Score', 
                         title="Niveles de Riesgo",
                         color='Nivel',
                         height=350,
                         color_discrete_map={
                         'NORMAL': 'green',
                         'CAUTION': 'yellow',
                         'ALERT': 'orange',
                         'CRITICAL': 'red'
                     })
        
        st.plotly_chart(fig, use_container_width=True)

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
