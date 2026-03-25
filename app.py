import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN VISUAL (ESTILO VALENTINA: "SOFT CORPORATE")
st.set_page_config(page_title="Análisis Big Tech - Valentina", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@1&family=Inter:wght@400;600&display=swap');
    
    /* Fondo y tipografía */
    .stApp { background-color: #fdfdfd; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Libre Baskerville', serif; color: #1e293b; }
    
    /* Tarjetas blancas para los datos */
    .report-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    
    /* Color de las métricas (Terracota) */
    [data-testid="stMetricValue"] { color: #c2410c !important; font-size: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (APPLE, MSFT, NVIDIA, META, AMAZON)
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=3600)
def load_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365) # 10 años exactos
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']
    return data

try:
    df_precios = load_data()
    df_retornos = df_precios.pct_change().dropna()

    # 3. CABECERA DEL PROYECTO
    st.title("🏛️ ANÁLISIS ESTRATÉGICO DE ACCIONES BIG TECH")
    st.caption("Valentina | Facultad de Administración | Universidad Externado de Colombia")
    st.markdown("---")

    # Selector en la barra lateral para un análisis profundo
    st.sidebar.header("Panel de Control")
    empresa = st.sidebar.selectbox("Seleccione una empresa para detalle:", tickers)

    # 4. ORGANIZACIÓN POR SECCIONES (TABS)
    tab1, tab2, tab3 = st.tabs(["📈 Evolución Histórica", "📊 Retornos y Frecuencias", "🎯 Indicadores de Desempeño"])

    # --- SECCIÓN 1: HISTÓRICO 10 AÑOS ---
    with tab1:
        st.subheader(f"Trayectoria de {empresa} (Última Década)")
        fig_precio = px.line(df_precios[empresa], color_discrete_sequence=['#c2410c'])
        fig_precio.update_layout(plot_bgcolor='white', xaxis_title="Año", yaxis_title="Precio de Cierre (USD)")
        st.plotly_chart(fig_precio, use_container_width=True)
        
        st.write("Este gráfico permite observar la tendencia de crecimiento sostenido y los ciclos de mercado de la empresa seleccionada.")

    # --- SECCIÓN 2: RETORNOS Y TABLA DE FRECUENCIAS ---
    with tab2:
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("Volatilidad de Retornos Diarios")
            fig_ret = px.area(df_retornos[empresa], color_discrete_sequence=['#475569'])
            fig_ret.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_ret, use_container_width=True)
            
        with col2:
            st.subheader("Tabla de Frecuencias")
            # Agrupamos los retornos para ver qué tan seguido gana o pierde
            bins = [-1, -0.05, -0.02, 0, 0.02, 0.05, 1]
            labels = ['Pérdida Crítica', 'Pérdida Fuerte', 'Leve Negativo', 'Leve Positivo', 'Ganancia Fuerte', 'Ganancia Crítica']
            frecuencia = pd.cut(df_retornos[empresa], bins=bins, labels=labels).value_counts().sort_index()
            df_frec = pd.DataFrame({'Rango de Retorno': frecuencia.index, 'Número de Días': frecuencia.values})
            
            st.dataframe(df_frec, hide_index=True, use_container_width=True)

    # --- SECCIÓN 3: INDICADORES (KPIs) Y BARRAS ---
    with tab3:
        st.subheader(f"Métricas Gerenciales: {empresa}")
        c1, c2, c3 = st.columns(3)
        
        # Cálculos de desempeño
        rend_total = (df_precios[empresa].iloc[-1] / df_precios[empresa].iloc[0] - 1) * 100
        volatilidad = df_retornos[empresa].std() * (252**0.5) * 100
        max_valor = df_precios[empresa].max()

        c1.metric("Rendimiento Total (10A)", f"{rend_total:.1f}%")
        c2.metric("Volatilidad Anualizada", f"{volatilidad:.1f}%")
        c3.metric("Precio Máximo", f"${max_valor:.2f}")

        st.markdown("---")
        st.subheader("Comparativa de Rendimiento entre Empresas (%)")
        
        # Gráfico de barras comparativo
        rendimientos_comp = ((df_precios.iloc[-1] / df_precios.iloc[0]) - 1) * 100
        fig_barras = px.bar(rendimientos_comp, 
                            color=rendimientos_comp.values, 
                            color_continuous_scale='Oranges',
                            labels={'value': '% de Rendimiento Acumulado', 'index': 'Empresa'})
        fig_barras.update_layout(showlegend=False, plot_bgcolor='white')
        st.plotly_chart(fig_barras, use_container_width=True)

    st.markdown("---")
    st.caption("© 2024 Valentina - Análisis Académico | Universidad Externado de Colombia")

except Exception as e:
    st.error(f"Hubo un problema al cargar los datos financieros: {e}")
