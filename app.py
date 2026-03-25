import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. ESTILO "DARK ACADEMIC" DE ALTO NIVEL
st.set_page_config(page_title="Valentina - Critical Investment Analysis", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .titulo-v { color: #d4af37; font-family: 'Playfair Display', serif; font-size: 38px; text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 15px; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #d4af37 !important; }
    .critica-card { padding: 25px; border-radius: 15px; border: 2px solid; margin: 20px 0; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (YAHOO FINANCE VERÍDICO)
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=600)
def load_data_critical():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
    if not df.empty:
        if 'Adj Close' in df.columns: df = df['Adj Close']
        elif 'Close' in df.columns: df = df['Close']
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
    return df

try:
    st.markdown('<p class="titulo-v">CRÍTICA ESTRATÉGICA DE INVERSIÓN</p>', unsafe_allow_html=True)
    st.caption("Valentina | Análisis Crítico de Mercados | Universidad Externado")

    data = load_data_critical()
    if data.empty:
        st.error("Error de conexión. Refresca la página.")
        st.stop()

    # SIDEBAR
    empresa = st.sidebar.selectbox("Seleccione Activo:", tickers)
    monto = st.sidebar.number_input("Capital a Invertir (USD):", min_value=100, value=1000)
    
    # Cálculos Estadísticos Base
    rets = data[empresa].pct_change().dropna()
    media = rets.mean()
    mediana = rets.median()
    moda = rets.round(4).mode()[0]
    
    # Métricas Críticas (Anualizadas)
    rend_anual = media * 252
    volatilidad = rets.std() * (252**0.5)
    eficiencia = rend_anual / volatilidad  # Ratio de Sharpe simplificado

    # --- SECCIÓN: TENDENCIA CENTRAL ---
    st.subheader("📋 Parámetros de Tendencia Central")
    c1, c2, c3 = st.columns(3)
    c1.metric("MEDIA (Retorno Diario)", f"{media:.4%}")
    c2.metric("MEDIANA (Punto de Equilibrio)", f"{mediana:.4%}")
    c3.metric("MODA (Lo más frecuente)", f"{moda:.4%}")

    st.markdown("---")

    # --- SECCIÓN: EL DICTAMEN CRÍTICO ---
    st.header(f"⚖️ ¿Es bueno invertir en {empresa}?")
    
    if eficiencia > 0.8:
        color, juicio, icono = "#00ff88", "INVERSIÓN ALTAMENTE RECOMENDADA", "🚀"
        razon = f"Este activo genera un excelente retorno por cada unidad de riesgo asumida. Su trayectoria de 10 años muestra que es una 'máquina de valor'."
    elif eficiencia > 0.5:
        color, juicio, icono = "#ffaa00", "INVERSIÓN DE RIESGO MODERADO", "⚖️"
        razon = "El rendimiento es bueno, pero la volatilidad es considerable. Solo invierte si no necesitas este dinero en los próximos 2 años."
    else:
        color, juicio, icono = "#ff4b4b", "INVERSIÓN NO RECOMENDADA / ALTO RIESGO", "⚠️"
        razon = "La volatilidad actual supera con creces el beneficio esperado. El comportamiento histórico sugiere que podrías enfrentar pérdidas graves antes de ver ganancias."

    st.markdown(f"""
        <div class="critica-card" style="border-color: {color}; background-color: {color}15;">
            <h2 style="color: {color}; margin-top: 0;">{icono} {juicio}</h2>
            <p><b>Análisis de Valentina:</b> {razon}</p>
            <p>Con tus <b>${monto:,.2f} USD</b>, el riesgo estimado de pérdida en un día de pánico es de <b>{(rets.std()*2):.2%}</b>.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- SECCIÓN: GRÁFICAS (BOXPLOT MEJORADO) ---
    t1, t2
