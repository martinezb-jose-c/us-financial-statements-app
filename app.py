import streamlit as st
import pandas as pd
from edgar import set_identity
from stitching_statements import company_statements_to_df

# Configuración de la página
st.set_page_config(
    page_title="Descarga de Estados Financieros de la SEC",
    page_icon="📊",
    layout="wide"
)

# ✅ INICIALIZAR STATE PARA PERSISTENCIA
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "last_ticker" not in st.session_state:
    st.session_state.last_ticker = None
if "last_periods" not in st.session_state:
    st.session_state.last_periods = None
if "last_normalize" not in st.session_state:
    st.session_state.last_normalize = None

# Título
st.title("📊 Descarga de Estados Financieros de la SEC")
st.markdown("""
Descarga y analiza estados financieros consolidados utilizando **XBRL Stitching**.

El stitching combina múltiples reportes 10-K en estados históricamente comparables.
""")

st.markdown("---")

# ✅ SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuración")
    
    email_sec = st.text_input(
        "📧 Correo electrónico",
        placeholder="usuario@ejemplo.com",
        help="Correo requerido por la API de la SEC."
    )
    
    ticker = st.text_input(
        "🔍 Ticker",
        value="AAPL",
        placeholder="AAPL, MSFT, RHI...",
        help="Símbolo bursátil de la empresa"
    ).upper()

    format = st.radio(
        "Informes anuales o trimestrales",
        options=["10-K", "10-Q"]
    )

    num_periods = st.slider(
            "📅 Períodos (años/trimestres)",
            min_value=1,
            max_value=30,
            value=10,
            step=1,
            help="Cantidad de reportes 10-K a descargar"
    )

    normalize_concepts = st.checkbox(
            "🔄 Normalizar",
            value=True,
            help="Consolida variantes de nombres"
    )


# ✅ CONTENIDO PRINCIPAL - TAB 1
st.subheader(f"Estados Financieros Consolidados: {ticker}")

process_button = st.button(
    "⬇️ Procesar Stitching",
    type="primary",
    use_container_width=True
)

st.markdown("---")

# ✅ DETECTAR CAMBIOS
if (st.session_state.last_ticker != ticker or
    st.session_state.last_periods != num_periods or
    st.session_state.last_normalize != normalize_concepts):
    st.session_state.processed_data = None
    st.session_state.last_ticker = ticker
    st.session_state.last_periods = num_periods
    st.session_state.last_normalize = normalize_concepts

# ✅ PROCESAR
if process_button:
    if not ticker:
        st.error("❌ Por favor introduce un ticker válido")
    elif not email_sec:
        st.error("❌ Por favor introduce tu correo")
    else:
        try:
            with st.spinner("🔧 Conectando a SEC API..."):
                set_identity(email_sec)
            
            with st.spinner(f"📥 Descargando {ticker}..."):
                bs_df, is_df, cf_df = company_statements_to_df(
                    ticker,
                    format=format,
                    periods=num_periods,
                    normalize=normalize_concepts
                )
            
            st.session_state.processed_data = {
                "bs_df": bs_df,
                "is_df": is_df,
                "cf_df": cf_df
            }
            
            st.success(f"✅ Datos procesados exitosamente")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("🔍 Detalles"):
                st.code(str(e))

# ✅ MOSTRAR DATOS
if st.session_state.processed_data is not None:
    bs_df = st.session_state.processed_data["bs_df"]
    is_df = st.session_state.processed_data["is_df"]
    cf_df = st.session_state.processed_data["cf_df"]
    
    # Métricas
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    
    with col_info1:
        st.metric("Períodos", len(bs_df.columns))
    with col_info2:
        st.metric("Conceptos (BS)", len(bs_df))
    with col_info3:
        st.metric("Conceptos (IS)", len(is_df))
    with col_info4:
        st.metric("Conceptos (CF)", len(cf_df))
    
    st.markdown("---")
    
    # Vistas previas
    st.subheader("👀 Vista Previa de Datos")
    
    tab1_view, tab2_view, tab3_view = st.tabs([
        f"📊 Estado de Resultados ({len(is_df)} filas)",
        f"📋 Balance General ({len(bs_df)} filas)",
        f"💰 Flujo de Efectivo ({len(cf_df)} filas)"
    ])
    
    with tab1_view:
        st.dataframe(is_df, use_container_width=True, height=500)
    with tab2_view:
        st.dataframe(bs_df, use_container_width=True, height=500)
    with tab3_view:
        st.dataframe(cf_df, use_container_width=True, height=500)
    
    st.markdown("---")
    
    # Descargas
    st.subheader("💾 Descargar CSV")
    
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        csv_is = is_df.to_csv(index=True)
        suffix = "_normalized" if st.session_state.last_normalize else ""
        st.download_button(
            label="📄 Estado de Resultados",
            data=csv_is,
            file_name=f"IncomeStatement_{ticker}{suffix}.csv",
            mime="text/csv",
            use_container_width=True,
            key="is_download"
        )
    
    with col_dl2:
        csv_bs = bs_df.to_csv(index=True)
        st.download_button(
            label="📄 Balance General",
            data=csv_bs,
            file_name=f"BalanceSheet_{ticker}{suffix}.csv",
            mime="text/csv",
            use_container_width=True,
            key="bs_download"
        )
    
    with col_dl3:
        csv_cf = cf_df.to_csv(index=True)
        st.download_button(
            label="📄 Flujo de Efectivo",
            data=csv_cf,
            file_name=f"CashFlowStatement_{ticker}{suffix}.csv",
            mime="text/csv",
            use_container_width=True,
            key="cf_download"
        )
else:
    st.info("""
    📌 **Pasos:**
    
    1. Configura ticker y correo en el sidebar
    2. Selecciona períodos
    3. Haz clic en **⬇️ Procesar Stitching**
    4. Descarga los CSV
    """)

st.markdown("---")
st.caption("🔗 SEC API - XBRL Stitching")
