import streamlit as st
from typing import Optional, Dict, Any, Tuple
from database import get_supabase_client

MAX_TEMAS = 3

DEFAULT_THEME = {
    "id": None,
    "nombre": "Default",
    "primary_color": "#8B5CF6",
    "hover": "#7C3AED",
    "background": "#FFFFFF",
    "text_color": "#31333F",
    "secondary_background": "#F0F2F6",
}


from typing import Optional

def _normalizar(tema: Optional[dict]) -> dict:
    """Garantiza que el dict tenga TODAS las claves que aplicar_tema espera."""
    if not tema:
        return dict(DEFAULT_THEME)
    return {
        "id": tema.get("id"),
        "nombre": tema.get("nombre") or "Sin nombre",
        "primary_color": tema.get("primary_color") or DEFAULT_THEME["primary_color"],
        "hover": tema.get("hover") or DEFAULT_THEME["hover"],
        "background": tema.get("background") or DEFAULT_THEME["background"],
        "text_color": tema.get("text_color") or DEFAULT_THEME["text_color"],
        "secondary_background": tema.get("secondary_background") or DEFAULT_THEME["secondary_background"],
    }


# ------------------------------------------------------------------
# Lectura
# ------------------------------------------------------------------
def listar_temas() -> list[dict]:
    sb = get_supabase_client()
    res = sb.table("temas").select("*").order("created_at").execute()
    return [_normalizar(t) for t in (res.data or [])]


def obtener_tema_por_id(tema_id) -> Optional[Dict[str, Any]]:
    if not tema_id:
        return None
    sb = get_supabase_client()
    res = sb.table("temas").select("*").eq("id", tema_id).limit(1).execute()
    return _normalizar(res.data[0]) if res.data else None


def obtener_tema_activo() -> Optional[Dict[str, Any]]:
    sb = get_supabase_client()
    res = sb.table("temas").select("*").eq("is_active", True).limit(1).execute()
    return _normalizar(res.data[0]) if res.data else None


# ------------------------------------------------------------------
# Escritura
# ------------------------------------------------------------------
def guardar_tema(nombre: str, primary: str, hover: str, background: str,
                 text: str, secondary_background: str) -> Tuple[bool, str]:
    sb = get_supabase_client()
    if len(listar_temas()) >= MAX_TEMAS:
        return False, f"Ya tienes {MAX_TEMAS} temas (máximo). Borra uno antes."
    try:
        sb.table("temas").insert({
            "nombre": nombre,
            "primary_color": primary,
            "hover": hover,
            "background": background,
            "text_color": text,
            "secondary_background": secondary_background,
            "is_active": False,
        }).execute()
        return True, "Tema guardado correctamente."
    except Exception as e:
        return False, f"Error al guardar: {e}"


def borrar_tema(tema_id) -> None:
    sb = get_supabase_client()

    # ¿Es el tema activo en la URL?
    era_activo = str(st.query_params.get("tema", "")) == str(tema_id)

    # Borrar la fila
    sb.table("temas").delete().eq("id", tema_id).execute()

    # Si era el activo, limpiar query param y session_state
    if era_activo:
        if "tema" in st.query_params:
            del st.query_params["tema"]
        st.session_state.pop("tema_activo", None)


def set_tema_activo(tema_id: Optional[str]) -> None:
    sb = get_supabase_client()
    # Desmarcar solo los que están activos (filtro válido sobre boolean)
    sb.table("temas").update({"is_active": False}).eq("is_active", True).execute()
    if tema_id:
        sb.table("temas").update({"is_active": True}).eq("id", tema_id).execute()
        st.query_params["tema"] = str(tema_id)
    else:
        if "tema" in st.query_params:
            del st.query_params["tema"]


# ------------------------------------------------------------------
# Resolución + aplicación
# ------------------------------------------------------------------
def resolver_tema_activo() -> dict:
    if "tema_activo" in st.session_state:
        return st.session_state["tema_activo"]

    tema = None
    tema_id_url = st.query_params.get("tema")
    if tema_id_url:
        try:
            tema = obtener_tema_por_id(int(tema_id_url))
        except (ValueError, TypeError):
            tema = None
    if tema is None:
        tema = obtener_tema_activo()
    if tema is None:
        tema = dict(DEFAULT_THEME)

    st.session_state["tema_activo"] = tema
    return tema


