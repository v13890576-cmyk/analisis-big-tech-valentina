import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. ESTILO "GERENCIAL PREMIUM"
st.set_page_config(page_title="Valentina - Big Tech Strategy", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .titulo { color: #d4af37; font-family: 'serif'; font-size: 40px; text-align: center; font-weight: bold; border-bottom: 2px solid #d4af37; padding-bottom: 10px; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    .best-card { background-color: #111; padding: 30px; border-radius: 20px; border: 2px solid #d4af37; text-align: center; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (10 AÑOS)
@st.cache_data(ttl=600)
def get_data():
    try:
        tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
        df = yf.download(tickers, start=datetime.now()-timedelta(days=3650), progress=False)
        return df['Close'] if 'Close' in df.columns else df['Adj Close']
    except:
        return None

try:
    st.markdown('<p class="titulo">ESTRATEGIA FINANCIERA Y ANÁLISIS DE MERCADOS</p>', unsafe_allow_html=True)
    st.caption("Valentina | Facultad de Administración de Empresas | Universidad Externado de Colombia")

    data = get_data()
    if data is None or data.empty:
        st.error("Error de sincronización con los mercados financieros.")
        st.stop()

    # --- CUADRO DE ESTADO ACTUAL DE LAS ACCIONES ---
    st.header("🏢 Monitor de Activos (Big Tech)")
    
    # Creamos un resumen del estado actual
    resumen_mercado = []
    for t in data.columns:
        precio_actual = data[t].iloc[-1]
        precio_ayer = data[t].iloc[-2]
        cambio = precio_actual - precio_ayer
        pct_cambio = (cambio / precio_ayer) * 100
        resumen_mercado.append({
            "Empresa": t,
            "Precio Actual (USD)": precio_actual,
            "Variación ($)": cambio,
            "Variación (%)": pct_camb
