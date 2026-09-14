import sqlite3
from database import get_supabase_client

supabase = get_supabase_client()

print("Conectando a la base de datos local (bitacora_recepcion.db)...")
try:
    conn = sqlite3.connect("bitacora_recepcion.db")
    cursor = conn.cursor()
except Exception as e:
    print(f"Error al abrir la base de datos local: {e}")
    exit()

# 1. Migrar registros de la bitácora
try:
    cursor.execute("SELECT fecha, hora, suceso, nota, estado, fecha_eliminacion FROM registros")
    registros_antiguos = cursor.fetchall()
    
    count_reg = 0
    for reg in registros_antiguos:
        supabase.table("registros").insert({
            "fecha": reg[0],
            "hora": reg[1],
            "suceso": reg[2],
            "nota": reg[3],
            "estado": reg[4] or "activo",
            "fecha_eliminacion": reg[5]
        }).execute()
        count_reg += 1
    print(f"¡Éxito! Se migraron {count_reg} registros de la bitácora a Supabase.")
except Exception as e:
    print(f"Nota en registros (quizás ya estaban o tabla vacía): {e}")

# 2. Migrar notas importantes
try:
    cursor.execute("SELECT titulo, contenido, estado, fecha_eliminacion FROM notas_importantes")
    notas_antiguas = cursor.fetchall()
    
    count_not = 0
    for nota in notas_antiguas:
        supabase.table("notas_importantes").insert({
            "titulo": nota[0],
            "contenido": nota[1],
            "estado": nota[2] or "activo",
            "fecha_eliminacion": nota[3]
        }).execute()
        count_not += 1
    print(f"¡Éxito! Se migraron {count_not} notas importantes a Supabase.")
except Exception as e:
    print(f"Nota en notas (quizás ya estaban o tabla vacía): {e}")

conn.close()
print("¡Migración completada con éxito!")