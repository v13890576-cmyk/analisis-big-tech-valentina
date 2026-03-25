import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Dashboard Valentina", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .kpi-card {
        background-color: #1a1c24; padding: 20px; border-radius: 12px;
        border: 1px solid #30363d; text-align: center; margin-bottom: 10px;
    }
    .kpi-price { font-size: 24px; font-weight: bold; color: white; white-space: nowrap; }
    .up { color: #00ff64; font-size: 14px; }
    .down { color: #ff3232; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    # Eliminamos TSLA de la lista
    tickers = ['AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 'NVDA']
    df = yf.download(tickers, period="10y", progress=False)
    return df['Close'] if 'Close' in df.columns else df['Adj Close']

data = load_data()

if data is not None and not data.empty:
    st.title("🏛️ Monitor Estratégico de Mercados")
    st.caption("Valentina | Facultad de Administración | Universidad Externado")

    # PESTAÑAS
    t1, t2 = st.tabs(["💰 Precios y Retornos", "📊 Análisis Estadístico"])

    with t1:
        st.subheader("Precios Actuales y Rendimiento")
        cols = st.columns(len(data.columns))
        precios, ayer = data.iloc[-1], data.iloc[-2]
        
        for i, col in enumerate(cols):
            tk = data.columns[i]
            diff = ((precios[tk] - ayer[tk]) / ayer[tk]) * 100
            clase = "up" if diff > 0 else "down"
            with col:
                st.markdown(f"""<div class="kpi-card">
                    <div style="color:gray; font-size:12px;">{tk}</div>
                    <div class="kpi-price">${precios[tk]:,.2f}</div>
                    <div class="{clase}">{'↑' if diff > 0 else '↓'} {abs(diff):.2f}% Hoy</div>
                </div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # SELECTOR EN LA PÁGINA PRINCIPAL
        col_select, col_empty = st.columns([1, 2])
        with col_select:
            emp_principal = st.selectbox("Seleccione empresa para ver Retornos:", data.columns)
        
        # GRÁFICA DE RETORNOS EN PÁGINA PRINCIPAL
        rets = data.pct_change().dropna()
        fig_rets = px.line(rets[emp_principal], 
                          title=f"Volatilidad de Retornos Diarios: {emp_principal}",
                          labels={'value': 'Cambio %', 'Date': 'Fecha'},
                          color_discrete_sequence=['#00ff64'])
        fig_rets.update_layout(plot_bgcolor='#1a1c24', paper_bgcolor='#0e1117', font_color='white')
        st.plotly_chart(fig_rets, use_container_width=True)
        
        st.subheader("Evolución Histórica de Precios (Costo)")
        st.line_chart(data)

    with t2:
        # TABLA DE MEDIA, MEDIANA Y MODA
        st.subheader("🎯 Comparativa Estadística Total")
        stats = []
        for c in rets.columns:
            stats.append({
                "Empresa": c,
                "Retorno Medio (Media)": f"{rets[c].mean():.4%}",
                "Punto Medio (Mediana)": f"{rets[c].median():.4%}",
                "Valor Frecuente (Moda)": f"{rets[c].round(4).mode()[0]:.4%}"
            })
        st.table(pd.DataFrame(stats))

        # RECOMENDACIÓN E INVERSIÓN
        st.markdown("---")
        efi = (rets.mean() * 252) / (rets.std() * (252**0.5))
        mejor = efi.idxmax()
        
        c_rec, c_calc = st.columns(2)
        with c_rec:
            st.success(f"🏆 **RECOMENDACIÓN:** Invertir en **{mejor}**")
            st.write("Seleccionada por su alta eficiencia retorno/riesgo en 10 años.")
        with c_calc:
            monto = st.number_input("Inversión Estimada (USD):", value=1000)
            res = monto * (1 + rets[mejor].mean())
            st.metric(f"Proyección en {mejor}", f"${res:,.2f}")

else:
    st.error("Error de conexión. Intente refrescar la página.")
