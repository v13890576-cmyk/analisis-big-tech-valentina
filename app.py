import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Valentina - Decisión Tech", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .titulo { color: #d4af37; font-size: 35px; text-align: center; font-weight: bold; border-bottom: 2px solid #333; }
    .best-card { background-color: #111; padding: 20px; border-radius: 15px; border: 2px solid #d4af37; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (10 AÑOS)
@st.cache_data(ttl=600)
def get_all_data():
    tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
    df = yf.download(tickers, start=datetime.now()-timedelta(days=3650), progress=False)
    return df['Close'] if 'Close' in df.columns else df['Adj Close']

try:
    st.markdown('<p class="titulo">ANÁLISIS CRÍTICO Y RECOMENDACIÓN GERENCIAL</p>', unsafe_allow_html=True)
    st.caption("Valentina | Facultad de Administración | Universidad Externado de Colombia")

    data = get_all_data()
    
    if data is None:
        st.error("Error al conectar con los datos financieros.")
        st.stop()

    # --- LÓGICA DE LA MEJOR OPCIÓN ---
    all_rets = data.pct_change().dropna()
    eficiencias = (all_rets.mean() * 252) / (all_rets.std() * (252**0.5))
    mejor_ticker = eficiencias.idxmax()
    
    st.markdown("### 🏆 Dictamen: ¿Cuál es la mejor opción?")
    col_a, col_b = st.columns([1.5, 1])
    
    with col_a:
        fig_rank = px.bar(eficiencias, color=eficiencias.values, 
                          labels={'value': 'Ratio de Eficiencia', 'index': 'Empresa'},
                          title="Comparativo: Retorno por cada unidad de Riesgo",
                          color_continuous_scale='Gold')
        fig_rank.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white")
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_b:
        st.markdown(f"""
            <div class="best-card">
                <h2 style="color: #d4af37;">RECOMENDACIÓN FINAL</h2>
                <h1 style="font-size: 50px;">{mejor_ticker}</h1>
                <p>Basado en 10 años de datos, <b>{mejor_ticker}</b> ofrece el mejor equilibrio entre ganancias y estabilidad.</p>
                <p style
