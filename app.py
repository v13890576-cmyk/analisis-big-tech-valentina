import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Analisis Valentina", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    t = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']
    d = yf.download(t, period="10y", progress=False)
    return d['Close'] if 'Close' in d.columns else d['Adj Close']

# 2. EJECUCIÓN
data = load_data()

if data is not None:
    st.title("📊 MONITOR ESTRATÉGICO")
    
    # --- CUADRO DE PRECIOS CON FLECHAS ---
    st.subheader("🏢 Precios Actuales")
    h, a = data.iloc[-1], data.iloc[-2]
    
    res = []
    for c in data.columns:
        dif = h[c] - a[c]
        ico = "▲" if dif > 0 else "▼"
        col = "green" if dif > 0 else "red"
        res.append({"Empresa": c, "Precio": f"${h[c]:.2f}", "Trend": ico, "Diff": dif})
    
    df_res = pd.DataFrame(res)
    # Mostramos la tabla con las flechas de color
    st.table(df_res.style.apply(lambda x: ["","","",f"color: {'green' if x.Diff > 0 else 'red'}"], axis=1))

    # --- LA MEJOR OPCIÓN ---
    rets = data.pct_change().dropna()
    efi = (rets.mean() * 252) / (rets.std() * (252**0.5))
    st.success(f"🏆 MEJOR OPCIÓN: **{efi.idxmax()}** (Basado en eficiencia riesgo/retorno)")

    # --- TABLA DE FRECUENCIAS ---
    st.markdown("---")
    emp = st.sidebar.selectbox("Acción:", data.columns)
    r_e = rets[emp]
    
    st.subheader(f"Análisis: {emp}")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Frecuencias**")
        b = [-1, -0.02, -0.005, 0.005, 0.02, 1]
        lab = ["Caída", "Baja", "Estable", "Subida", "Salto"]
        fr = pd.cut(r_e, bins=b, labels=lab).value_counts().reset_index()
        fr.columns = ['Escenario', 'Días']
        st.table(fr)
    with col2:
        st.write("**Estadísticas**")
        st.metric("MEDIA", f"{r_e.mean():.4%}")
        st.metric("MODA", f"{r_e.round(4).mode()[0]:.4%}")

    # --- GRÁFICAS ---
    st.line_chart(data[emp])
    st.plotly_chart(px.line(r_e, title="Retornos Diarios"))

else:
    st.error("Error de conexión. Revisa tu archivo requirements.txt")
