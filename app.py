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
    # Solo las empresas solicitadas (sin Tesla)
    tk = ['AAPL', 'AMZN', 'GOOGL', 'META', 'MSFT', 'NVDA']
    df = yf.download(tk, period="10y", progress=False)
    return df['Close'] if 'Close' in df.columns else df['Adj Close']

data = load_data()

if data is not None and not data.empty:
    st.title("🏛️ Monitor Estratégico de Mercados")
    st.caption("Valentina | Facultad de Administración | Universidad Externado")

    t1, t2 = st.tabs(["💰 Precios y Retornos", "📊 Análisis Estadístico"])

    with t1:
        st.subheader("Precios Actuales y Rendimiento")
        cols = st.columns(len(data.columns))
        hoy, ayer = data.iloc[-1], data.iloc[-2]
        
        for i, col in enumerate(cols):
            ticker = data.columns[i]
            diff = ((hoy[ticker] - ayer[ticker]) / ayer[ticker]) * 100
            clase = "up" if diff > 0 else "down"
            with col:
                st.markdown(f"""<div class="kpi-card">
                    <div style="color:gray; font-size:12px;">{ticker}</div>
                    <div class="kpi-price">${hoy[ticker]:,.2f}</div>
                    <div class="{clase}">{'↑' if diff > 0 else '↓'} {abs(diff):.2f}% Hoy</div>
                </div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # --- MEJORA: GRÁFICA DE PRECIOS INTERACTIVA (Plotly) ---
        st.subheader("📈 Evolución Interactiva del Costo de las Acciones")
        fig_precios = px.line(data, 
                             labels={'value': 'Precio (USD)', 'Date': 'Fecha', 'variable': 'Empresa'},
                             title="Histórico de Precios (Pasa el mouse para ver detalles)")
        fig_precios.update_layout(plot_bgcolor='#1a1c24', paper_bgcolor='#0e1117', font_color='white', hovermode="x unified")
        st.plotly_chart(fig_precios, use_container_width=True)

        st.markdown("---")
        # Gráfica de Retornos con selector
        emp_p = st.selectbox("Ver Retornos Diarios de:", data.columns)
        rets = data.pct_change().dropna()
        fig_rets = px.line(rets[emp_p], title=f"Volatilidad: {emp_p}", color_discrete_sequence=['#00ff64'])
        fig_rets.update_layout(plot_bgcolor='#1a1c24', paper_bgcolor='#0e1117', font_color='white')
        st.plotly_chart(fig_rets, use_container_width=True)

    with t2:
        # Estadísticas: Media, Mediana, Moda
        st.subheader("🎯 Comparativa Estadística")
        stats = []
        for c in rets.columns:
            stats.append({
                "Empresa": c,
                "Media (Retorno)": f"{rets[c].mean():.4%}",
                "Mediana": f"{rets[c].median():.4%}",
                "Moda": f"{rets[c].round(4).mode()[0]:.4%}"
            })
        st.table(pd.DataFrame(stats))

        # Calculadora de Inversión por tiempo
        st.markdown("---")
        st.subheader("💵 Calculadora de Inversión Proyectada")
        c_inv, c_res = st.columns([1, 2])
        with c_inv:
            monto = st.number_input("Monto a invertir (USD):", value=2019)
            emp_c = st.selectbox("Empresa para proyectar:", data.columns)
        with c_res:
            m = rets[emp_c].mean()
            r1, r2, r3 = st.columns(3)
            r1.metric("En 1 Día", f"${monto*(1+m):,.2f}")
            r2.metric("En 1 Mes", f"${monto*(1+m)**21:,.2f}")
            r3.metric("En 1 Año", f"${monto*(1+m)**252:,.2f}")
        
        efi = (rets.mean() * 252) / (rets.std() * (252**0.5))
        st.success(f"🏆 **Recomendación:** La mejor opción por eficiencia es **{efi.idxmax()}**.")
else:
    st.error("No se pudo conectar con los datos.")
