import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Análisis Crítico - Valentina", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .titulo-v { color: #d4af37; font-family: 'serif'; font-size: 35px; text-align: center; border-bottom: 2px solid #333; }
    .card { background-color: #111; padding: 20px; border-radius: 15px; border: 1px solid #444; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# CARGA DE DATOS SEGURO
@st.cache_data(ttl=600)
def fetch_data():
    try:
        end = datetime.now()
        start = end - timedelta(days=10*365)
        tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
        df = yf.download(tickers, start=start, end=end, progress=False)
        if df.empty: return None
        # Seleccionamos precios de cierre de forma segura
        df = df['Close'] if 'Close' in df.columns else df['Adj Close']
        return df
    except:
        return None

try:
    st.markdown('<p class="titulo-v">CRÍTICA ESTRATÉGICA Y DECISIÓN FINANCIERA</p>', unsafe_allow_html=True)
    st.caption("Valentina | Universidad Externado de Colombia")

    data = fetch_data()

    if data is None:
        st.error("⌛ Yahoo Finance no responde. Refresca la página en un minuto.")
    else:
        # SIDEBAR
        empresa = st.sidebar.selectbox("Seleccione Activo:", data.columns)
        monto = st.sidebar.number_input("Inversión (USD):", value=1000)
        
        # CÁLCULOS
        precios = data[empresa].dropna()
        rets = precios.pct_change().dropna()
        
        # TENDENCIA CENTRAL
        st.markdown("### 📊 Parámetros de Tendencia Central")
        c1, c2, c3 = st.columns(3)
        c1.metric("MEDIA (Retorno Diario)", f"{rets.mean():.4%}")
        c2.metric("MEDIANA", f"{rets.median():.4%}")
        c3.metric("MODA", f"{rets.round(4).mode()[0]:.4%}")

        # ANÁLISIS CRÍTICO DE VALENTINA
        st.markdown("---")
        rend_anual = rets.mean() * 252
        volatilidad = rets.std() * (252**0.5)
        eficiencia = rend_anual / volatilidad # Coeficiente de desempeño

        st.subheader(f"⚖️ Juicio Crítico sobre {empresa}")
        
        if eficiencia > 0.7:
            st.success(f"🚀 **DICTAMEN: EXCELENTE INVERSIÓN.** {empresa} tiene un historial de crecimiento muy superior a su riesgo. Con tus ${monto:,.2f}, estarías entrando en un activo de alta eficiencia.")
        elif eficiencia > 0.4:
            st.warning(f"⚖️ **DICTAMEN: RIESGO EQUILIBRADO.** Es una buena opción, pero prepárate para caídas fuertes. No metas dinero que necesites pronto.")
        else:
            st.error(f"⚠️ **DICTAMEN: ALTO RIESGO / EVITAR.** Actualmente la volatilidad es demasiado alta para el retorno que ofrece. Podrías perder gran parte de tus ${monto:,.2f} en un mal día.")

        # GRÁFICAS MEJORADAS
        tab1, tab2 = st.tabs(["🧬 Análisis de Riesgo (Boxplot)", "📈 Evolución Histórica"])

        with tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Boxplot Profesional (Detección de Crisis/Outliers)**")
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(y=rets, name=empresa, marker_color='#d4af37', boxpoints='outliers'))
                fig_box.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white", height=400)
                st.plotly_chart(fig_box, use_container_width=True)
            with col_b:
                st.write("**Distribución de Retornos (Histograma)**")
                fig_hist = px.histogram(rets, nbins=80, color_discrete_sequence=['#d4af37'])
                fig_hist.update_layout(plot_bgcolor='#050505', paper_bgcolor
