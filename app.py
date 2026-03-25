import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="Dashboard Valentina", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .kpi-card {
        background-color: #1a1c24; padding: 20px; border-radius: 12px;
        border: 1px solid #30363d; text-align: center; margin-bottom: 10px;
    }
    .kpi-price { font-size: 24px; font-weight: bold; color: white; white-space: nowrap; }
    .up { color: #00ff64; } .down { color: #ff3232; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    tickers = ['AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 'NVDA']
    df = yf.download(tickers, period="10y", progress=False)
    return df['Close'] if 'Close' in df.columns else df['Adj Close']

data = load_data()

if data is not None and not data.empty:
    st.title("🏛️ Monitor Estratégico de Mercados")
    st.caption("Valentina | Facultad de Administración | Universidad Externado")

    t1, t2 = st.tabs(["💰 Precios y Retornos", "📊 Análisis Estadístico"])

    with t1:
        # TARJETAS DE PRECIOS
        cols = st.columns(len(data.columns))
        precios, ayer = data.iloc[-1], data.iloc[-2]
        for i, col in enumerate(cols):
            tk = data.columns[i]
            diff = ((precios[tk] - ayer[tk]) / ayer[tk]) * 100
            clase = "up" if diff > 0 else "down"
            with col:
                st.markdown(f'<div class="kpi-card"><div style="color:gray;font-size:12px;">{tk}</div><div class="kpi-price">${precios[tk]:,.2f}</div><div class="{clase}">{"↑" if diff > 0 else "↓"} {abs(diff):.2f}% Hoy</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        emp_p = st.selectbox("Seleccione empresa para ver Retornos:", data.columns)
        rets = data.pct_change().dropna()
        fig = px.line(rets[emp_p], title=f"Volatilidad Diaria: {emp_p}", labels={'value':'%','Date':'Fecha'}, color_discrete_sequence=['#00ff64'])
        fig.update_layout(plot_bgcolor='#1a1c24', paper_bgcolor='#0e1117', font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        # TABLA DE ESTADÍSTICAS
        st.subheader("🎯 Comparativa: Media, Mediana y Moda")
        stats = []
        for c in rets.columns:
            stats.append({"Empresa": c, "Media": f"{rets[c].mean():.4%}", "Mediana": f"{rets[c].median():.4%}", "Moda": f"{rets[c].round(4).mode()[0]:.4%}"})
        st.table(pd.DataFrame(stats))

        # --- CALCULADORA UNIVERSAL POR TIEMPO ---
        st.markdown("---")
        st.subheader("💵 Calculadora de Inversión Proyectada")
        c1, c2 = st.columns([1, 2])
        
        with c1:
            monto = st.number_input("Monto a invertir (USD):", value=2000, step=100)
            emp_calc = st.selectbox("Empresa para calcular:", data.columns)
        
        with c2:
            m = rets[emp_calc].mean()
            r_dia = monto * (1 + m)
            r_mes = monto * (1 + m)**21
            r_año = monto * (1 + m)**252
            
            res1, res2, res3 = st.columns(3)
            res1.metric("En 1 Día", f"${r_dia:,.2f}")
            res2.metric("En 1 Mes", f"${r_mes:,.2f}")
            res3.metric("En 1 Año", f"${r_año:,.2f}")
        
        st.success(f"🏆 **Nota:** La proyección anual de **{emp_calc}** usa el interés compuesto basado en su media histórica de 10 años.")
else:
    st.error("Error al cargar datos.")