def aplicar_tema(tema: dict) -> None:
    tema = _normalizar(tema)
    primary = tema["primary_color"]
    hover = tema["hover"]
    background = tema["background"]
    text = tema["text_color"]
    secondary_bg = tema["secondary_background"]

    st.markdown(f"""
        <style>
        /* ============================================================
           FONDO GENERAL Y TEXTO
           ============================================================ */
        div[data-testid="stApp"],
        div[data-testid="stAppViewContainer"],
        div[data-testid="stMain"] {{
            background-color: {background} !important;
            color: {text} !important;
        }}

        div[data-testid="stMarkdownContainer"],
        h1, h2, h3, h4, h5, h6, p, label, span, li, small {{
            color: {text} !important;
        }}

        /* ============================================================
           SIDEBAR
           ============================================================ */
        div[data-testid="stSidebar"],
        div[data-testid="stSidebar"] > div,
        div[data-testid="stSidebarContent"],
        div[data-testid="stSidebarUserContent"],
        div[data-testid="stSidebarHeader"] {{
            background-color: {secondary_bg} !important;
        }}

        /* ============================================================
           INPUTS, TEXTAREAS, SELECTBOX
           ============================================================ */
        div[data-baseweb="input"],
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"],
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="base-input"] {{
            background-color: {background} !important;
            color: {text} !important;
        }}

        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {{
            background-color: {background} !important;
            color: {text} !important;
        }}

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="textarea"]:focus-within {{
            border-color: {primary} !important;
            box-shadow: 0 0 0 1px {primary} !important;
        }}

        /* Selectbox cerrado */
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div > div,
        div[data-baseweb="select"] div[role="button"] {{
            background-color: {background} !important;
            color: {text} !important;
            border-color: {primary} !important;
        }}

        /* Lista desplegable abierta (popup) */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        div[data-baseweb="menu"],
        ul[role="listbox"],
        li[role="option"] {{
            background-color: {background} !important;
            color: {text} !important;
        }}

        /* Hover del desplegable */
        div[data-baseweb="popover"] li:hover,
        ul[role="listbox"] li[role="option"]:hover {{
            background-color: {primary} !important;
        }}
        div[data-baseweb="popover"] li:hover *,
        ul[role="listbox"] li[role="option"]:hover * {{
            color: #FFFFFF !important;
            background-color: transparent !important;
        }}

        /* Ítem seleccionado del desplegable */
        li[role="option"][aria-selected="true"],
        div[data-baseweb="popover"] li[aria-selected="true"] {{
            background-color: {primary} !important;
        }}
        li[role="option"][aria-selected="true"] *,
        div[data-baseweb="popover"] li[aria-selected="true"] * {{
            color: #FFFFFF !important;
            background-color: transparent !important;
        }}

        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        div[data-baseweb="textarea"],
        div[data-baseweb="select"] > div {{
            border: 1px solid {primary} !important;
        }} 

        /* ============================================================
           BOTONES
           ============================================================ */
           
        /* SECONDARY BTTONS */

        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-secondaryFormSubmit"] {{
            background-color: {background} !important;
            border-color: {primary} !important;
            color: {primary} !important;
            transition: all 0.15s ease !important;
        }}

        button[data-testid="stBaseButton-secondary"] *,
        button[data-testid="stBaseButton-secondaryFormSubmit"] * {{
            background-color: transparent !important;
            color: {primary} !important;
        }}

        button[data-testid="stBaseButton-secondary"]:hover,
        button[data-testid="stBaseButton-secondaryFormSubmit"]:hover {{
            border-color: {hover} !important;
            background-color: {hover} !important;
        }}

        button[data-testid="stBaseButton-secondary"]:hover *,
        button[data-testid="stBaseButton-secondaryFormSubmit"]:hover * {{
            color: #FFFFFF !important;
            background-color: transparent !important;
        }}

        /* PRIMARY */
        
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-primaryFormSubmit"] {{
            background-color: {primary} !important;
            border-color: {primary} !important;
        }}

        button[data-testid="stBaseButton-primary"] *,
        button[data-testid="stBaseButton-primaryFormSubmit"] * {{
            background-color: transparent !important;
            color: #FFFFFF !important;
        }}

        button[data-testid="stBaseButton-primary"]:hover,
        button[data-testid="stBaseButton-primaryFormSubmit"]:hover {{
            background-color: {hover} !important;
            border-color: {hover} !important;
        }}

        button[data-testid="stBaseButton-primary"]:hover *,
        button[data-testid="stBaseButton-primaryFormSubmit"]:hover * {{
            color: #FFFFFF !important;
            background-color: transparent !important;
        }}


        /* ============================================================
           TARJETAS CON BORDE (st.container(border=True))
           ============================================================ */
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background-color: {background} !important;
            border-color: {primary} !important;
        }}

        /* ============================================================
           EXPANDERS (st.expander)
           ============================================================ */
        details,
        details > summary,
        div[data-testid="stExpander"],
        div[data-testid="stExpander"] > details,
        div[data-testid="stExpander"] > details > summary {{
            background-color: {background} !important;
            color: {text} !important;
            border-color: {primary} !important;
        }}

        details > summary:hover {{
            background-color: color-mix(in srgb, {primary} 15%, {background}) !important;
        }}

        /* Contenido interno del expander */
        div[data-testid="stExpander"] details > div {{
            background-color: {background} !important;
        }}

        /* ============================================================
           DIVISORES
           ============================================================ */
        hr,
        div[data-testid="stDivider"] {{
            border-color: {primary} !important;
            background-color: {primary} !important;
        }}
       
        button[data-testid="stBaseButton-secondary"] *,
        button[data-testid="stBaseButton-secondaryFormSubmit"] * {{
            color: {primary} !important;
            background-color: transparent !important;
        }}
        /* Hover de las tarjetas (login y containers con borde) */
        div[data-testid="stVerticalBlock"][data-test-wrap="false"],
        div[data-testid="stVerticalBlock"][data-test-scroll-behavior="normal"],
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            height: 100% !important;
            border-radius: 14px !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stVerticalBlock"][data-test-wrap="false"]:hover,
        div[data-testid="stVerticalBlock"][data-test-scroll-behavior="normal"]:hover,
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            border-color: {primary} !important;
            box-shadow: 0 6px 16px color-mix(in srgb, {primary} 30%, transparent) !important;
            transform: translateY(-3px) !important;
        }}
        
        label[data-baseweb="radio"] > div:first-child {{
            background-color: {primary} !important;
            border: 2px solid {primary} !important;
        }}
        
        label[data-baseweb="radio"]:not(:has(input:checked)) > div:first-child {{
            background-color: transparent !important;
            border: 2px solid {text} !important;
        }}

        label[data-baseweb="radio"]:has(input:checked) > div:first-child {{
            background-color: {primary} !important;
            border: 3px solid {primary} !important;
        }}

        /* === CALENDARIO (versión nuclear) === */

        /* Fondo general del popover del datepicker */
        div[data-baseweb="popover"]:has(div[data-baseweb="calendar"]),
        div[data-baseweb="popover"]:has(div[data-baseweb="calendar"]) > div {{
            background-color: {background} !important;
            color: {text} !important;
        }}

        /* Todo dentro del calendario */
        div[data-baseweb="calendar"],
        div[data-baseweb="calendar"] *,
        div[data-baseweb="calendar"] *::before,
        div[data-baseweb="calendar"] *::after {{
            background-color: {background} !important;
            color: {text} !important;
        }}

        /* Día seleccionado y hover: repintar por encima */
        div[data-baseweb="calendar"] *[aria-label^="Selected"],
        div[data-baseweb="calendar"] *[aria-label^="Selected"]::before,
        div[data-baseweb="calendar"] *[aria-label^="Selected"]::after,
        div[data-baseweb="calendar"] *[aria-label^="Selected"] > div {{
            background-color: {primary} !important;
            color: #FFFFFF !important;
            border-color: {primary} !important;
        }}

        div[data-baseweb="calendar"] div[role="gridcell"]:hover,
        div[data-baseweb="calendar"] div[role="gridcell"]:hover::before,
        div[data-baseweb="calendar"] div[role="gridcell"]:hover::after,
        div[data-baseweb="calendar"] div[role="gridcell"]:hover > div {{
            background-color: {primary} !important;
            color: #FFFFFF !important;
            border-color: {primary} !important;
            border-radius: 50% !important;
        }}

        /* Día seleccionado */
        div[data-baseweb="calendar"] *[aria-label^="Selected"],
        div[data-baseweb="calendar"] *[aria-label^="Selected"]::before,
        div[data-baseweb="calendar"] *[aria-label^="Selected"]::after,
        div[data-baseweb="calendar"] *[aria-label^="Selected"] > div {{
            background-color: {primary} !important;
            border-color: {primary} !important;
            color: #FFFFFF !important;
        }}

        /* Hover de días */
        div[data-baseweb="calendar"] div[role="gridcell"]:hover,
        div[data-baseweb="calendar"] div[role="gridcell"]:hover::before,
        div[data-baseweb="calendar"] div[role="gridcell"]:hover::after,
        div[data-baseweb="calendar"] div[role="gridcell"]:hover > div {{
            background-color: {primary} !important;
            color: #FFFFFF !important;
            border-color: {primary} !important;
            border-radius: 50% !important;
        }}

        /* Aro exterior del día seleccionado */
        div[data-baseweb="calendar"] div[role="gridcell"][aria-label^="Selected"] {{
            background-color: {primary} !important;
            border: none !important;
            border-radius: 50% !important;
        }}

        /* Botones del number input */
        div[data-testid="stNumberInput"] button,
        div[data-testid="stNumberInput"] button *,
        div[data-testid="stNumberInput"] button:hover,
        div[data-testid="stNumberInput"] button:hover * {{
            background-color: {primary} !important;
            border-color: {primary} !important;
            color: #FFFFFF !important;
        }}

        div[data-testid="stNumberInput"] button:hover,
        div[data-testid="stNumberInput"] button:hover * {{
            background-color: {hover} !important;
            border-color: {hover} !important;
        }}

        /* El ícono dentro del botón */
        div[data-testid="stNumberInput"] button svg,
        div[data-testid="stNumberInput"] button svg path {{
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }}

        /* Botón del popover: círculo con color del tema */
        div[data-testid="stPopover"] button {{
            width: 44px !important;
            height: 44px !important;
            min-height: 44px !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 50% !important;
            border: 3px solid {primary} !important;
            background-color: {primary} !important;
            box-shadow: 0 4px 12px color-mix(in srgb, {primary} 40%, transparent) !important;
            position: relative !important;
        }}

        div[data-testid="stPopover"] button:hover {{
            background-color: {hover} !important;
            border-color: {hover} !important;
        }}

        /* Ocultar TODO el contenido interno del botón */
        div[data-testid="stPopover"] button > * {{
            display: none !important;
        }}

        /* Ícono propio, centrado absoluto */
        div[data-testid="stPopover"] button::after {{
            content: "⚙" !important;
            font-size: 20px !important;
            color: #FFFFFF !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            line-height: 1 !important;
        }}

        /* Input de fecha (date picker) */
        div[data-testid="stDateInput"] div[data-baseweb="input"],
        div[data-testid="stDateInput"] div[data-baseweb="base-input"] {{
            background-color: {background} !important;
            border: 1px solid {primary} !important;
        }}

        div[data-testid="stDateInput"] div[data-baseweb="input"]:focus-within,
        div[data-testid="stDateInput"] div[data-baseweb="base-input"]:focus-within {{
            border-color: {primary} !important;
            box-shadow: 0 0 0 1px {primary} !important;
        }}

        div[data-testid="stDateInput"] input {{
            background-color: {background} !important;
            color: {text} !important;
        }}

        </style>
    """, unsafe_allow_html=True)


def cambiar_tema(tema_id: Optional[str]) -> None:
    set_tema_activo(tema_id)
    if tema_id:
        st.session_state["tema_activo"] = obtener_tema_por_id(tema_id) or dict(DEFAULT_THEME)
    else:
        st.session_state["tema_activo"] = dict(DEFAULT_THEME)
    st.rerun()