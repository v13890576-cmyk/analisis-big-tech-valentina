import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN VISUAL (ESTILO CYBERPUNK)
# ==========================================
st.set_page_config(page_title="Big Tech - Valentina", layout="wide", initial_sidebar_state="collapsed")

# CSS para Fondo Negro y Tipografía Clara
style_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Inter:wght@400;600&display=swap');
    
    /* Fondo Negro Total */
    .stApp { background-color: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Títulos Futuristas */
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #ffffff; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Tarjetas de Información Oscuras */
    .report-card {
        background-color: #111111;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #333333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* Métricas con color de resalte */
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    
    /* Texto general claro */
    .stMarkdown, .stCaption { color: #dddddd; }
    </style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE DATOS (VERÍDICOS DE YAHOO)
# ==========================================
# Tus empresas
tickers = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMZN']

# --- NOVEDAD: DICCIONARIO DE COLORES POR EMPRESA ---
colores_empresas = {
    'AAPL': '#f8f9fa', # Blanco Plata
    'MSFT': '#00a4ef', # Azul Microsoft
    'NVDA': '#76b900', # Verde Nvidia
    'META': '#0081fb', # Azul Meta
    'AMZN': '#ff9900'  # Naranja Amazon
}

@st.cache_data(ttl=3600)
def load_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365) # 10 años exactos
    # Descargamos los datos y limpiamos los nombres
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)
    if 'Adj Close' in data.columns:
        data = data['Adj Close']
    elif 'Close' in data.columns:
        data = data['Close']
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(-1)
    return data

try:
    with st.spinner('Descargando datos históricos verídicos...'):
        df_precios = load_data()
        df_retornos = df_precios.pct_change().dropna()

    # ==========================================
    # 3. INTERFAZ PRINCIPAL
    # ==========================================
    st.markdown("<h1>🏛️ ANÁLISIS ESTRATÉGICO DE ACCIONES BIG TECH</h1>", unsafe_allow_html=True)
    st.caption("Valentina | Proyecto de Administración | Universidad Externado de Colombia")
    st.markdown("---")

    # Selector en barra lateral
    st.sidebar.header("Panel de Control")
    empresa = st.sidebar.selectbox("Seleccione Empresa:", tickers)
    color_actual = colores_empresas.get(empresa)

    # Organización por Pestañas
    tab1, tab2, tab3 = st.tabs(["📈 Histórico (10 años)", "📊 Retornos Diarios", "🎯 KPIs de Desempeño"])

    # ------------------------------------------
    # TAB 1: PRECIOS 10 AÑOS (MULTICOLOR)
    # ------------------------------------------
    with tab1:
        st.subheader(f"Evolución del Precio: {empresa}")
        
        # Gráfico con el color específico de la empresa
        fig_precio = px.line(df_precios, y=empresa, color_discrete_sequence=[color_actual])
        
        # Fondo Negro en el Gráfico
        fig_precio.update_layout(
            plot_bgcolor='#000000', paper_bgcolor='#000000',
            xaxis=dict(showgrid=False, color='#ffffff'),
            yaxis=dict(gridcolor='#333333', color='#ffffff'),
            title_font_color="#ffffff"
        )
        st.plotly_chart(fig_precio, use_container_width=True)
        
        st.info("Este gráfico representa el precio de cierre ajustado de los últimos 10 años, fundamental para entender la valorización histórica corporativa.")

    # ------------------------------------------
    # TAB 2: RETORNOS Y FRECUENCIA
    # ------------------------------------------
    with tab2:
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader(f"Volatilidad Diaria de {empresa}")
            # Usamos un gráfico de área con el color de la empresa pero más suave
            fig_ret = px.area(df_retornos, y=empresa, color_discrete_sequence=[color_actual])
            fig_ret.update_layout(
                plot_bgcolor='#000000', paper_bgcolor='#000000',
                xaxis=dict(showgrid=False, color='#ffffff'),
                yaxis=dict(gridcolor='#333333', color='#ffffff')
            )
            st.plotly_chart(fig_ret, use_container_width=True)
            
        with col2:
            st.markdown(f"<div class='report-card'>", unsafe_allow_html=True)
            st.subheader("Frecuencia de Movimientos")
            
            # Tabla de frecuencia con rangos
            bins = [-1, -0.05, -0.02, 0, 0.02, 0.05, 1]
            labels = ['Caída Crítica', 'Caída Fuerte', 'Leve Neg.', 'Leve Pos.', 'Subida Fuerte', 'Subida Crítica']
            frec = pd.cut(df_retornos[empresa], bins=bins, labels=labels).value_counts().sort_index()
            df_frec = pd.DataFrame({'Rango': frec.index, 'Días': frec.values})
            st.table(df_frec)
            st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 3: KPIs Y COMPARATIVO BARRAS
    # ------------------------------------------
    with tab3:
        st.subheader(f"Métricas de Gestión Gerencial: {empresa}")
        c1, c2, c3 = st.columns(3)
        
        # Cálculos
        rend_total = (df_precios[empresa].iloc[-1] / df_precios[empresa].iloc[0] - 1) * 100
        volatilidad = df_retornos[empresa].std() * (252**0.5) * 100
        ultimo_p = df_precios[empresa].iloc[-1]

        c1.metric("Rendimiento 10A", f"{rend_total:.1f}%")
        c2.metric("Volatilidad Anual", f"{volatilidad:.1f}%")
        c3.metric("Último Precio USD", f"${ultimo_p:.2f}")

        # Gráfico de Barras Comparativo (Multicolor)
        st.markdown("---")
        st.subheader("Comparativo de Crecimiento Total (Todas las Empresas)")
        
        rendimientos_comp = ((df_precios.iloc[-1] / df_precios.iloc[0]) - 1) * 100
        # NOVEDAD: Convertimos el diccionario de colores en una lista para el gráfico de barras
        lista_colores = [colores_empresas.get(tk) for tk in rendimientos_comp.index]
        
        fig_barras = px.bar(rendimientos_comp, 
                            color=rendimientos_comp.index, # Usamos los nombres para asignar colores
                            color_discrete_map=colores_empresas, # Mapeamos los colores que definimos
                            labels={'value': '% de Rendimiento Acumulado', 'index': 'Empresa'})
        
        fig_barras.update_layout(
            plot_bgcolor='#000000', paper_bgcolor='#000000',
            xaxis=dict(showgrid=False, color='#ffffff'),
            yaxis=dict(gridcolor='#333333', color='#ffffff'),
            showlegend=False
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    st.markdown("---")
    st.caption("© 2024 Valentina - Análisis Académico | Universidad Externado de Colombia")

except Exception as e:
    st.error(f"Hubo un problema al cargar los datos financieros. Es posible que el archivo 'requirements.txt' esté incompleto o que haya un fallo temporal de conexión. Error: {e}")
