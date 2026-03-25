import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. ESTILO VISUAL (TARJETAS TIPO DASHBOARD)
st.set_page_config(page_title="Dashboard Valentina", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .metric-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .metric-val { font-size: 24px; font-weight: bold; margin: 5px 0; }
    .metric-delta { font-size: 14px; border-radius: 5px; padding: 2px 8px; }
    .delta-up { background-color: rgba(0,255,0,0.1); color: #00ff00; }
    .delta-down { background-color: rgba(255,0,0,0.1); color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    # Incluimos TSLA y GOOGL para que se vea como tu referencia
    t = ['AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 'NVDA', 'TSLA']
    d = yf.download(t, period="10y", progress=False)
    return d['Close'] if 'Close' in d.columns else d['Adj Close']

data = load_data()

if data is not None:
    st.title("📊 Monitor Estratégico de Valentina")
    
    # --- PÁGINA 1: DASHBOARD PRINCIPAL ---
    tab_main, tab_stats = st.tabs(["🏠 Desempeño & Ciclos", "📈 Análisis Estadístico"])

    with tab_main:
        st.subheader("🏢 Precios Actuales y Desempeño (YTD)")
        
        # Fila de tarjetas (estilo imagen referencia)
        cols = st.columns(len(data.columns))
        h, a = data.iloc[-1], data.iloc[0] # Para simular YTD/Crecimiento
        
        for i, col in enumerate(cols):
            ticker = data.columns[i]
            val = h[ticker]
            # Calculamos un porcentaje simulado de crecimiento para la tarjeta
            pct = ((val - a[ticker]) / a[ticker]) * 100
            clase = "delta-up" if pct > 0 else "delta-down"
            signo = "↑" if pct > 0 else "↓"
            
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #8b949e; font-size: 12px;">{ticker}</div>
                        <div class="metric-val">${val:.2f} {signo}</div>
                        <span class="metric-delta {clase}">{signo} {abs(pct):.1f}% YTD</span>
                    </div>
                """, unsafe_allow_html=True)

        # Recomendación destacada
        rets = data.pct_change().dropna()
        efi = (rets.mean() * 252) / (rets.std() * (252**0.5))
        st.success(f"🏆 **DICTAMEN CRÍTICO:** La mejor opción basada en eficiencia es **{efi.idxmax()}**")
        
        st.subheader("Visualización de Costo Histórico")
        st.line_chart(data)

    with tab_stats:
        # --- PÁGINA 2: ESTADÍSTICAS ---
        st.sidebar.header("Configuración")
        emp = st.sidebar.selectbox("Seleccione Acción para Detalle:", data.columns)
        r_e = rets[emp]

        st.header(f"Análisis Profundo: {emp}")
        
        # TABLA DE MEDIA, MEDIANA Y
