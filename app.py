import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Big Tech Analytics - Valentina", layout="wide")

# Estilo Negro y Dorado (Elegante)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .titulo-v { color: #d4af37; font-family: 'Serif'; font-size: 35px; text-align: center; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 10px; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; }
    .report-card { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS CON "CACHÉ" (Para que no cargue cada vez que muevas algo)
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=3600) # Guarda los datos por 1 hora para que vuele
def load_data():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    # Descarga optimizada
    df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
    if not df.empty:
        if 'Adj Close' in df.columns: df = df['Adj Close']
        elif 'Close' in df.columns: df = df['Close']
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
    return df

try:
    st.markdown('<p class="titulo-v">ESTRATEGIA Y ESTADÍSTICA: BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Universidad Externado de Colombia")

    df_precios = load_data()

    if df_precios.empty:
        st.error("⌛ Yahoo Finance está tardando en responder. Refresca la página en 10 segundos.")
        st.stop()

    # --- SIDEBAR ---
    st.sidebar.header("Configuración")
    empresa = st.sidebar.selectbox("Seleccione Empresa:", tickers)
    capital = st.sidebar.number_input("Inversión Inicial (USD):", value=1000)
    
    rets = df_precios[empresa].pct_change().dropna()

    # --- MÓDULO DE RECOMENDACIÓN ---
    st.subheader("🎯 Recomendación de Inversión")
    col_rec1, col_rec2 = st.columns([1, 2])
    
    with col_rec1:
        rend_anual = rets.mean() * 252 * 100
        volatilidad = rets.std() * (252**0.5) * 100
        st.markdown(f"""
        <div class='report-card'>
        <h4>Perfil: {empresa}</h4>
        <p>Retorno Anual Esperado: <b>{rend_anual:.2f}%</b></p>
        <p>Riesgo (Volatilidad): <b>{volatilidad:.2f}%</b></p>
        </div>
        """, unsafe_allow_html=True)

    with col_rec2:
        if volatilidad > 40: rec = "Agresivo (Alta ganancia, alto riesgo)"
        elif volatilidad > 25: rec = "Equilibrado"
        else: rec = "Conservador"
        
        st.success(f"Para tus **${capital:,.2f}**, {empresa} se clasifica como perfil **{rec}**.")

    # --- ESTADÍSTICA ---
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("MEDIA (Diaria)", f"{rets.mean():.5%}")
    c2.metric("MEDIANA", f"{rets.median():.5%}")
    c3.metric("MODA", f"{rets.round(4).mode()[0]:.5%}")

    # --- GRÁFICAS MEJORADAS ---
    t1, t2 = st.tabs(["📊 Distribución (Histograma/Boxplot)", "📈 Trayectoria Histórica"])

    with t1:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_h = px.histogram(rets, nbins=50, title="Histograma de Retornos", color_discrete_sequence=['#d4af37'])
            fig_h.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
            st.plotly_chart(fig_h, use_container_width=True)
        with col_g2:
            fig_b = px.box(rets, orientation='h', title="Diagrama de Caja (Riesgo)", color_discrete_sequence=['#ffffff'])
            fig_b.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
