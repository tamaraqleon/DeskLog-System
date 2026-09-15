from datetime import datetime, timedelta
import streamlit as st
from database import get_supabase_client

# ------------------------------------------
# 1. REGISTRO DE TURNOS
# ------------------------------------------

def render_registro_turnos():
    st.title("Libro Recepción")
    
    fecha_seleccionada = st.date_input("Seleccione la fecha:", datetime.now())
    fecha_actual = fecha_seleccionada.strftime("%Y-%m-%d")

    if "fecha_anterior" not in st.session_state:
      st.session_state.fecha_anterior = fecha_actual

    if st.session_state.fecha_anterior != fecha_actual:
      st.session_state.fecha_anterior = fecha_actual
      for key in list(st.session_state.keys()):
        if key.startswith("suceso_") or key.startswith("nota_"):
          st.session_state[key] = ""
      st.rerun()
    
    st.subheader(f"Registrando para el día: {fecha_actual}")
    st.markdown("Añade los eventos de tu jornada.")
    st.divider()

    if "filas_activas" not in st.session_state:
      st.session_state.filas_activas = [0, 1, 2]
      st.session_state.contador_id = 3

    opciones_horas = [
        "08:30", "09:00", "10:00", "11:00", "12:00", 
        "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "Otro"
    ]

    with st.form("form_bitacora_dinamica"):
      eventos_a_guardar = []
      filas_a_eliminar = None

      col_h, col_s, col_n, col_d = st.columns([1.5, 3.5, 3.5, 0.8])
      col_h.markdown("**Hora**")
      col_s.markdown("**Descripción**")
      col_n.markdown("**Detalle adicional**")
      col_d.markdown("**Borrar**")

      for idx in st.session_state.filas_activas:
        c1, c2, c3, c4 = st.columns([1.5, 3.5, 3.5, 0.8])
        with c1:
          hora = st.selectbox(f"Hora {idx}", opciones_horas, key=f"hora_{idx}", label_visibility="collapsed")
        with c2:
          suceso = st.text_area(f"Suceso {idx}", key=f"suceso_{idx}", placeholder="¿Qué pasó?", label_visibility="collapsed", height=70)
        with c3:
          nota = st.text_area(f"Nota {idx}", key=f"nota_{idx}", placeholder="Detalle opcional", label_visibility="collapsed", height=70)
        with c4:
          if st.form_submit_button("🗑️", key=f"del_{idx}"):
            filas_a_eliminar = idx
        
        eventos_a_guardar.append({"id": idx, "hora": hora, "suceso": suceso, "nota": nota})

      st.divider()
      
      col_btn1, col_espacio, col_btn2 = st.columns([1, 4.5, 2.2])
      with col_btn1:
        agregar_fila = st.form_submit_button("Añadir fila")
      with col_btn2:
        guardar_todo = st.form_submit_button("Guardar", type="primary")

      if filas_a_eliminar is not None:
        if len(st.session_state.filas_activas) > 1:
          st.session_state.filas_activas.remove(filas_a_eliminar)
          st.rerun()
        else:
          st.warning("Debe mantener al menos una fila.")

      if agregar_fila:
        nuevo_id = st.session_state.contador_id
        st.session_state.filas_activas.append(nuevo_id)
        st.session_state.contador_id += 1
        st.rerun()

      if guardar_todo:
        supabase = get_supabase_client()
        guardados_count = 0
        for ev in eventos_a_guardar:
          if ev["suceso"].strip() != "":  
            supabase.table("registros").insert({
                "fecha": fecha_actual,
                "hora": ev["hora"],
                "suceso": ev["suceso"],
                "nota": ev["nota"],
                "estado": "activo"
            }).execute()
            guardados_count += 1

        if guardados_count > 0:
          st.success(f"¡Se han guardado {guardados_count} registros para el día {fecha_actual} con éxito!")
        else:
          st.warning("No hay nada para guardar.")

# --------------------------------------------
# 2. BUSCAR EN EL HISTÓRICO 
# --------------------------------------------

