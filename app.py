import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Análisis Crítico - Valentina", layout="wide")
st.markdown("<style>.stApp { background-color: #050505; color: white; }</style>", unsafe_allow_html=True)

# 2. CARGA DE DATOS ESTABLE
@st.cache_data(ttl=600)
def get_data():
    tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
    # Descarga de los últimos 10 años
    df = yf.download(tickers, start=datetime.now()-timedelta(days=3650), progress=False)
    return df['Close'] if 'Close' in df.columns else df['Adj Close']

try:
    st.markdown("<h1 style='text-align: center; color: #d4af37;'>DICTAMEN ESTRATÉGICO DE INVERSIÓN</h1>", unsafe_allow_html=True)
    st.caption("Valentina | Universidad Externado de Colombia")

    data = get_data()
    if data is None or data.empty:
        st.error("Error de conexión. Intenta refrescar la página.")
        st.stop()

    # --- LÓGICA DE LA MEJOR OPCIÓN ---
    rets_all = data.pct_change().dropna()
    # Ratio de Eficiencia (Retorno / Riesgo)
    eficiencia = (rets_all.mean() * 252) / (rets_all.std() * (252**0.5))
    mejor_empresa = eficiencia.idxmax()

    st.markdown(f"### 🏆 La Mejor Opción Actual: {mejor_empresa}")
    st.info(f"Basado en el análisis de 10 años, **{mejor_empresa}** ofrece el mejor rendimiento por cada unidad de riesgo asumida.")

    # --- TABLA DE FRECUENCIAS ---
    empresa = st.sidebar.selectbox("Analizar detalle de:", data.columns)
    monto = st.sidebar.number_input("Monto a invertir (USD):", value=1000)
    rets = rets_all[empresa]

    st.markdown("---")
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("📋 Tabla de Frecuencias")
        bins = [-1, -0.02, -0.005, 0.005, 0.02, 1]
        labels = ['Baja Fuerte', 'Baja Leve', 'Estable', 'Subida Leve', 'Subida Fuerte']
        frec = pd.cut(rets, bins=bins, labels=labels).value_counts().reset_index()
        frec.columns = ['Rango', 'Días']
        frec['% Relativo'] = (frec['Días'] / frec['Días'].sum()) * 100
        st.table(frec.style.format({'% Relativo': '{:.2f}%'}))

    with col_der:
        st.subheader("📊 Gráfica de Retornos Diarios")
        fig_ret = px.line(rets, color_discrete_sequence=['#d4af37'])
        fig_ret.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white", xaxis_title="Tiempo", yaxis_title="Retorno %")
        st.plotly_chart(fig_ret, use_container_width=True)

    # --- BOXPLOT Y TENDENCIA ---
    t1, t2 = st.tabs(["🧬 Riesgo (Boxplot)", "📈 Tendencia Central"])
    
    with t1:
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=rets, name=empresa, marker_color='#d4af37', boxpoints='outliers'))
        fig_box.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white", title="Detección de Riesgos Extremos (Outliers)")
        st.plotly_chart(fig_box, use_container_width=True)

    with t2:
        c1, c2, c3 = st.columns(3)
        c1.metric("MEDIA", f"{rets.mean():.4%}")
        c2.metric("MEDIANA", f"{rets.median():.4%}")
        c3.metric("MODA", f"{rets.round(4).mode()[0]:.4%}")
        st.write(f"Con **${monto:,.0f}**, el comportamiento de **{empresa}** indica que es una opción estratégica para tu portafolio.")

except Exception as e:
    st.warning("Configurando conexión... Refresca en un momento.")
