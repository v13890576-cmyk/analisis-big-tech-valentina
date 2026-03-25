import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. ESTILO "DARK ACADEMIC" (EXCLUSIVO VALENTINA)
st.set_page_config(page_title="Análisis Estadístico - Valentina", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Roboto+Mono&display=swap');
    
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Títulos en Dorado Académico */
    .titulo-v {
        font-family: 'Playfair Display', serif;
        color: #d4af37;
        font-size: 35px;
        text-align: center;
        border-bottom: 2px solid #d4af37;
        padding-bottom: 10px;
    }
    
    /* Tarjetas de métricas */
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-family: 'Roboto Mono', monospace; }
    
    /* Estilo para las tablas */
    .styled-table { background-color: #1c1f26; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS REALES
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=3600)
def load_data():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    df = yf.download(tickers, start=start, end=end, progress=False)
    if 'Adj Close' in df.columns:
        df = df['Adj Close']
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
    return df

try:
    st.markdown('<p class="titulo-v">ESTRATEGIA Y ESTADÍSTICA: BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Análisis de Datos para Administración | Universidad Externado")

    data = load_data()
    
    if not data.empty:
        empresa = st.sidebar.selectbox("Seleccione Activo:", tickers)
        rets = data[empresa].pct_change().dropna()

        # --- SECCIÓN DE ESTADÍSTICA DESCRIPTIVA ---
        st.header(f"📊 Análisis Estadístico de {empresa}")
        
        # Cálculos de Media, Mediana y Moda
        media = rets.mean()
        mediana = rets.median()
        # La moda en finanzas se calcula redondeando para encontrar valores frecuentes
        moda = rets.round(4).mode()[0] 
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Media (Promedio Diario)", f"{media:.4%}")
        col_m2.metric("Mediana", f"{mediana:.4%}")
        col_m3.metric("Moda (Valor Frecuente)", f"{moda:.4%}")

        t1, t2 = st.tabs(["📉 Tendencia Histórica", "🧬 Distribución y Riesgo"])

        with t1:
            # Gráfico de Línea Clásico
            fig_linea = px.line(data, y=empresa, color_discrete_sequence=['#d4af37'])
            fig_linea.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                    font_color="white", xaxis_title="Año", yaxis_title="Precio USD")
            st.plotly_chart(fig_linea, use_container_width=True)

        with t2:
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Histograma de Retornos")
                # El histograma muestra la frecuencia de los datos
                fig_hist = px.histogram(rets, color_discrete_sequence=['#d4af37'], nbins=100)
                fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_hist, use_container_width=True)
                st.write("Muestra qué tan seguido la acción gana o pierde cierto porcentaje.")

            with c2:
                st.subheader("Boxplot (Diagrama de Caja)")
                # El boxplot es muy usado en estadística para ver valores atípicos
                fig_box = px.box(rets, color_discrete_sequence=['#ffffff'])
                fig_box.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_box, use_container_width=True)
                st.write("Identifica la dispersión y los días de ganancias/pérdidas extremas.")

        # --- TABLA DE DATOS CRUDA ---
        st.markdown("---")
        with st.expander("Ver Tabla de Datos Históricos"):
            st.dataframe(data[empresa].tail(10).style.highlight_max(axis=0, color='#d4af37'))

except Exception as e:
    st.error(f"Error en la conexión con Yahoo Finance: {e}")
