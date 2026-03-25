import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Valentina - Análisis Final", layout="wide")
st.markdown("<style>.stApp { background-color: #050505; color: white; }</style>", unsafe_allow_html=True)

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
    st.markdown("<h1 style='text-align: center; color: #d4af37;'>ANÁLISIS CRÍTICO Y COSTO DE ACCIONES</h1>", unsafe_allow_html=True)
    st.caption("Valentina | Universidad Externado de Colombia")

    data = get_data()
    if data is None or data.empty:
        st.error("Error de conexión. Intenta refrescar la página.")
        st.stop()

    # --- LÓGICA DE LA MEJOR OPCIÓN ---
    rets_all = data.pct_change().dropna()
    eficiencia = (rets_all.mean() * 252) / (rets_all.std() * (252**0.5))
    mejor_empresa = eficiencia.idxmax()

    st.markdown(f"### 🏆 Recomendación de Inversión: {mejor_empresa}")
    st.success(f"Basado en eficiencia, **{mejor_empresa}** es la mejor opción para tu capital.")

    # --- NUEVA SECCIÓN: GRÁFICA DEL COSTO (PRECIOS) ---
    st.subheader("📈 Evolución del Costo de las Acciones (USD)")
    # Gráfica interactiva de precios
    fig_precios = px.line(data, labels={'value': 'Precio USD', 'Date': 'Fecha'}, 
                         title="Comparativo de Precios de Cierre (10 Años)")
    fig_precios.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white", legend_title="Empresas")
    fig_precios.update_xaxes(gridcolor='#222')
    fig_precios.update_yaxes(gridcolor='#222')
    st.plotly_chart(fig_precios, use_container_width=True)

    # --- ANÁLISIS POR EMPRESA ---
    st.markdown("---")
    empresa = st.sidebar.selectbox("Detalle de:", data.columns)
    monto = st.sidebar.number_input("Monto a invertir (USD):", value=1000)
    rets = rets_all[empresa]

    # --- TABLA DE FRECUENCIAS ---
    st.subheader(f"📋 Tabla de Frecuencias: {empresa}")
    bins = [-1, -0.02, -0.005, 0.005, 0.02, 1]
    labels = ['Baja Fuerte', 'Baja Leve', 'Estable', 'Subida Leve', 'Subida Fuerte']
    frec = pd.cut(rets, bins=bins, labels=labels).value_counts().reset_index()
    frec.columns = ['Rango', 'Días']
    frec['% Relativo'] = (frec['Días'] / frec['Días'].sum()) * 100
    st.table(frec.style.format({'% Relativo': '{:.2f}%'}))

    # --- BOXPLOT Y TENDENCIA ---
    t1, t2 = st.tabs(["🧬 Riesgo (Boxplot)", "📊 Tendencia Central"])
    
    with t1:
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=rets, name=empresa, marker_color='#d4af37', boxpoints='outliers'))
        fig_box.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white", title="Outliers (Días de pánico o euforia)")
        st.plotly_chart(fig_box, use_container_width=True)

    with t2:
        c1, c2, c3 = st.columns(3)
        c1.metric("MEDIA", f"{rets.mean():.4%}")
        c2.metric("MEDIANA", f"{rets.median():.4%}")
        c3.metric("MODA", f"{rets.round(4).mode()[0]:.4%}")
        st.info(f"Con **${monto:,.0f}**, el análisis sugiere que este activo se ajusta a una estrategia de administración moderna.")

except Exception as e:
    st.warning("Sincronizando con el mercado... espera 5 segundos.")