def render_buscador():
    st.title("Buscador de Antecedentes")  
    st.write("Busca registros por palabra clave o selecciona un día específico para revisar o limpiar turnos.")
    
    tipo_busqueda = st.radio("¿Cómo deseas buscar?", ["Por palabra clave", "Por día específico"], horizontal=True)
    termino_busqueda_sql = ""
    ejecutar_busqueda = False

    if tipo_busqueda == "Por palabra clave":
      with st.form("form_busqueda_clave"):
        termino = st.text_input("Escribe una palabra clave (ej: nombre, documento):", key="input_busqueda_historico")
        buscar_en_formulario = st.form_submit_button("Buscar")

      if buscar_en_formulario:
        termino_busqueda_sql = termino.strip()
        ejecutar_busqueda = True
    else:
      col_fb1, col_fb2, col_fb3 = st.columns(3)
      hoy = datetime.now()
      with col_fb1:
        f_dia = st.selectbox("Día", list(range(1, 32)), index=hoy.day - 1, key="busq_dia")
      with col_fb2:
        meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
        f_mes = st.selectbox("Mes", list(meses.keys()), format_func=lambda x: meses[x], index=hoy.month - 1, key="busq_mes")
      with col_fb3:
        f_anio = st.number_input("Año", min_value=2024, max_value=2030, value=hoy.year, key="busq_anio")

      if st.button("Buscar"):
        try:
          fecha_busq_obj = datetime(f_anio, f_mes, f_dia)
          termino_busqueda_sql = fecha_busq_obj.strftime("%Y-%m-%d")
          ejecutar_busqueda = True
        except ValueError:
          st.error("⚠️ La fecha seleccionada no es válida.")

    if ejecutar_busqueda:
      supabase = get_supabase_client()
      query = supabase.table("registros").select("id, fecha, hora, suceso, nota").eq("estado", "activo")
      
      if termino_busqueda_sql:
        query = query.or_(f"suceso.ilike.%{termino_busqueda_sql}%,nota.ilike.%{termino_busqueda_sql}%,fecha.eq.{termino_busqueda_sql}")
      
      response = query.order("fecha", desc=True).order("hora", desc=True).execute()
      resultados = [(r["id"], r["fecha"], r["hora"], r["suceso"], r["nota"]) for r in response.data]
      st.session_state["resultados_busqueda"] = resultados

    if "resultados_busqueda" in st.session_state and st.session_state["resultados_busqueda"]:
      resultados = st.session_state["resultados_busqueda"]
      st.divider()
      st.success(f"Se encontraron {len(resultados)} coincidencias:")
      
      # Si es observador, ocultamos el botón de borrar de los resultados del buscador
      es_observador = st.session_state.get("role") == "observer"

      for res_id, fecha, hora, suceso, nota in resultados:
        col_res1, col_res2 = st.columns([5, 1] if not es_observador else [6, 0.01])
        with col_res1:
          st.info(f"**Fecha:** {fecha} | **Hora:** {hora}\n\n**Registro:** {suceso}\n\n**Nota:** {nota if nota else 'Sin notas adicionales'}")
        if not es_observador:
          with col_res2:
            if st.button("🗑️", key=f"del_hist_{res_id}", help="Enviar a papelera"):
              supabase = get_supabase_client()
              ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              supabase.table("registros").update({
                  "estado": "eliminado",
                  "fecha_eliminacion": ahora
              }).eq("id", res_id).execute()
              
              st.session_state["resultados_busqueda"] = [r for r in resultados if r[0] != res_id]
              st.rerun()

# --------------------------------------------
# 3. VISTA CUADERNO
# --------------------------------------------

def render_cuaderno():
    st.title("Cuaderno de Turnos")
    st.write("Hojea las páginas del libro por día para revisar los turnos pasados como en un cuaderno físico.")

    if "fecha_cuaderno_actual" not in st.session_state:
      st.session_state.fecha_cuaderno_actual = datetime.now().date()

    col_flecha_izq, col_date_c, col_flecha_der = st.columns([1, 4, 1])

    with col_flecha_izq:
      st.markdown("<br>", unsafe_allow_html=True)
      if st.button("◀", use_container_width=True):
        st.session_state.fecha_cuaderno_actual -= timedelta(days=1)
        st.rerun()

    with col_date_c:
      fecha_cuaderno = st.date_input("Selecciona la página (día) a revisar:", value=st.session_state.fecha_cuaderno_actual, key="date_cuaderno_input")
      if fecha_cuaderno != st.session_state.fecha_cuaderno_actual:
        st.session_state.fecha_cuaderno_actual = fecha_cuaderno
        st.rerun()

    with col_flecha_der:
      st.markdown("<br>", unsafe_allow_html=True)
      if st.button("▶", use_container_width=True):
        st.session_state.fecha_cuaderno_actual += timedelta(days=1)
        st.rerun()

    fecha_busqueda_str = st.session_state.fecha_cuaderno_actual.strftime("%Y-%m-%d")
    
    st.divider()
    st.markdown(f"### Página del día: {fecha_busqueda_str}")
    st.write("") # Pequeño respiro visual

    supabase = get_supabase_client()
    response = supabase.table("registros").select("hora, suceso, nota").eq("estado", "activo").eq("fecha", fecha_busqueda_str).order("hora", desc=False).execute()
    registros_dia = [(r["hora"], r["suceso"], r["nota"]) for r in response.data]

    if registros_dia:
      for hora, suceso, nota in registros_dia:
        # Usamos contenedores con borde para estructurarlos como tarjetas limpias y ordenadas
        with st.container(border=True):
          col_h, col_t = st.columns([1, 6])
          with col_h:
            st.markdown(f"**{hora}**")
          with col_t:
            st.write(f"{suceso}")
            if nota:
              st.caption(f"Detalle: {nota}")
    else:
      st.info("No hay registros para esta fecha.")

