import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. ESTILO DE TARJETAS (DASHBOARD DARK)
st.set_page_config(page_title="Valentina Analytics", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .metric-card {
        background-color: #1a1c24; padding: 20px; border-radius: 10px;
        border: 1px solid #30363d; text-align: center;
    }
    .metric-val { font-size: 22px; font-weight: bold; margin: 5px 0; }
    .delta-up { color: #00ff00; font-size: 14px; }
    .delta-down { color: #ff4b4b; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    t = ['AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 'NVDA', 'TSLA']
    d = yf.download(t, period="10y", progress=False)
    return d['Close'] if 'Close' in d.columns else d['Adj Close']

data = load_data()

if data is not None:
    st.title("🏛️ Monitor de Inteligencia Financiera")
    st.caption("Valentina | Facultad de Administración | Universidad Externado")

    # CREACIÓN DE PESTAÑAS
    tab1, tab2 = st.tabs(["💰 Desempeño y Costos", "📈 Análisis Estadístico"])

    with tab1:
        # TARJETAS DE PRECIOS (COMO TU IMAGEN)
        st.subheader("Precios Actuales y Rendimiento")
        cols = st.columns(len(data.columns))
        h, a = data.iloc[-1], data.iloc[0]
        
        for i, col in enumerate(cols):
            ticker = data.columns[i]
            pct = ((h[ticker] - data.iloc[-252][ticker]) / data.iloc[-252][ticker]) * 100
            clase = "delta-up" if pct > 0 else "delta-down"
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div style="color:gray; font-size:12px;">{ticker}</div>
                    <div class="metric-val">${h[ticker]:.2f}</div>
                    <div class="{clase}">{'↑' if pct > 0 else '↓'} {abs(pct):.1f}% YTD</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📈 Evolución del Costo de las Acciones (USD)")
        st.line_chart(data)
        
        # MEJOR OPCIÓN
        rets = data.pct_change().dropna()
        efi = (rets.mean() * 252) / (rets.std() * (252**0.5))
        st.success(f"🏆 **DICTAMEN CRÍTICO:** La mejor opción para invertir es **{efi.idxmax()}**.")

    with tab2:
        st.sidebar.header("Filtros de Análisis")
        emp = st.sidebar.selectbox("Acción a Detallar:", data.columns)
        monto = st.sidebar.number_input("Capital a Invertir (USD):", value=1000)
        r_e = rets[emp]

        st.header(f"Análisis Estadístico: {emp}")

        # CALCULADORA DE RETORNO (CUANTA PLATA SE DEVUELVE)
        retorno_esperado = monto * (1 + r_e.mean())
        ganancia_neta = retorno_esperado - monto
        
        st.subheader("💵 Proyección de Retorno")
        c1, c2 = st.columns(2)
        c1.metric("Monto Total Estimado", f"${retorno_esperado:,.2f}", f"{r_e.mean():.4%} esperado")
        c2.metric("Ganancia Neta Estimada", f"${ganancia_neta:,.2f}")

        # TABLA DE MEDIA, MEDIANA Y MODA (BONITA)
        st.subheader("🎯 Medidas de Tendencia Central")
        stats_df = pd.DataFrame({
            "Métrica": ["Media (Promedio)", "Mediana (Centro)", "Moda (Frecuente)"],
            "Valor": [f"{r_e.mean():.4%}", f"{r_e.median():.4%}", f"{r_e.round(4).mode()[0]:.4%}"],
            "Nota": ["Retorno diario esperado", "Punto medio de datos", "Valor más repetido"]
        })
        st.table(stats_df)

        # GRÁFICA DE RETORNOS
        st.subheader(f"🧬 Volatilidad de Retornos: {emp}")
        fig = px.line(r_e, labels={'value': 'Cambio %', 'Date': 'Fecha'}, color_discrete_sequence=['#d4af37'])
        fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

        # TABLA DE FRECUENCIAS
        st.subheader("📊 Distribución de Frecuencias")
        b = [-1, -0.02, -0.005, 0.005, 0.02, 1]
        lab = ["Caída", "Baja", "Estable", "Subida", "Salto"]
        fr = pd.cut(r_e, bins=b, labels=lab).value_counts().reset_index()
        fr.columns = ['Estado de Mercado', 'Días Registrados']
        st.table(fr)

else:
    st.error("Error al cargar datos. Refresca la página.")
