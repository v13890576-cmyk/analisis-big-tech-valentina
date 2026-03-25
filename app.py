import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. ESTILO VISUAL (CORREGIDO PARA VISIBILIDAD)
st.set_page_config(page_title="Big Tech - Valentina", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    /* Título en color negro pizarra para que sea legible */
    .titulo-v {
        color: #1e293b;
        font-family: 'Serif';
        font-size: 32px;
        font-weight: bold;
    }
    [data-testid="stMetricValue"] { color: #c2410c !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN DE DATOS REFORZADA
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

@st.cache_data(ttl=3600)
def load_data():
    end = datetime.now()
    start = end - timedelta(days=10*365)
    # Descargamos los datos
    df = yf.download(tickers, start=start, end=end, progress=False)
    
    # LIMPIEZA CRÍTICA: Esto evita el error 'Adj Close'
    if 'Adj Close' in df.columns:
        df = df['Adj Close']
    elif 'Close' in df.columns:
        df = df['Close']
    
    # Si las columnas tienen niveles extra, los aplanamos
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
        
    return df

# 3. INTERFAZ
try:
    st.markdown('<p class="titulo-v">🏛️ ANÁLISIS ESTRATÉGICO DE ACCIONES BIG TECH</p>', unsafe_allow_html=True)
    st.caption("Valentina | Universidad Externado de Colombia | Facultad de Administración")
    st.markdown("---")

    data = load_data()
    
    if data.empty:
        st.warning("Cargando datos... por favor refresca la página en un momento.")
    else:
        # Selector lateral
        empresa = st.sidebar.selectbox("Selecciona una Empresa:", tickers)
        
        # Pestañas
        t1, t2, t3 = st.tabs(["📈 Histórico (10 años)", "📊 Retornos", "🎯 Indicadores"])

        with t1:
            st.subheader(f"Evolución del Precio: {empresa}")
            fig1 = px.line(data, y=empresa, color_discrete_sequence=['#c2410c'])
            fig1.update_layout(plot_bgcolor='white', xaxis_title="Año", yaxis_title="Precio (USD)")
            st.plotly_chart(fig1, use_container_width=True)

        with t2:
            col_a, col_b = st.columns([1.5, 1])
            rets = data[empresa].pct_change().dropna()
            
            with col_a:
                st.subheader("Volatilidad Diaria")
                fig2 = px.area(rets, color_discrete_sequence=['#475569'])
                st.plotly_chart(fig2, use_container_width=True)
            
            with col_b:
                st.subheader("Tabla de Frecuencias")
                bins = [-1, -0.02, 0, 0.02, 1]
                labs = ['Baja', 'Leve Neg.', 'Leve Pos.', 'Alta']
                df_f = pd.cut(rets, bins=bins, labels=labs).value_counts().reset_index()
                df_f.columns = ['Rango', 'Días']
                st.table(df_f)

        with t3:
            st.subheader("Desempeño Gerencial")
            m1, m2, m3 = st.columns(3)
            
            rend_tot = (data[empresa].iloc[-1] / data[empresa].iloc[0] - 1) * 100
            m1.metric("Rendimiento 10A", f"{rend_tot:.1f}%")
            m2.metric("Precio Actual", f"${data[empresa].iloc[-1]:.2f}")
            m3.metric("Empresa", empresa)
            
            st.markdown("---")
            st.subheader("Comparativa de Crecimiento Total")
            comp = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
            fig3 = px.bar(comp, color=comp.values, color_continuous_scale='Oranges')
            st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
    st.error(f"Error técnico: {e}. Revisa que 'requirements.txt' esté correcto.")
