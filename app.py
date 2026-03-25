import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Análisis Valentina", layout="wide")
st.markdown("<style>.stApp{background-color:#050505;color:white;}</style>", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    t = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
    d = yf.download(t, period="10y", progress=False)
    return d['Close'] if 'Close' in d.columns else d['Adj Close']

# 2. CUERPO PRINCIPAL
st.title("📈 ESTRATEGIA Y MONITOREO DE ACCIONES")
data = load_data()

if data is not None and not data.empty:
    # --- CUADRO DE EMPRESAS CON FLECHAS ---
    st.subheader("🏢 Estado Actual del Mercado")
    
    precios_hoy = data.iloc[-1]
    precios_ayer = data.iloc[-2]
    
    resumen_data = []
    for ticker in data.columns:
        actual = precios_hoy[ticker]
        anterior = precios_ayer[ticker]
        diff = actual - anterior
        # Lógica de flechas
        icono = "🔺" if diff > 0 else "🔻"
        color = "green" if diff > 0 else "red"
        resumen_data.append({
            "Empresa": ticker,
            "Precio USD": f"${actual:.2f}",
            "Tendencia": f"{icono}",
            "Cambio": diff
        })
    
    df_resumen = pd.DataFrame(resumen_data)
    # Aplicar color a la flecha
    st.table(df_resumen.style.apply(lambda x: ["color: white", "color: white", f"color: {'green' if x['Cambio'] > 0 else 'red'}", "display: none"], axis=1))

    # --- RECOMENDACIÓN CRÍTICA ---
    rets = data.pct_change().dropna()
    eficiencia = (rets.mean() * 252) / (rets.std() * (252**0.5))
    mejor = eficiencia.idxmax()
    st.success(f"🏆 **LA MEJOR OPCIÓN:** Invertir en **{mejor}** es la decisión más eficiente hoy.")

    # --- TABLA DE FRECUENCIAS CORREGIDA ---
    st.markdown("---")
    emp = st.sidebar.selectbox("Seleccione Acción:", data.columns)
    r_emp = rets[emp]
    
    st.subheader(f"📊 Análisis Detallado: {emp}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Tabla de Frecuencias (Rangos)**")
        bins = [-1, -0.02, -0.005, 0.005, 0.02, 1]
