import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ==========================================
# 1. ESTILO "CYBERPUNK GERENCIAL"
# ==========================================
st.set_page_config(page_title="Big Tech Analytics - Valentina", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Inter:wght@400;600&display=swap');
    
    /* Fondo Negro y Tipografía Clara */
    .stApp { background-color: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Título Futurista */
    .titulo-v {
        font-family: 'Orbitron', sans-serif;
        color: #ffffff;
        font-size: 38px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid #333;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 2rem !important; }
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    
    /* Tarjetas oscuras */
    .report-card {
        background-color: #111111;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333333;
    }
    
    /* Inputs */
    .stNumberInput>div>div>input { background-color: #1a1a1a; color: #fff; border: 1px solid #444; }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] { background-color: #111111; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATOS VERÍDICOS DE YAHOO FINANCE
# ==========================================
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

# Paleta de colores eléctricos por empresa
colores_comp = {
    'AAPL': '#f8f9fa', # Plata
    'MSFT': '#00a4ef', # Azul Microsoft
    'NVDA': '#76b900', # Verde Nvidia
    'META': '#0081fb', # Azul Meta
    'AMZN': '#ff9900'  # Naranja Amazon
}

@st.cache_data(ttl=600)
def load_data_veridico():
    with st.spinner('Actualizando datos financieros reales...'):
        end = datetime.now()
        start = end - timedelta(days=10*365)
        # Descarga con threads=False para estabilidad
        df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
        
        if df.empty:
            return pd.DataFrame()
            
        # Limpieza de columna Adj Close
        if 'Adj Close' in df.columns:
            df = df['Adj Close']
        elif 'Close' in df.columns:
            df = df['Close']
        
        # Aplanar MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level
