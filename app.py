import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="Valentina - Análisis Crítico", layout="wide")
st.markdown("<style>.stApp { background-color: #050505; color: white; }</style>", unsafe_allow_html=True)

# 2. CARGA DE DATOS SEGURO
@st.cache_data(ttl=600)
def load_data():
    try:
        tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
        df = yf.download(tickers, start=datetime.now()-timedelta(days=3650), progress=False)
        return df['Close'] if 'Close' in df.columns else df['Adj Close']
    except:
        return None

# 3. CUERPO DE LA APLICACIÓN
data = load_data()

if data is None or data.empty:
    st.error("Error de conexión con Yahoo Finance. Revisa tu archivo requirements.txt")
else:
    st.title("⚖️ CRÍTICA ESTRATÉGICA: BIG TECH")
    st.caption("Valentina | Universidad Externado de Colombia")
    
    empresa = st.sidebar.selectbox("Seleccione Acción:", data.columns)
    monto = st.sidebar.number_input("Capital a invertir (USD):", value=1000)
    
    # ESTADÍSTICAS (Media, Mediana, Moda)
    rets = data[empresa].pct_change().dropna()
    
    st.subheader(f"📊 Estadísticas de Retorno: {empresa}")
    col1, col2, col3 = st.columns(3)
    col1.metric("MEDIA (Promedio)", f"{rets.mean():.4%}")
    col2.metric("MEDIANA", f"{rets.median():.4%}")
    col3.metric("MODA", f"{rets.round(4).mode()[0]:.4%}")

    # JUICIO CRÍTICO DE INVERSIÓN
    st.markdown("---")
    volatilidad = rets.std() * (252**0.5)
    retorno_anual = rets.mean() * 252
    eficiencia = retorno_anual / volatilidad

    st.subheader("🎯 Mi Recomendación Crítica")
    if eficiencia > 0.7:
        st.success(f"**¡ES BUENA OPCIÓN!** {empresa} tiene un historial sólido. Con tus ${monto:,.0f}, la probabilidad de éxito es alta debido a su eficiencia histórica.")
    elif eficiencia > 0.4:
        st.warning(f"**OPCIÓN MODERADA.** Es aceptable, pero la volatilidad es alta. Solo invierte tus ${monto:,.0f} si no los necesitas a corto plazo.")
    else:
        st.error(f"**¡NO RECOMENDADO!** El riesgo de {empresa} supera al beneficio. Podrías perder gran parte de tu capital rápidamente.")

    # GRÁFICAS (Boxplot mejorado)
    t1, t2 = st.tabs(["🧬 Riesgo (Boxplot)", "📈 Evolución"])
    
    with t1:
        # Boxplot con puntos individuales (Outliers)
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=rets, name=empresa, marker_color='#d4af37', boxpoints='outliers'))
        fig_box.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white", title="Dispersión y Días de Crisis (Outliers)")
        st.plotly_chart(fig_box, use_container_width=True)
        st.info("Los puntos fuera de la caja son los 'días de pánico' o ganancias extremas.")

    with t2:
        fig_line = px.line(data[empresa], title=f"Precio Histórico: {empresa}", color_discrete_sequence=['#d4af37'])
        fig_line.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white")
        st.plotly_chart(fig_line, use_container_width=True)
