import hashlib
import streamlit as st
from database import (
    init_db,
    obtener_hash_login,
    obtener_hash_reservas,
    actualizar_hash_login,
)
from views import (
    render_registro_turnos,
    render_buscador,
    render_cuaderno,
    render_notas,
    render_papelera,
    render_bienvenida,
)
from theme_manager import (
    resolver_tema_activo,
    aplicar_tema,
    listar_temas,
    guardar_tema,
    borrar_tema,
    cambiar_tema,
    MAX_TEMAS,
    DEFAULT_THEME,
)

# Inicializar Base de Datos
init_db()

# Clave de login: primero busca en Supabase, si no hay usa la de secrets como fallback
_hash_supabase = obtener_hash_login()
if _hash_supabase:
    CLAVE_RCPN_HASH = _hash_supabase
else:
    clave_guardada = st.secrets["CLAVE_RCPN"]
    CLAVE_RCPN_HASH = hashlib.sha256(clave_guardada.encode()).hexdigest()

# Clave de reservas: primero busca en Supabase, si no hay usa la de secrets como fallback
_hash_reservas_supabase = obtener_hash_reservas()
if _hash_reservas_supabase:
    CLAVE_RESERVAS_HASH = _hash_reservas_supabase
else:
    clave_reservas = st.secrets["CLAVE_RESERVAS"]
    CLAVE_RESERVAS_HASH = hashlib.sha256(clave_reservas.encode()).hexdigest()

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Bitácora de Recepción", layout="wide", initial_sidebar_state="collapsed")

