import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN GENERAL Y ESTILO "DARK DASHBOARD"
st.set_page_config(page_title="Dashboard Valentina", layout="wide")

st.markdown("""
    <style>
    /* Estilo para las tarjetas de KPI */
    .stApp { background-color: #0e1117; color: white; }
    .kpi-container { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 25px; }
    .kpi-card {
        background-color: #1a1c24;
        padding: 20px 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        flex: 1;
        min-width: 150px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .kpi-card div:first-child { color: #8b949e; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-card div:nth-child(2) { color: #8b949e; font-size: 13px; margin-bottom: 5px; }
    .kpi-card div:nth-child(3) { 
        color: white; 
        font-size: 26px; /* Precio completo en una sola línea */
        font-weight: bold; 
        margin: 5px 0; 
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-val { font-size: 14px; border-radius: 5px; padding: 2px 8px; font-weight: bold;}
    .delta-up { background-color: rgba(0,255,100,0.1); color: #00ff64; }
    .delta-down { background-color: rgba(255,50,50,0.1); color: #ff3232; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (10 AÑOS - DATOS VERÍDICOS)
@st.cache_data(ttl=600)
def load_data():
    t = ['AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 'NVDA', 'TSLA']
    try:
        # Descarga de datos
        df = yf.download(t, period="10y", progress=False)
        return df['Close'] if 'Close' in df.columns else df['Adj Close']
    except Exception as e:
        return pd.DataFrame() # Retorna DF vacío en caso de error

data = load_data()

# Lógica principal solo si hay datos
if not data.empty:
    st.markdown('<p style="color:white; font-size:32px; font-weight:bold; margin-bottom:20px;">Precios Actuales y Rendimiento</p>', unsafe_allow_html=True)

    # Obtenemos los últimos datos y los de hace un año (simulación YTD)
    try:
        current_data = data.iloc[-1]
        last_year_data = data.iloc[-252] # Datos de aprox.
