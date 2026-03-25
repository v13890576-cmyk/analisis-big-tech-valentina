import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN Y ESTILO "FINTECH"
st.set_page_config(page_title="Dashboard Valentina", layout="wide")
st.markdown("""
    <style> 
    .stApp { background-color: #0e1117; color: white; }
    .kpi-card {
        background-color: #1a1c24; padding: 20px; border-radius: 12px;
        border: 1px solid #30363d; text-align: center;
    }
    .kpi-price { font-size: 26px; font-weight: bold; color: white; white-space: nowrap; }
    .delta-up { color: #00ff64; font-size: 14px; }
    .delta-down { color: #ff3232; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    t = ['AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 'NVDA', 'TSLA']
    d = yf.download(t, period="10y", progress=False)
    return d['Close'] if 'Close' in d.columns else d['Adj Close']

data = load_data()

if not data.empty:
    st.title("🏛️ Monitor Estratégico de Mercados")
    st.caption("Valentina | Universidad Externado de Colombia")

    tab1, tab2 = st.tabs(["💰 Precios y Desempeño", "📊 Análisis Estadístico y Retornos"])

    with tab1:
        st.subheader("Precios Actuales y Rendimiento (YTD)")
        cols = st.columns(len(data.columns))
        h, a = data.iloc[-1], data.iloc[0]
        
        for i, col in enumerate(cols):
            ticker = data.columns[i]
            pct = ((h[ticker] - data.iloc[-252][ticker]) / data.iloc[-252][ticker]) * 100
            clase = "delta-up" if pct > 0 else "delta-down"
            with col:
                st.markdown(f"""<div class="kpi-card">
                    <div style="color:gray; font-size:12px;">{ticker}</div>
                    <div class="kpi-price">${h[ticker]:.2f}</div>
                    <div class="{clase}">{'↑' if pct > 0 else '↓'} {abs(pct):.1f}% YTD</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📈 Evolución del Costo Histórico")
        st.line_chart(data)

    with tab2:
        # --- CÁLCULOS DE RETORNOS Y ESTADÍSTICAS ---
        rets = data.pct_change().dropna()
        
        # Tabla comparativa de todas las empresas
        st.subheader("🎯 Comparativa de Medidas de Tendencia y Retorno")
        
        stats_data = []
        for c in rets.columns:
            stats_data.append({
                "Empresa": c,
                "Retorno Promedio (Media)": f"{rets[c].mean():.4%}",
                "Punto Central (Mediana)": f"{rets[c].median():.4%}",
                "Valor Frecuente (Moda)": f"{rets[c].round(4).mode()[0]:.4%}",
                "Riesgo (Volatilidad)": f"{rets[c].std():.4%}"
            })
        
        df_stats = pd.DataFrame(stats_data)
        st.table(df_stats)

        # --- RECOMENDACIÓN DE INVERSIÓN ---
        st.markdown("---")
        st.subheader("🏆 Recomendación de Inversión Crítica")
        
        # Cálculo de eficiencia (Sharpe Ratio simplificado)
        eficiencia = (rets.mean() * 252) / (rets.std() * (252**0.5))
        mejor_empresa = eficiencia.idxmax()
        
        col_rec, col_calc = st.columns([1, 1])
        
        with col_rec:
    
