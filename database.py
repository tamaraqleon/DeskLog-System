from datetime import datetime, timedelta
from supabase import create_client
import streamlit as st
import hashlib 

def get_supabase_client():
    """Crea y retorna la conexión oficial con Supabase usando los secretos de Streamlit."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def _hash(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


@st.cache_data(ttl=60)
def obtener_hash_login():
    """Devuelve el hash de la contraseña de login guardado en Supabase, o None."""
    sb = get_supabase_client()
    res = sb.table("config").select("clave_login_hash").eq("id", 1).limit(1).execute()
    if not res.data:
        return None
    return res.data[0].get("clave_login_hash")


@st.cache_data(ttl=60)
def obtener_hash_reservas():
    """Devuelve el hash de la contraseña de reservas guardado en Supabase, o None."""
    sb = get_supabase_client()
    res = sb.table("config").select("clave_reservas_hash").eq("id", 1).limit(1).execute()
    if not res.data:
        return None
    return res.data[0].get("clave_reservas_hash")


def actualizar_hash_login(nueva_clave: str) -> None:
    """Hashea y guarda la nueva contraseña de login en Supabase."""
    sb = get_supabase_client()
    sb.table("config").update({
        "clave_login_hash": _hash(nueva_clave)
    }).eq("id", 1).execute()
    obtener_hash_login.clear()  


def actualizar_hash_reservas(nueva_clave: str) -> None:
    """Hashea y guarda la nueva contraseña de reservas en Supabase."""
    sb = get_supabase_client()
    sb.table("config").update({
        "clave_reservas_hash": _hash(nueva_clave)
    }).eq("id", 1).execute()
    obtener_hash_reservas.clear()



def init_db():
    """
    Como las tablas 'registros' y 'notas_importantes' ya están creadas 
    y configuradas directamente en la nube de Supabase, 
    esta función queda lista para inicializar o hacer validaciones si lo necesitas.
    """
    supabase = get_supabase_client()
    
    pass