# ----------------------------------------------
# 4. NOTAS 
# ----------------------------------------------

def render_notas():
    st.title("Notas")
    st.write("Guarde aquí información de referencia permanente, como listados de jefaturas, secretarias o procesos de reservas.")
    st.divider()

    # Si es observador, bloqueamos la creación de nuevas notas
    es_observador = st.session_state.get("role") == "observer"

    if not es_observador:
        if "input_titulo_nota" not in st.session_state:
          st.session_state["input_titulo_nota"] = ""
        if "input_contenido_nota" not in st.session_state:
          st.session_state["input_contenido_nota"] = ""

        if "limpiar_campos" not in st.session_state:
          st.session_state["limpiar_campos"] = False

        if st.session_state["limpiar_campos"]:
          st.session_state["campo_titulo_temp"] = ""
          st.session_state["campo_contenido_temp"] = ""
          st.session_state["limpiar_campos"] = False

        with st.expander("➕ Añadir nueva nota", expanded=False):
          titulo_nota = st.text_input("Título", key="campo_titulo_temp")
          contenido_nota = st.text_area("Contenido", height=120, key="campo_contenido_temp")
          
          col_espacio_n, col_btn_n = st.columns([5, 2])
          with col_btn_n:
            guardar_nota = st.button("Guardar Nota", type="primary")

          if guardar_nota:
            if titulo_nota.strip() != "" and contenido_nota.strip() != "":
              supabase = get_supabase_client()
              supabase.table("notas_importantes").insert({
                  "titulo": titulo_nota,
                  "contenido": contenido_nota,
                  "estado": "activo"
              }).execute()
              
              st.session_state["limpiar_campos"] = True
              st.success("¡Nota guardada con éxito en la nube!")
              st.rerun()
            else:
              st.warning("Debe rellenar tanto el título como el contenido de la nota.")

        st.divider()
    
    st.subheader("Notas Guardadas")

    supabase = get_supabase_client()
    response = supabase.table("notas_importantes").select("id, titulo, contenido").eq("estado", "activo").order("id", desc=True).execute()
    notas = [(n["id"], n["titulo"], n["contenido"]) for n in response.data]

    if notas:
      for nota_id, titulo, contenido in notas:
        edit_key = f"editando_{nota_id}"
        if edit_key not in st.session_state:
          st.session_state[edit_key] = False

        if not st.session_state[edit_key]:
          with st.expander(f"{titulo}"):
            st.write(contenido)
            if not es_observador:
              col_nb1, col_nb2 = st.columns([1, 1])
              with col_nb1:
                if st.button("Editar", key=f"btn_edit_{nota_id}"):
                  st.session_state[edit_key] = True
                  st.rerun()
              with col_nb2:
                if st.button("Enviar a papelera", key=f"del_nota_{nota_id}"):
                  ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                  supabase.table("notas_importantes").update({
                      "estado": "eliminado",
                      "fecha_eliminacion": ahora
                  }).eq("id", nota_id).execute()
                  
                  st.success(f"Nota '{titulo}' enviada a la papelera.")
                  st.rerun()
        else:
          if not es_observador:
            with st.container():
              st.markdown(f"**Editando: {titulo}**")
              nuevo_titulo = st.text_input("Nuevo título", value=titulo, key=f"nt_title_{nota_id}")
              nuevo_contenido = st.text_area("Nuevo contenido", value=contenido, height=120, key=f"nt_cont_{nota_id}")
              
              col_e1, col_e2 = st.columns([1, 1])
              with col_e1:
                if st.button("Guardar cambios", key=f"save_edit_{nota_id}", type="primary"):
                  if nuevo_titulo.strip() != "" and nuevo_contenido.strip() != "":
                    supabase.table("notas_importantes").update({
                        "titulo": nuevo_titulo,
                        "contenido": nuevo_contenido
                    }).eq("id", nota_id).execute()
                    
                    st.session_state[edit_key] = False
                    st.success("¡Nota actualizada con éxito!")
                    st.rerun()
                  else:
                    st.warning("Los campos no pueden quedar vacíos.")
              with col_e2:
                if st.button("Cancelar", key=f"cancel_edit_{nota_id}"):
                  st.session_state[edit_key] = False
                  st.rerun()
            st.divider()
    else:
      st.info("No hay notas guardadas")

