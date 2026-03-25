import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. ESTILO "DARK ACADEMIC" (VISIBILIDAD TOTAL)
st.set_page_config(page_title="Valentina - Big Tech Stats", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro&display=swap');
    
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    .titulo-v {
        font-family: 'Playfair Display', serif;
        color: #d4af37;
        font-size: 38px;
        text-align: center;
        border-bottom: 2px solid #333;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    
    /* Estilo para los KPI de Media, Moda y Mediana */
    [data-testid="stMetricValue"] { 
        color: #d4af37 !important; 
        font-family: 'Source Code Pro', monospace; 
        font-size: 1.8rem !important;
    }
    
    .stat-card {
        background-color: #1c1f26;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #d4af37;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DE DATOS REFORZADA (ANTI-ERROR 0)
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=600)
def load_data_safe():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    # Descarga directa sin hilos para evitar bloqueos
    df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
    
    if df.empty:
        return pd.DataFrame()
        
    # Limpieza profunda de las columnas de Yahoo
    if 'Adj Close' in df.columns:
        df = df['Adj Close']
    elif 'Close' in df.columns:
        df = df['Close']
    
    # Aplanar columnas si vienen duplicadas
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
        
    return df

# 3. INTERFAZ DE USUARIO
try:
    st.markdown('<p class="titulo-v">ESTRATEGIA Y ESTADÍSTICA: BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Análisis de Datos Gerencial | Universidad Externado")

    data = load_data_safe()
    
    if data.empty:
        st.error("⚠️ Yahoo Finance está saturado. Por favor, espera 10 segundos y refresca la página.")
        st.stop()

    # Selector lateral
    empresa = st.sidebar.selectbox("Seleccione el Activo para el Análisis:", tickers)
    
    # Cálculo de Retornos
    rets = data[empresa].pct_change().dropna()

    # --- NUEVA SECCIÓN: MEDIA, MODA, MEDIANA ---
    st.markdown("### 📋 Parámetros de Tendencia Central")
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        # Cálculos Estadísticos
        media_val = rets.mean()
        mediana_val = rets.median()
        # Redondeamos a 4 decimales para que la moda tenga sentido financiero
        moda_val = rets.round(4).mode().iloc[0] 

        col1.metric("MEDIA (Retorno Promedio)", f"{media_val:.4%}")
        col2.metric("MEDIANA (Punto Central)", f"{mediana_val:.4%}")
        col3.metric("MODA (Valor más repetido)", f"{moda_val:.4%}")
    
    st.markdown("---")

    # --- PESTAÑAS DE GRÁFICAS ---
    t1, t2, t3 = st.tabs(["📉 Evolución de Precios", "📊 Distribución de Riesgo", "🧬 Análisis Técnico"])

    with t1:
        st.subheader(f"Histórico de Valorización: {empresa} (10 años)")
        fig_line = px.line(data, y=empresa, color_discrete_sequence=['#d4af37'])
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_line, use_container_width=True)

    with t2:
        c_a, c_b = st.columns(2)
        with c_a:
            st.subheader("Histograma (Frecuencias)")
            fig_hist = px.histogram(rets, nbins=80, color_discrete_sequence=['#d4af37'])
            fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_hist, use_container_width=True)
        with c_b:
            st.subheader("Boxplot (Dispersión)")
            fig_box = px.box(rets, orientation='h', color_discrete_sequence=['#ffffff'])
            fig_box.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,
