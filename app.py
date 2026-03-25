import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. ESTILO "DARK ACADEMIC" PROFESIONAL
st.set_page_config(page_title="Valentina - Estrategia Financiera", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .titulo-v { color: #d4af37; font-family: 'Serif'; font-size: 35px; text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-family: monospace; }
    .recomendacion-card { background-color: #1c1f26; padding: 20px; border-radius: 10px; border-left: 5px solid #d4af37; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS ESTABLE
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=600)
def load_data_v():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    df = yf.download(tickers, start=start, end=end, progress=False, threads=False)
    if not df.empty:
        if 'Adj Close' in df.columns: df = df['Adj Close']
        elif 'Close' in df.columns: df = df['Close']
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(-1)
    return df

try:
    st.markdown('<p class="titulo-v">ANÁLISIS ESTRATÉGICO: VALENTINA</p>', unsafe_allow_html=True)
    
    data = load_data_v()
    
    if data.empty:
        st.error("Error de conexión con los mercados. Por favor refresca.")
        st.stop()

    # SIDEBAR
    empresa = st.sidebar.selectbox("Seleccione Activo:", tickers)
    monto = st.sidebar.number_input("Monto a Invertir (USD):", min_value=100, value=1000)
    
    # Cálculo de Retornos Diarios
    rets = data[empresa].pct_change().dropna()

    # --- SECCIÓN: TENDENCIA CENTRAL ---
    st.subheader(f"📊 Estadísticas de Retorno: {empresa}")
    c1, c2, c3 = st.columns(3)
    
    # Cálculos exactos
    media_val = rets.mean()
    mediana_val = rets.median()
    # Moda: redondeamos a 4 decimales para encontrar el retorno más frecuente
    moda_val = rets.round(4).mode()[0]

    c1.metric("MEDIA (Promedio Diario)", f"{media_val:.4%}")
    c2.metric("MEDIANA (Punto Medio)", f"{mediana_val:.4%}")
    c3.metric("MODA (Valor más común)", f"{moda_val:.4%}")

    st.markdown("---")

    # --- SECCIÓN: RECOMENDACIÓN GERENCIAL ---
    st.subheader("🎯 Recomendación de Inversión")
    
    # Lógica: Relación Riesgo/Retorno (Sharpe Ratio simplificado)
    volatilidad = rets.std()
    rendimiento_anual = media_val * 252
    riesgo_anual = volatilidad * (252**0.5)
    
    # Determinamos si es buena opción
    score = rendimiento_anual / riesgo_anual # Ratio de eficiencia
    
    with st.container():
        st.markdown('<div class="recomendacion-card">', unsafe_allow_html=True)
        
        if score > 0.6:
            st.success(f"✅ **¡EXCELENTE OPCIÓN!** {empresa} tiene un crecimiento muy sólido frente a su riesgo.")
            rec_texto = f"Con tus **${monto:,.2f} USD**, podrías esperar un crecimiento eficiente basado en su tendencia histórica de 10 años."
        elif score > 0.4:
            st.info(f"⚠️ **OPCIÓN MODERADA.** {empresa} es buena, pero tiene periodos de alta volatilidad.")
            rec_texto = "Es apta si buscas crecimiento a largo plazo y no te asustan las caídas temporales."
        else:
            st.warning(f"❌ **OPCIÓN DE ALTO RIESGO.** {empresa} presenta demasiada inestabilidad actualmente.")
            rec_texto = "Te recomendamos diversificar tus fondos o esperar a una fase de mercado más estable."
            
        st.write(rec_texto)
        st.write(f"*Nota técnica: La volatilidad anualizada de este activo es del **{riesgo_anual:.2%}**.*")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- GRÁFICAS MEJORADAS ---
    t1, t2 = st.tabs(["🧬 Análisis de Distribución", "📈 Trayectoria de Precios"])
    
    with t1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Histograma (Frecuencia de Ganancias/Pérdidas)**")
            fig_h = px.histogram(rets, nbins=100, color_discrete_sequence=['#d4af37'], marginal="box")
            fig_h.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color="white")
            st.plotly_chart(fig_h, use_container_width=True)
        with col_b:
            st.write("**Boxplot (Identificación de Riesgos Extremos)**")
            fig_b = px.box(rets, orientation='h', color_discrete_sequence=['#ffffff'])
            fig_b.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color="white")
            st.plotly_chart(fig_b, use_container_width=True)

    with t2:
        fig_l = px.line(data, y=empresa, color_discrete_sequence=['#d4af37'], title=f"Precio Histórico de {empresa}")
        fig_l.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color="white")
        st.plotly_chart(fig_l, use_container_width=True)

except Exception as e:
    st.error(f"Error detectado: {e}")