# ---------------------------------------------
# 5. PAPELERA 
# ---------------------------------------------

def render_papelera():
    st.title("Papelera de Reciclaje")
    st.write("Los elementos eliminados se conservan aquí durante 7 días antes de borrarse de forma definitiva. Puedes restaurarlos o eliminarlos de inmediato si lo deseas.")
    st.divider()

    supabase = get_supabase_client()
    
    res_reg = supabase.table("registros").select("id, fecha, hora, suceso, fecha_eliminacion").eq("estado", "eliminado").order("fecha_eliminacion", desc=True).execute()
    registros_papelera = [(r["id"], r["fecha"], r["hora"], r["suceso"], r["fecha_eliminacion"]) for r in res_reg.data]

    res_not = supabase.table("notas_importantes").select("id, titulo, fecha_eliminacion").eq("estado", "eliminado").order("fecha_eliminacion", desc=True).execute()
    notas_papelera = [(n["id"], n["titulo"], n["fecha_eliminacion"]) for n in res_not.data]

    total_papelera = len(registros_papelera) + len(notas_papelera)

    if total_papelera == 0:
      st.info("La papelera está vacía.")
    else:
      if registros_papelera:
        st.subheader("Registros de Bitácora en Papelera")
        for reg_id, fecha, hora, suceso, f_elim in registros_papelera:
          col_p1, col_p2, col_p3 = st.columns([4, 1.5, 1.5])
          with col_p1:
            st.text(f"[{fecha} - {hora}] {suceso} (Borrado el: {f_elim})")
          with col_p2:
            if st.button("Restaurar", key=f"rest_reg_{reg_id}"):
              supabase.table("registros").update({
                  "estado": "activo",
                  "fecha_eliminacion": None
              }).eq("id", reg_id).execute()
              st.success("Registro restaurado con éxito.")
              st.rerun()
          with col_p3:
            if st.button("Borrar ya", key=f"perm_reg_{reg_id}"):
              supabase.table("registros").delete().eq("id", reg_id).execute()
              st.success("Eliminado definitivamente.")
              st.rerun()

      if notas_papelera:
        st.subheader("Notas Importantes en Papelera")
        for nota_id, titulo, f_elim in notas_papelera:
          col_n1, col_n2, col_n3 = st.columns([4, 1.5, 1.5])
          with col_n1:
            st.text(f"📌 {titulo} (Borrado el: {f_elim})")
          with col_n2:
            if st.button("Restaurar nota", key=f"rest_nota_{nota_id}"):
              supabase.table("notas_importantes").update({
                  "estado": "activo",
                  "fecha_eliminacion": None
              }).eq("id", nota_id).execute()
              st.success("Nota restaurada con éxito.")
              st.rerun()
          with col_n3:
            if st.button("Borrar nota ya", key=f"perm_nota_{nota_id}"):
              supabase.table("notas_importantes").delete().eq("id", nota_id).execute()
              st.success("Nota eliminada definitivamente.")
              st.rerun()


# ------------------------------------------
# 6. BIENVENIDA 
# ------------------------------------------

def render_bienvenida():
  _, col_centro, _ = st.columns([1, 2, 1])
  
  with col_centro:
      st.markdown("<h1 style='text-align: center;'>Bienvenida</h1>", unsafe_allow_html=True)
      st.markdown("<p style='text-align: center; color: gray;'>Selecciona una opcion para comenzar</p>", unsafe_allow_html=True)
      st.write("")
      
      # Verificamos si el usuario actual es observador
      es_observador = st.session_state.get("role") == "observer"
      
      if st.button("Registro de Turnos", use_container_width=True, disabled=es_observador):
          st.session_state.menu_seleccionado = "Registro de Turnos"
          st.rerun()
          
      if st.button("Vista Cuaderno", use_container_width=True):
          st.session_state.menu_seleccionado = "Vista Cuaderno"
          st.rerun()
          
      if st.button("Buscar en el Historico", use_container_width=True):
          st.session_state.menu_seleccionado = "Buscar en el Histórico"
          st.rerun()
          
      if st.button("Notas", use_container_width=True, disabled=es_observador):
          st.session_state.menu_seleccionado = "Notas"
          st.rerun()
          
      if st.button("Papelera", use_container_width=True, disabled=es_observador):
          st.session_state.menu_seleccionado = "Papelera"
          st.rerun()

  st.markdown("<br><br>", unsafe_allow_html=True)
  st.markdown("<div style='text-align: center; color: gray; font-size: 12px;'>DeskLog System — Operando en la nube con Supabase.</div>", unsafe_allow_html=True)

