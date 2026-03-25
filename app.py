import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. ESTILO PROFESIONAL
st.set_page_config(page_title="Valentina - Tech Strategy", layout="wide")
st.markdown("<style>.stApp{background-color:#050505;color:white;}.titulo{color:#d4af37;text-align:center;font-weight:bold;border-bottom:2px solid #333;}</style>", unsafe_allow_html=True)

# 2. CARGA DE DATOS ESTABLE
@st.cache_data(ttl=600)
def load_market_data():
    try:
        t = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
        df = yf.download(t, start=datetime.now()-timedelta(days=3650), progress=False)
        return df['Close'] if 'Close' in df.columns else df['Adj Close']
    except: return None

data = load_market_data()

if data is None or data.empty:
    st.error("Error de conexión. Refresca la página en 10 segundos.")
else:
    st.markdown('<p class="titulo">ESTRATEGIA Y COSTO DE ACCIONES: BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Universidad Externado de Colombia")

    # --- CUADRO DE EMPRESAS ---
    st.subheader("🏢 Estado Actual del Mercado")
    resumen = pd.DataFrame({
        "Precio USD": data.iloc[-1],
        "Var Diaria %": data.pct_change().iloc[-1] * 100
    })
    st.table(resumen.style.format({'Precio USD': '${:.2f}', 'Var Diaria %': '{:+.2f}%'}))

    # --- LA MEJOR OPCIÓN (CRÍTICA) ---
    rets_all = data.pct_change().dropna()
    eficiencia = (rets_all.mean() * 252) / (rets_all.std() * (252**0.5))
    mejor = eficiencia.idxmax()
    st.success(f"🏆 **DICTAMEN CRÍTICO:** La mejor opción para tu inversión es **{mejor}** por su alta eficiencia retorno/riesgo.")

    # --- GRÁFICA DE COSTO (PRECIOS) ---
    st.subheader("📈 Evolución del Costo (10 Años)")
    st.line_chart(data)

    # --- ANÁLISIS DETALLADO ---
    st.sidebar.header("Filtros")
    emp = st.sidebar.selectbox("Seleccione Activo:", data.columns)
    monto = st.sidebar.number_input("Inversión (USD):", value=1000)
    r = rets_all[emp]

    t1, t2, t3 = st.tabs(["📋 Frecuencias", "📊 Retornos", "🧬 Estadística"])

    with t1:
        st.write(f"**Distribución de Probabilidad: {emp}**")
        bins = [-1, -0.02, -0.005, 0.005, 0.02, 1]
        labels = ['Caída', 'Baja', 'Estable', 'Subida', 'Salto']
        f = pd.cut(r, bins=bins, labels=labels).value_counts().reset_index()
        f.columns = ['Escenario', 'Días']; f['%'] = (f['Días']/len(r))*100
        st.table(f.style.format({'%': '{:.2f}%'}))

    with t2:
        st.plotly_chart(px.line(r, title="Volatilidad Diaria (Retornos)", color_discrete_sequence=['#d4af37']).update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white"))
        fig_b = go.Figure().add_trace(go.Box(y=r, name=emp, marker_color='#d4af37', boxpoints='outliers'))
        st.plotly_chart(fig_b.update_layout(plot_bgcolor='#050505', paper_bgcolor='#050505', font_color="white", title="Boxplot de Riesgo"))

    with t3:
        c1, c2, c3 = st.columns(3)
        c1.metric("MEDIA", f"{r.mean():.4%}")
        c2.metric("MEDIANA", f"{r.median():.4%}")
        c3.metric("
