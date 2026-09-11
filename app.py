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

else:
  # APLICACIÓN PRINCIPAL
  st.sidebar.title("Menú de Navegación")
  opcion = st.sidebar.radio(
      "Seleccione una opción:",
      ["Inicio", "Registro de Turnos", "Buscar en el Histórico", "Vista Cuaderno", "Notas", "Papelera"],
  )

  if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

  # Enrutador de vistas limpio
  if opcion == "Inicio":
    render_bienvenida()
  elif opcion == "Registro de Turnos":
    render_registro_turnos()
  elif opcion == "Buscar en el Histórico":
    render_buscador()
  elif opcion == "Vista Cuaderno":
    render_cuaderno()
  elif opcion == "Notas":
    render_notas()
  elif opcion == "Papelera":
    render_papelera()