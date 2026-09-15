import hashlib
import streamlit as st
from database import init_db
from views import (
    render_registro_turnos,
    render_buscador,
    render_cuaderno,
    render_notas,
    render_papelera,
    render_bienvenida,
)

# Inicializar Base de Datos
init_db()

# Contraseña
CLAVE_RCPN_HASH = hashlib.sha256("RCPN26".encode()).hexdigest()

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Bitácora de Recepción", layout="wide")

# --- CSS: ocultar ayuda de formularios + tarjetas parejas con hover ---
st.markdown("""
    <style>
    div[data-testid="stForm"] div[data-baseweb="input"] ~ div,
    div[data-testid="stForm"] div[data-baseweb="textarea"] ~ div,
    div[data-testid="stForm"] small,
    div[data-testid="stForm"] div[class*="instructions"],
    div[data-testid="stForm"] span[class*="instruction"] {
        display: none !important;
    }

    /* Igualar altura de las columnas */
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }
    div[data-testid="stColumn"] {
        display: flex !important;
    }
    div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
        width: 100% !important;
        height: 100% !important;
    }
    div[data-testid="stColumn"] div[data-testid="stLayoutWrapper"] {
        height: 100% !important;
    }

    /* La tarjeta con borde (container(border=True)) - varios nombres según versión de Streamlit */
    div[data-testid="stVerticalBlock"][data-test-wrap="false"],
    div[data-testid="stVerticalBlock"][data-test-scroll-behavior="normal"],
    div[data-testid="stVerticalBlockBorderWrapper"] {
        height: 100% !important;
        border-radius: 14px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    div[data-testid="stVerticalBlock"][data-test-wrap="false"]:hover,
    div[data-testid="stVerticalBlock"][data-test-scroll-behavior="normal"]:hover,
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #8B5CF6 !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.25) !important;
        transform: translateY(-3px) !important;
    }

    /* Alinear el botón "Entrar como Observador" con el campo de contraseña */
    .st-key-btn_observador {
        margin-top: -13.6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ESTADO DE SESIÓN (LOGIN Y ROLES)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "role" not in st.session_state:
    st.session_state.role = None

# PANTALLA DE ACCESO (LOGIN / SELECCIÓN DE ROL)
if not st.session_state.autenticado:
    st.title("Seleccione el modo de ingreso")
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Soy Recepcionista")
            with st.form("form_login", border=False):
                password_ingresada = st.text_input("Contraseña:", type="password")
                ingresar = st.form_submit_button("Ingresar")

            if ingresar:
                hash_ingresado = hashlib.sha256(password_ingresada.encode()).hexdigest()
                if hash_ingresado == CLAVE_RCPN_HASH:
                    st.session_state.autenticado = True
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("Oh, oh...")

    with col2:
        with st.container(border=True):
            st.subheader("Soy Observador")
            st.markdown("Visualizacion de registros y notas en modo lectura.")
            if st.button("Entrar como Observador", key="btn_observador"):
                st.session_state.autenticado = True
                st.session_state.role = "observer"
                st.rerun()

# ------------------------------------------
# PANTALLA INICIAL
# ------------------------------------------
else:
    if "menu_seleccionado" not in st.session_state:
        st.session_state.menu_seleccionado = "Inicio"

    if st.session_state.menu_seleccionado != "Inicio":
        st.sidebar.title("Menu de Navegacion")
        
        # Filtrar opciones según el rol
        if st.session_state.role == "observer":
            opciones_disponibles = ["Inicio", "Buscar en el Histórico", "Vista Cuaderno"]
        else:
            opciones_disponibles = ["Inicio", "Registro de Turnos", "Buscar en el Histórico", "Vista Cuaderno", "Notas", "Papelera"]

        # Si por alguna razón la sesión quedó con una opción prohibida, lo devolvemos a Inicio
        if st.session_state.menu_seleccionado not in opciones_disponibles:
            st.session_state.menu_seleccionado = "Inicio"
            st.rerun()

        current_index = opciones_disponibles.index(st.session_state.menu_seleccionado)

        opcion = st.sidebar.radio(
            "Seleccione una opcion:",
            opciones_disponibles,
            index=current_index,
            key="radio_menu_lateral"
        )

        if opcion != st.session_state.menu_seleccionado:
            st.session_state.menu_seleccionado = opcion
            st.rerun()

        if st.sidebar.button("Cerrar Sesion"):
            st.session_state.autenticado = False
            st.session_state.role = None
            st.session_state.menu_seleccionado = "Inicio"
            st.rerun()

    # Enrutador de vistas
    if st.session_state.menu_seleccionado == "Inicio":
        render_bienvenida()
    elif st.session_state.menu_seleccionado == "Registro de Turnos":
        render_registro_turnos()
    elif st.session_state.menu_seleccionado == "Buscar en el Histórico":
        render_buscador()
    elif st.session_state.menu_seleccionado == "Vista Cuaderno":
        render_cuaderno()
    elif st.session_state.menu_seleccionado == "Notas":
        render_notas()
    elif st.session_state.menu_seleccionado == "Papelera":
        render_papelera()