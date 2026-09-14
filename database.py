from datetime import datetime, timedelta
from supabase import create_client
import streamlit as st

def get_supabase_client():
    """Crea y retorna la conexión oficial con Supabase usando los secretos de Streamlit."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def init_db():
    """
    Como las tablas 'registros' y 'notas_importantes' ya están creadas 
    y configuradas directamente en la nube de Supabase, 
    esta función queda lista para inicializar o hacer validaciones si lo necesitas.
    """
    supabase = get_supabase_client()
    
    # Opcional: Aquí podrías agregar lógica de limpieza si la requieres, 
    # pero la estructura principal ya vive segura en Supabase.
    pass