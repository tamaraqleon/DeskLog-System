from datetime import datetime, timedelta
import sqlite3

def init_db():
  conn = sqlite3.connect("bitacora_recepcion.db")
  cursor = conn.cursor()

  # Crear tablas base si no existen
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            suceso TEXT,
            nota TEXT
        )
    """)
  
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas_importantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            contenido TEXT
        )
    """)
  conn.commit()

  # Asegurar columnas de estado y fecha de eliminación en registros
  cursor.execute("PRAGMA table_info(registros)")
  columnas_reg = [col[1] for col in cursor.fetchall()]
  if "estado" not in columnas_reg:
    cursor.execute("ALTER TABLE registros ADD COLUMN estado TEXT DEFAULT 'activo'")
  if "fecha_eliminacion" not in columnas_reg:
    cursor.execute("ALTER TABLE registros ADD COLUMN fecha_eliminacion TEXT")

  # Asegurar columnas en notas_importantes
  cursor.execute("PRAGMA table_info(notas_importantes)")
  columnas_notas = [col[1] for col in cursor.fetchall()]
  if "estado" not in columnas_notas:
    cursor.execute("ALTER TABLE notas_importantes ADD COLUMN estado TEXT DEFAULT 'activo'")
  if "fecha_eliminacion" not in columnas_notas:
    cursor.execute("ALTER TABLE notas_importantes ADD COLUMN fecha_eliminacion TEXT")

  conn.commit()

  # Limpieza de elementos con más de 7 días en la papelera
  hace_siete_dias = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute("DELETE FROM registros WHERE estado = 'eliminado' AND fecha_eliminacion < ?", (hace_siete_dias,))
  cursor.execute("DELETE FROM notas_importantes WHERE estado = 'eliminado' AND fecha_eliminacion < ?", (hace_siete_dias,))
  
  conn.commit()
  conn.close()