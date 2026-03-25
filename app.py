import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Análisis Valentina", layout="wide")
st.markdown("<style>.stApp{background-color:#050505;color:white;}</style>", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    t = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
    d = yf.download(t, period="10y", progress=False)
    return d['Close'] if 'Close' in d.columns else d['Adj Close']

# 2. CUERPO DE LA APP
st.title("📈 ESTRATEGIA Y COSTO DE ACCIONES")
data = load_data()

if data is not None and not data.empty:
    # --- CUADRO DE EMPRESAS Y COSTO ---
    st.subheader("🏢 Monitoreo de Precios Actuales")
    resumen = pd.DataFrame({"Precio Actual (USD)": data.iloc[-1]})
    st.table(resumen.style.format("${:.2f}"))
    
    st.subheader("📊 Gráfica de Costo Histórico")
    st.line_chart(data)

    # --- LÓGICA DE INVERSIÓN ---
    rets = data.pct_change().dropna()
    eficiencia = (rets.mean() * 252) / (rets.std() * (252**0.5))
    mejor = eficiencia.idxmax()
    
    st.success(f"🏆 **DICTAMEN CRÍTICO:** La mejor opción para invertir es **{mejor}** por su relación retorno/riesgo.")

    # --- ANÁLISIS POR EMPRESA ---
    emp = st.sidebar.selectbox("Seleccione Acción:", data.columns)
    r_emp = rets[emp]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Tabla de Frecuencias: {emp}**")
        bins = [-1, -0.02, -0.005, 0.005, 0.02, 1]
        frec = pd.cut(r_emp, bins=bins).value_counts().reset_index()
        frec.columns = ['Rango de Retorno', 'Días']
        st.table(frec)
    
    with col2:
        st.write("**Estadísticas de Tendencia**")
        st.metric("MEDIA", f"{r_emp.mean():.4%}")
        st.metric("MEDIANA", f"{r_emp.median():.4%}")
        st.metric("MODA", f"{r_emp.round(4).mode()[0]:.4%}")

    # --- GRÁFICA DE RETORNOS ---
    st.subheader(f"🧬 Volatilidad Diaria (Retornos) de {emp}")
    st.plotly_chart(px.line(r_emp, color_discrete_sequence=['#d4af37']).update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white'))
else:
    st.error("Error al conectar con Yahoo Finance. Intenta refrescar.")
