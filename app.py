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

# Contraseña genérica por defecto para el repositorio público
CLAVE_DEFAULT_HASH = hashlib.sha256("tu_contrasena_aqui".encode()).hexdigest()

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DeskLog System", layout="wide")

# --- TRUCO CSS PARA OCULTAR EL TEXTO DE AYUDA EN FORMULARIOS ---
st.markdown("""
    <style>
    div[data-testid="stForm"] div[data-baseweb="input"] ~ div,
    div[data-testid="stForm"] div[data-baseweb="textarea"] ~ div,
    div[data-testid="stForm"] small,
    div[data-testid="stForm"] div[class*="instructions"],
    div[data-testid="stForm"] span[class*="instruction"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ESTADO DE SESIÓN (LOGIN)
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

# PANTALLA DE ACCESO (LOGIN)
if not st.session_state.autenticado:
  st.title("Access Control")

  with st.form("form_login"):
    password_ingresada = st.text_input("Password:", type="password")
    ingresar = st.form_submit_button("Login")

    if ingresar:
      hash_ingresado = hashlib.sha256(password_ingresada.encode()).hexdigest()
      if hash_ingresado == CLAVE_DEFAULT_HASH:
        st.session_state.autenticado = True
        st.rerun()
      else:
        st.error("Access Denied")

# ------------------------------------------
# PANATALLA INICIAL 
# ------------------------------------------
else:
  if "menu_seleccionado" not in st.session_state:
    st.session_state.menu_seleccionado = "Inicio"

  # El menú lateral SOLO se dibuja si NO estamos en la pantalla de inicio
  if st.session_state.menu_seleccionado != "Inicio":
    st.sidebar.title("Menu de Navegacion")
    
    opciones_disponibles = ["Inicio", "Registro de Turnos", "Buscar en el Histórico", "Vista Cuaderno", "Notas", "Papelera"]
    current_index = opciones_disponibles.index(st.session_state.menu_seleccionado) if st.session_state.menu_seleccionado in opciones_disponibles else 0

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