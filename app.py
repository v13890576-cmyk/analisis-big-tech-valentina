import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN VISUAL (FONDO NEGRO Y DORADO)
st.set_page_config(page_title="Big Tech Analytics - Valentina", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .titulo { color: #d4af37; font-family: 'Serif'; font-size: 40px; text-align: center; font-weight: bold; }
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 1.8rem !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1c1f26; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS REALES
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=600)
def get_data():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    # Descarga limpia
    df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
    if 'Adj Close' in df.columns:
        df = df['Adj Close']
    elif 'Close' in df.columns:
        df = df['Close']
    return df

try:
    st.markdown('<p class="titulo">ESTRATEGIA Y ESTADÍSTICA: BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Reporte Gerencial | Universidad Externado de Colombia")
    
    data = get_data()
    
    if data.empty:
        st.warning("No se pudieron cargar los datos. Por favor, refresca la página.")
        st.stop()

    # Barra lateral
    empresa = st.sidebar.selectbox("Seleccione Empresa:", tickers)
    rets = data[empresa].pct_change().dropna()

    # --- SECCIÓN ESTADÍSTICA ---
    st.markdown("### 📋 Parámetros de Tendencia Central")
    col1, col2, col3 = st.columns(3)
    
    media = rets.mean()
    mediana = rets.median()
    # Moda redondeada para encontrar valores comunes
    moda = rets.round(4).mode()[0]

    col1.metric("MEDIA (Promedio)", f"{media:.5%}")
    col2.metric("MEDIANA", f"{mediana:.5%}")
    col3.metric("MODA", f"{moda:.5%}")

    st.markdown("---")

    # --- PESTAÑAS ---
    t1, t2, t3, t4 = st.tabs(["📊 Tabla de Frecuencias", "📈 Trayectoria (10A)", "🧬 Distribución", "🎯 Comparativo"])

    with t1:
        st.subheader("Distribución de Frecuencia de Retornos")
        # Definición de rangos lógicos
        bins = [-1, -0.05, -0.02, 0, 0.02, 0.05, 1]
        labels = ['Pérdida Crítica', 'Pérdida Fuerte', 'Leve Negativo', 'Leve Positivo', 'Subida Fuerte', 'Subida Crítica']
        
        frecuencias = pd.cut(rets, bins=bins, labels=labels).value_counts().reset_index()
        frecuencias.columns = ['Categoría de Retorno', 'Días (Frecuencia)']
        
        # Tabla estilizada
        st.table(frecuencias)

    with t2:
        st.subheader(f"Evolución Histórica: {empresa}")
        fig_line = px.line(data, y=empresa, color_discrete_sequence=['#d4af37'])
        fig_line.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color="white")
        fig_line.update_xaxes(gridcolor='#333')
        fig_line.update_yaxes(gridcolor='#333')
        st.plotly_chart(fig_line, use_container_width=True)

    with t3:
        st.subheader("Análisis de Distribución y Riesgo")
        c1, c2 = st.columns(2)
        with c1:
            fig_hist = px.histogram(rets, nbins=100, color_discrete_sequence=['#d4af37'], title="Histograma")
            st.plotly_chart(fig_hist, use_container_width=True)
        with c2:
            fig_box = px.box(rets, orientation='h', color_discrete_sequence=['#ffffff'], title="Diagrama de Caja (Outliers)")
            st.plotly_chart(fig_box, use_container_width=True)

    with t4:
        st.subheader("Crecimiento Acumulado Comparativo")
        # Rendimiento total: (Precio Final / Precio Inicial) - 1
        rend_total = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
        fig_bar = px.bar(rend_total, color=rend_total.index, 
                         color_discrete_map={'AAPL':'#f8f9fa', 'MSFT':'#00a4ef', 'NVDA':'#76b900', 'META':'#0081fb', 'AMZN':'#ff9900'})
        fig_bar.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"Error técnico detectado: {e}")
