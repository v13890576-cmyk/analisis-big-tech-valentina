import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. ESTILO VISUAL "DARK ACADEMIC"
# ==========================================
st.set_page_config(page_title="Valentina - Big Tech Analytics", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro&family=Inter:wght@400;600&display=swap');
    
    /* Fondo general oscuro */
    .stApp { background-color: #0e1117; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Título Dorado Académico */
    .titulo-v {
        font-family: 'Playfair Display', serif;
        color: #d4af37;
        font-size: 38px;
        text-align: center;
        border-bottom: 2px solid #333;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    
    /* Estilo para las métricas (Dorado) */
    [data-testid="stMetricValue"] { 
        color: #d4af37 !important; 
        font-family: 'Source Code Pro', monospace; 
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    
    /* Fondo oscuro para las pestañas y gráficas */
    .stTabs [data-baseweb="tab-list"] { background-color: #1c1f26; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #ffffff; padding-left: 15px; padding-right: 15px; }
    .stTabs [data-baseweb="tab"]:hover { color: #d4af37; }
    
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CARGA DE DATOS REFORZADA (ANTI-ERROR 0)
# ==========================================
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

# Diccionario de colores para el gráfico comparativo
colores_comp = {
    'AAPL': '#f8f9fa', # Plata
    'MSFT': '#00a4ef', # Azul Microsoft
    'NVDA': '#76b900', # Verde Nvidia
    'META': '#0081fb', # Azul Meta
    'AMZN': '#ff9900'  # Naranja Amazon
}

@st.cache_data(ttl=600)
def load_data_veridico():
    with st.spinner('Cargando datos históricos verídicos...'):
        end = datetime.now()
        start = end - timedelta(days=10*365)
        # Descarga con threads=False para evitar bloqueos
        df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
        
        if df.empty:
            return pd.DataFrame()
            
        # Limpieza de la columna principal
        if 'Adj Close' in df.columns:
            df = df['Adj Close']
        elif 'Close' in df.columns:
            df = df['Close']
        
        # Aplanar columnas si vienen duplicadas
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
            
        return df

# ==========================================
# 3. INTERFAZ DE USUARIO (UI)
# ==========================================
try:
    st.markdown('<p class="titulo-v">ESTRATEGIA Y ESTADÍSTICA: BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Análisis de Datos Gerencial | Universidad Externado de Colombia")
    st.markdown("---")

    data = load_data_veridico()
    
    if data.empty:
        st.error("⚠️ Yahoo Finance está saturado. Por favor, refresca la página.")
        st.stop()

    # Selector lateral con íconos (si la versión de Streamlit lo permite)
    empresa = st.sidebar.selectbox("Seleccione el Activo:", tickers)
    
    # Cálculo de Retornos
    rets = data[empresa].pct_change().dropna()

    # --- NUEVA SECCIÓN: MEDIA, MODA, MEDIANA ---
    st.markdown(f"### 📋 Parámetros de Tendencia Central: {empresa}")
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        # Cálculos Estadísticos Verídicos
        media_val = rets.mean()
        mediana_val = rets.median()
        # Redondeamos para que la moda tenga sentido financiero
        moda_val = rets.round(4).mode().iloc[0] 

        col1.metric("MEDIA (Retorno Promedio)", f"{media_val:.6f}")
        col2.metric("MEDIANA", f"{mediana_val:.6f}")
        col3.metric("MODA (Frecuente)", f"{moda_val:.6f}")
    
    st.markdown("---")

    # ==========================================
    # 4. PESTAÑAS (TABS) - EXACTO A LA IMAGEN
    # ==========================================
    # Se añade íconos estándar (si Streamlit los soporta)
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tabla de Frecuencias", "📉 Trayectoria (10A)", "📊 Distribución y Riesgo", "🧬 KPIs y Volumen"])

    # --- TAB 1: TABLA DE FRECUENCIAS ---
    with tab1:
        st.subheader(f"Distribución de Retornos Diarios: {empresa} (10 Años)")
        
        # Crear bins detallados para la tabla de frecuencia
        bins = [-1, -0.05, -0.02, -0.005, 0.005, 0.02, 0.05, 1]
        labels = ['Caída Fuerte (<-5%)', 'Caída Moderada (-5% a -2%)', 'Leve Neg. (-2% a -0.5%)', 'Rango Neutro (-0.5% a 0.5%)', 'Leve Pos. (0.5% a 2%)', 'Subida Moderada (2% a 5%)', 'Subida Fuerte (>5%)']
        
        # Categorizar los retornos y calcular frecuencias
        frec = pd.cut(rets, bins=bins, labels=labels).value_counts().sort_index()
        df_frec = pd.DataFrame({'Rango de Retorno': frec.index, 'Frecuencia (Días)': frec.values})
        
        # Cálculos de frecuencia relativa y acumulada
        total_dias = len(rets)
        df_frec['Frecuencia Relativa (%)'] = (df_frec['Frecuencia (Días)'] / total_dias * 100).round(2)
        df_frec['Frecuencia Acumulada (%)'] = df_frec['Frecuencia Relativa (%)'].cumsum().round(2)
        
        # Estilar la tabla
        st.dataframe(df_frec.style.background_gradient(cmap='Brwnyl', subset=['Frecuencia (Días)']), use_container_width=True)

    # --- TAB 2: TRAYECTORIA ---
    with tab2:
        st.subheader(f"Histórico de Valorización: {empresa}")
        fig_line = px.line(data, y=empresa, color_discrete_sequence=['#d4af37'])
        # Fondo oscuro en la gráfica
        fig_line.update_layout(
            plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', 
            xaxis=dict(grid
