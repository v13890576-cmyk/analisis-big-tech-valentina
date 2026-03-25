import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN VISUAL MEJORADA
st.set_page_config(page_title="Análisis Big Tech - Valentina", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@1&family=Inter:wght@400;600&display=swap');
    
    .stApp { background-color: #fdfdfd; font-family: 'Inter', sans-serif; }
    
    /* TITULO VISIBLE: Color gris oscuro/negro */
    .titulo-principal {
        font-family: 'Libre Baskerville', serif;
        color: #1e293b;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0px;
    }

    .report-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    [data-testid="stMetricValue"] { color: #c2410c !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS CORREGIDA
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=3600)
def load_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365)
    # Descargamos los datos y nos aseguramos de que los nombres sean simples
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)
    
    # Si los datos tienen columnas multinivel (sucede a veces con yfinance), las limpiamos
    if isinstance(data.columns, pd.MultiIndex):
        data = data['Adj Close']
    else:
        data = data['Adj Close']
    return data

try:
    # Título manual para asegurar visibilidad
    st.markdown('<p class="titulo-principal">🏛️ ANÁLISIS ESTRATÉGICO DE ACCIONES BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Facultad de Administración | Universidad Externado de Colombia")
    st.markdown("---")

    df_precios = load_data()
    
    # Verificación de que los datos no estén vacíos
    if df_precios.empty:
        st.error("No se pudieron obtener datos. Intenta recargar la página.")
    else:
        df_retornos = df_precios.pct_change().dropna()

        # Selector
        empresa = st.sidebar.selectbox("Seleccione una empresa:", tickers)

        tabs = st.tabs(["📈 Evolución 10 Años", "📊 Retornos y Frecuencias", "🎯 KPIs de Desempeño"])

        # --- TAB 1: PRECIOS ---
        with tabs[0]:
            st.subheader(f"Precio Histórico de {empresa}")
            fig_precio = px.line(df_precios, y=empresa, color_discrete_sequence=['#c2410c'])
            fig_precio.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Fecha", yaxis_title="Precio USD")
            st.plotly_chart(fig_precio, use_container_width=True)

        # --- TAB 2: RETORNOS ---
        with tabs[1]:
            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.subheader("Gráfico de Volatilidad")
                fig_ret = px.area(df_retornos, y=empresa, color_discrete_sequence=['#475569'])
                st.plotly_chart(fig_ret, use_container_width=True)
            with c2:
                st.subheader("Frecuencia de Movimientos")
                bins = [-1, -0.05, -0.02, 0, 0.02, 0.05, 1]
                labels = ['Caída Fuerte', 'Caída Moderada', 'Leve Neg.', 'Leve Pos.', 'Subida Moderada', 'Subida Fuerte']
                frec = pd.cut(df_retornos[empresa], bins=bins, labels=labels).value_counts().sort_index()
                df_frec = pd.DataFrame({'Rango': frec.index, 'Días': frec.values})
                st.table(df_frec)

        # --- TAB 3: KPIs ---
        with tabs[2]:
            st.subheader("Indicadores de Gestión Estratégica")
            m1, m2, m3 = st.columns(3)
            
            # Cálculos
            total_ret = (df_precios[empresa].iloc[-1] / df_precios[empresa].iloc[0] - 1) * 100
            volatilidad = df_retornos[empresa].std() * (252**0.5) * 100
            ultimo_p = df_precios[empresa].iloc[-1]

            m1.metric("Rendimiento Total (10A)", f"{total_ret:.1f}%")
            m2.metric("Volatilidad Anual", f"{volatilidad:.1f}%")
            m3.metric("Último Precio", f"${ultimo_p:.2f}")

            # Gráfico de barras comparativo al final
            st.markdown("---")
            st.subheader("Comparativo de Crecimiento: Todas las empresas")
            rendimientos = ((df_precios.iloc[-1] / df_precios.iloc[0]) - 1) * 100
            fig_barras = px.bar(rendimientos, color=rendimientos.values, color_continuous_scale='Oranges')
            st.plotly_chart(fig_barras, use_container_width=True)

    st.markdown("---")
    st.caption("© 2026 Valentina - Reporte Generencial")

except Exception as e:
    st.error(f"Error detectado: {e}. Por favor revisa que el archivo 'requirements.txt' esté correcto.")