# Aplicar tema activo (antes de dibujar cualquier widget)
tema_activo = resolver_tema_activo()
aplicar_tema(tema_activo)

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

    div[data-testid="stHorizontalBlock"] { align-items: stretch !important; }
    div[data-testid="stColumn"] { display: flex !important; }
    div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
        width: 100% !important;
        height: 100% !important;
    }
    div[data-testid="stColumn"] div[data-testid="stLayoutWrapper"] {
        height: 100% !important;
    }

    .st-key-btn_observador { margin-top: -13.6px !important; }

        div[data-testid="stSidebar"] .st-key-btn_toggle_temas button {
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        font-size: 20px !important;
        border-radius: 50% !important;
    }
        /* Botón 🎨 flotante en la esquina superior derecha */
    div[data-testid="stPopover"] {
        position: fixed !important;
        top: 70px !important;
        right: 20px !important;
        z-index: 9999 !important;
        width: auto !important;
    }
    div[data-testid="stPopover"] > button {
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        font-size: 22px !important;
        border-radius: 50% !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }

    .st-key-btn_olvide_form button {
        background: none !important;
        border: none !important;
        padding: 0 !important;
        color: inherit !important;
        text-decoration: underline !important;
        font-size: 0.85em !important;
        box-shadow: none !important;
    }
    .st-key-btn_olvide_form button:hover {
        background: none !important;
        border: none !important;
        opacity: 0.7 !important;
    }
    .st-key-btn_olvide_form button p {
        color: inherit !important;
        text-decoration: underline !important;
    }

    .st-key-btn_olvide_form button:hover,
    .st-key-btn_olvide_form button:focus,
    .st-key-btn_olvide_form button:active {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    .st-key-btn_olvide_form button:hover p,
    .st-key-btn_olvide_form button:focus p,
    .st-key-btn_olvide_form button:active p {
        color: inherit !important;
        text-decoration: underline !important;
    }

    </style>
""", unsafe_allow_html=True)

# ESTADO DE SESIÓN (LOGIN Y ROLES)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "role" not in st.session_state:
    st.session_state.role = None
if "mostrar_recuperacion" not in st.session_state:
    st.session_state.mostrar_recuperacion = False

# PANTALLA DE ACCESO (LOGIN / SELECCIÓN DE ROL)
if not st.session_state.autenticado:
    st.title("Seleccione el modo de ingreso")
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Soy Recepcionista")

            if not st.session_state.get("mostrar_recuperacion", False):
                with st.form("form_login", border=False):
                    password_ingresada = st.text_input("Contraseña:", type="password")
                    col_a, col_b = st.columns([3, 2])
                    with col_a:
                        ingresar = st.form_submit_button("Ingresar")
                    with col_b:
                        olvide = st.form_submit_button("¿Olvidaste tu contraseña?", key="btn_olvide_form")

                if ingresar:
                    hash_ingresado = hashlib.sha256(password_ingresada.encode()).hexdigest()
                    if hash_ingresado == CLAVE_RCPN_HASH:
                        st.session_state.autenticado = True
                        st.session_state.role = "admin"
                        st.rerun()
                    else:
                        st.error("Oh, oh...")

                if olvide:
                    st.session_state.mostrar_recuperacion = True
                    st.rerun()
            else:
                with st.form("form_recuperacion", border=False):
                    st.markdown("**Recuperar contraseña**")
                    st.caption("Ingresá la contraseña de reservas para verificar tu identidad.")
                    reservas = st.text_input("Contraseña de reservas:", type="password", key="rec_reservas")
                    nueva = st.text_input("Nueva contraseña:", type="password", key="rec_nueva")
                    confirma = st.text_input("Confirmar nueva contraseña:", type="password", key="rec_confirma")
                    enviar = st.form_submit_button("Cambiar contraseña")

                if enviar:
                    hash_reservas_ingresada = hashlib.sha256(reservas.encode()).hexdigest()
                    if hash_reservas_ingresada != CLAVE_RESERVAS_HASH:
                        st.error("Contraseña de reservas incorrecta.")
                    elif not nueva or len(nueva) < 6:
                        st.warning("La nueva contraseña debe tener al menos 6 caracteres.")
                    elif nueva != confirma:
                        st.error("Las contraseñas nuevas no coinciden.")
                    else:
                        actualizar_hash_login(nueva)
                        st.success("¡Contraseña cambiada con éxito! Ya podés iniciar sesión.")
                        st.session_state.mostrar_recuperacion = False
                        st.rerun()

                if st.button("Cancelar", key="btn_cancelar_rec"):
                    st.session_state.mostrar_recuperacion = False
                    st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("Soy Observador")
            st.markdown("Visualizacion de registros y notas en modo lectura.")
            if st.button("Entrar como Observador", key="btn_observador"):
                st.session_state.autenticado = True
                st.session_state.role = "observer"
                st.rerun()

# ------------------------------------------
# PANTALLA INICIAL (usuario autenticado)
# ------------------------------------------
else:
    if "menu_seleccionado" not in st.session_state:
        st.session_state.menu_seleccionado = "Inicio"

    # --- MENÚ DE NAVEGACIÓN ---
    if st.session_state.menu_seleccionado != "Inicio":
        st.sidebar.title("Menu de Navegacion")

        if st.session_state.role == "observer":
            opciones_disponibles = ["Inicio", "Buscar en el Histórico", "Vista Cuaderno"]
        else:
            opciones_disponibles = ["Inicio", "Registro de Turnos", "Buscar en el Histórico",
                                    "Vista Cuaderno", "Notas", "Papelera"]

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
            st.session_state.pop("tema_activo", None)
            st.rerun()

        # --- 🎨 PERSONALIZACIÓN DE TEMAS (popover flotante) ---
    with st.popover(" ", use_container_width=False):
        temas = listar_temas()
        opciones = {"Default": None} | {t["nombre"]: t["id"] for t in temas}

        tema_actual = st.session_state.get("tema_activo", DEFAULT_THEME)
        nombre_actual = tema_actual.get("nombre", "Default")
        keys = list(opciones.keys())
        idx_actual = keys.index(nombre_actual) if nombre_actual in keys else 0

        seleccion = st.selectbox("Tema activo", options=keys, index=idx_actual,
                                 key="selector_tema")

        if opciones[seleccion] != tema_actual.get("id"):
            cambiar_tema(opciones[seleccion])

        st.divider()

        with st.expander(f"➕ Crear nuevo tema ({len(temas)}/{MAX_TEMAS})"):
            if len(temas) >= MAX_TEMAS:
                st.warning(f"Máximo {MAX_TEMAS} temas. Borra uno para crear otro.")
            else:
                nombre = st.text_input("Nombre del tema", key="nuevo_tema_nombre")
                c1, c2 = st.columns(2)
                with c1:
                    primary = st.color_picker("Color principal", "#8B5CF6")
                    background = st.color_picker("Fondo", "#FFFFFF")
                    secondary_bg = st.color_picker("Fondo secundario / sidebar", "#F0F2F6")
                with c2:
                    hover = st.color_picker("Color hover", "#7C3AED")
                    text = st.color_picker("Texto", "#31333F")
                if st.button("Guardar tema", disabled=not nombre, key="btn_guardar_tema"):
                    ok, msg = guardar_tema(nombre, primary, hover, background, text, secondary_bg)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        if temas:
            with st.expander("🗑️ Borrar un tema"):
                tema_a_borrar = st.selectbox("Elegir tema",
                                             [t["nombre"] for t in temas],
                                             key="tema_borrar_sel")
                if st.button("Borrar este tema", type="primary", key="btn_borrar_tema"):
                    tema_id = next(t["id"] for t in temas if t["nombre"] == tema_a_borrar)
                    borrar_tema(tema_id)
                    st.session_state.pop("tema_activo", None)
                    st.rerun()

    # --- ENRUTADOR DE VISTAS ---
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