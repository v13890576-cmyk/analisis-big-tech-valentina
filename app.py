import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Analytics Big Tech - Valentina", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .titulo-v { color: #d4af37; font-family: 'Serif'; font-size: 35px; text-align: center; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 10px; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; }
    .report-card { background-color: #111111; padding: 20px; border-radius: 10px; border: 1px solid #444; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATOS VERÍDICOS (CACHÉ PARA VELOCIDAD)
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=3600)
def load_data_final():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
    if not df.empty:
        if 'Adj Close' in df.columns: df = df['Adj Close']
        elif 'Close' in df.columns: df = df['Close']
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
    return df

# 3. CUERPO DE LA APP
try:
    st.markdown('<p class="titulo-v">ESTRATEGIA Y ESTADÍSTICA: BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Análisis Gerencial | Universidad Externado de Colombia")

    data = load_data_final()

    if data.empty:
        st.error("Error al conectar con Yahoo Finance. Por favor reintenta.")
    else:
        # SIDEBAR
        st.sidebar.header("Panel de Control")
        empresa = st.sidebar.selectbox("Empresa para análisis detallado:", tickers)
        monto = st.sidebar.number_input("Monto a invertir (USD):", min_value=10, value=1000)
        
        rets = data[empresa].pct_change().dropna()

        # --- SECCIÓN 1: RECOMENDADOR DE INVERSIÓN ---
        st.header("🎯 Simulador de Inversión y Recomendación")
        col_inv1, col_inv2 = st.columns([1, 1.5])
        
        with col_inv1:
            # Cálculo de rendimiento y riesgo anual
            rend_anual = rets.mean() * 252 * 100
            volatilidad = rets.std() * (252**0.5) * 100
            
            st.markdown(f"""
            <div class="report-card">
            <h3>Análisis de {empresa}</h3>
            <p>Retorno Anualizado: <b>{rend_anual:.2f}%</b></p>
            <p>Riesgo Anualizado: <b>{volatilidad:.2f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_inv2:
            # Lógica de recomendación gerencial
            if volatilidad > 35:
                perfil = "AGRESIVO (Alto riesgo / Alta ganancia)"
                mensaje = "Ideal para capital que puede soportar caídas fuertes a cambio de crecimientos exponenciales."
            elif volatilidad > 25:
                perfil = "EQUILIBRADO"
                mensaje = "Una opción sólida que balancea crecimiento estable con periodos de corrección moderada."
            else:
                perfil = "CONSERVADOR"
                mensaje = "Busca preservar el capital con movimientos menos bruscos en el mercado."
            
            st.info(f"**Recomendación Valentina:** Basado en datos verídicos de 10 años, tu inversión de **${monto:,.0f} USD** en **{empresa}** se clasifica como **{perfil}**. {mensaje}")

        # --- SECCIÓN 2: ESTADÍSTICA Y TABLA ---
        st.markdown("---")
        st.subheader("📊 Parámetros de Tendencia Central")
        c1, c2, c3 = st.columns(3)
        c1.metric("MEDIA (Diaria)", f"{rets.mean():.5%}")
        c2.metric("MEDIANA", f"{rets.median():.5%}")
        c3.metric("MODA", f"{rets.round(4).mode()[0]:.5%}")

        tabs = st.tabs(["🧬 Gráficas de Riesgo", "📈 Trayectoria Histórica", "📋 Tabla de Frecuencias"])

        with tabs[0]:
            st.subheader("Distribución Detallada de Retornos")
            g1, g2 = st.columns(2)
            with g1:
                fig_h = px.histogram(rets, nbins=60, title="Histograma (Frecuencia de cambios)", color_discrete_sequence=['#d4af37'])
                fig_h.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white', xaxis_title="Retorno", yaxis_title="Días")
                st.plotly_chart(fig_h, use_container_width=True)
            with g2:
                fig_b = px.box(rets, orientation='h', title="Boxplot (Detección de Riesgo/Outliers)", color_discrete_sequence=['#ffffff'])
                fig_b.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
                st.plotly_chart(fig_b, use_container_width=True)

        with tabs[1]:
            st.subheader(f"Evolución del Precio: {empresa}")
            fig_l = px.line(data, y=empresa, color_discrete_sequence=['#d4af37'])
            fig_l.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white', xaxis_title="Año", yaxis_title="Precio USD")
            st.plotly_chart(fig_l, use_container_width=True)

        with tabs[2]:
            st.subheader("Tabla de Frecuencia de Movimientos Diarios")
            # Definir rangos de frecuencia
            bins = [-1, -0.02, 0, 0.02, 1]
            labels = ['Baja Fuerte (<-2%)', 'Baja Leve (-2% a 0%)', 'Subida Leve (0% a 2%)', 'Subida Fuerte (>2%)']
            frecuencia = pd.cut(rets, bins=bins, labels=labels).value_counts().reset_index()
            frecuencia.columns = ['Rango de Movimiento', 'Cantidad de Días']
            st.table(frecuencia)

except Exception as e:
    st.error(f"Error en ejecución: {e}")
