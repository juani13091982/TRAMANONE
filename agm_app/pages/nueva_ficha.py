import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
"""Formulario de carga de nueva Ficha de Service — AGM Performance."""
import streamlit as st
import json, os
from datetime import date, datetime
from database import (get_clientes, upsert_cliente, get_motos_cliente,
                      upsert_moto, next_orden, insert_servicio, get_cliente, get_moto)
from pdf_export import generate_pdf

MAX_ITEMS = 8   # filas de presupuesto (vacías se ignoran al guardar)

# ── Caché de consultas frecuentes (evita ir a la BD en cada rerun) ────────────
@st.cache_data(ttl=120)
def _clientes():
    return get_clientes()

@st.cache_data(ttl=120)
def _motos_de(cliente_id):
    return get_motos_cliente(cliente_id)


def show():
    st.markdown('<div class="agm-header"><span>CARGA DE DATOS</span>'
                '<h2>Nueva Ficha de Service y Diagnóstico</h2></div>',
                unsafe_allow_html=True)

    if 'srv_guardado' not in st.session_state:
        st.session_state.srv_guardado = None
    if 'srv_pdf_path' not in st.session_state:
        st.session_state.srv_pdf_path = None

    # ── SI YA SE GUARDÓ ───────────────────────────────────────────────
    if st.session_state.srv_guardado:
        st.success(f"✅ Servicio **{st.session_state.srv_guardado['orden']}** guardado correctamente.")
        col_pdf, col_new = st.columns([2, 1])
        with col_pdf:
            if st.session_state.srv_pdf_path and os.path.exists(st.session_state.srv_pdf_path):
                with open(st.session_state.srv_pdf_path, 'rb') as f:
                    st.download_button(
                        "⬇️  Descargar Ficha PDF",
                        data=f.read(),
                        file_name=f"{st.session_state.srv_guardado['orden']}.pdf",
                        mime='application/pdf',
                    )
        with col_new:
            if st.button("➕  Cargar nueva ficha"):
                st.session_state.srv_guardado = None
                st.session_state.srv_pdf_path = None
                st.rerun()
        return

    numero_orden = next_orden()
    st.markdown(f"**N° de Orden:** `{numero_orden}`")

    # ══════════════════════════════════════════════════════════════════
    # FUERA DEL FORM — solo los selectores que controlan campos
    # condicionales (inevitablemente causan 1 rerun al cambiar).
    # El resto va dentro del form para eliminar reruns al tipear.
    # ══════════════════════════════════════════════════════════════════

    # ── ENCABEZADO ────────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">📋 ENCABEZADO DE LA ORDEN</div>', unsafe_allow_html=True)
    e1, e2, e3, e4 = st.columns(4)
    fecha_ing = e1.date_input("Fecha de Ingreso", value=date.today())
    hora_ing  = e2.time_input("Hora de Ingreso",  value=datetime.now().time())
    fecha_ent = e3.date_input("Entrega Estimada",  value=date.today())
    prioridad = e4.selectbox("Prioridad", ["Normal", "Urgente"])

    # ── SELECTOR DE CLIENTE ───────────────────────────────────────────
    st.markdown('<div class="sec-hdr">👤 DATOS DEL CLIENTE</div>', unsafe_allow_html=True)
    clientes    = _clientes()
    cli_nombres = ["+ Nuevo cliente"] + [f"{c['nombre']} ({c['dni_cuit'] or 'sin DNI'})" for c in clientes]
    cli_sel     = st.selectbox("Cliente", cli_nombres, label_visibility='collapsed')

    cliente_id_existente = None
    cli_obj = {}
    # Valores por defecto (se sobreescriben en el form si es nuevo cliente)
    cli_nombre = cli_dni = cli_tel = cli_email = cli_dir = cli_ciu = ''

    if cli_sel != "+ Nuevo cliente":
        idx      = cli_nombres.index(cli_sel) - 1
        cli_obj  = clientes[idx]
        cliente_id_existente = cli_obj['id']
        cli_nombre = cli_obj.get('nombre', '')
        cli_dni    = cli_obj.get('dni_cuit', '')
        cli_tel    = cli_obj.get('telefono', '')
        cli_email  = cli_obj.get('email', '')
        cli_dir    = cli_obj.get('direccion', '')
        cli_ciu    = cli_obj.get('ciudad', '')
        st.info(f"📞 {cli_tel or '─'}  ·  ✉️ {cli_email or '─'}  ·  📍 {cli_ciu or '─'}")
    else:
        st.caption("↓ Completá los datos del nuevo cliente en el formulario de abajo.")

    # ── SELECTOR DE MOTO ──────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">🏍️ DATOS DE LA MOTOCICLETA</div>', unsafe_allow_html=True)
    moto_nueva        = True
    moto_obj          = {}
    moto_id_existente = None
    # Valores por defecto
    moto_marca = moto_modelo = moto_dom = moto_vin = moto_motor = moto_color = ''
    moto_anio  = datetime.now().year

    if cliente_id_existente:
        motos = _motos_de(cliente_id_existente)
        if motos:
            moto_opts = ["+ Nueva moto"] + [f"{m['marca']} {m['modelo']} — {m['dominio']}" for m in motos]
            moto_sel  = st.selectbox("Moto del cliente", moto_opts, label_visibility='collapsed')
            if moto_sel != "+ Nueva moto":
                idx2              = moto_opts.index(moto_sel) - 1
                moto_obj          = motos[idx2]
                moto_id_existente = moto_obj['id']
                moto_nueva        = False
                moto_marca  = moto_obj.get('marca', '')
                moto_modelo = moto_obj.get('modelo', '')
                moto_anio   = moto_obj.get('anio', datetime.now().year)
                moto_dom    = moto_obj.get('dominio', '')
                moto_vin    = moto_obj.get('vin', '')
                moto_motor  = moto_obj.get('nro_motor', '')
                moto_color  = moto_obj.get('color', '')
                st.info(f"VIN: {moto_vin or '─'}  ·  Motor: {moto_motor or '─'}  ·  Color: {moto_color or '─'}")
    if moto_nueva:
        st.caption("↓ Completá los datos de la nueva moto en el formulario de abajo.")

    # ══════════════════════════════════════════════════════════════════
    # FORMULARIO PRINCIPAL — todo lo demás va aquí dentro.
    # Nada dentro del form recarga la app al escribir/interactuar.
    # Solo se procesa al presionar GUARDAR.
    # ══════════════════════════════════════════════════════════════════
    with st.form("nueva_ficha_form", border=False):

        # ─── DATOS NUEVO CLIENTE (dentro del form = sin reruns) ───────
        if cli_sel == "+ Nuevo cliente":
            st.markdown('<div class="sec-hdr">📝 DATOS DEL NUEVO CLIENTE</div>', unsafe_allow_html=True)
            fa, fb = st.columns(2)
            cli_nombre = fa.text_input("Nombre y Apellido *")
            cli_dni    = fb.text_input("D.N.I. / C.U.I.T.")
            fc, fd = st.columns(2)
            cli_tel    = fc.text_input("Teléfono / Celular")
            cli_email  = fd.text_input("E-mail")
            fe, ff = st.columns(2)
            cli_dir    = fe.text_input("Dirección")
            cli_ciu    = ff.text_input("Ciudad")

        # ─── DATOS NUEVA MOTO (dentro del form = sin reruns) ──────────
        if moto_nueva:
            st.markdown('<div class="sec-hdr">🏍️ DATOS DE LA NUEVA MOTOCICLETA</div>', unsafe_allow_html=True)
            ma, mb, mc = st.columns(3)
            moto_marca  = ma.text_input("Marca")
            moto_modelo = mb.text_input("Modelo")
            moto_anio   = mc.number_input("Año", min_value=1950, max_value=2030,
                                           value=datetime.now().year, step=1)
            md, me, mf = st.columns(3)
            moto_dom   = md.text_input("Dominio / Patente *")
            moto_vin   = me.text_input("N° de Chasis (VIN)")
            moto_motor = mf.text_input("N° de Motor")
            mg, _ = st.columns([1, 2])
            moto_color = mg.text_input("Color")

        # ─── KILOMETRAJE / TIPO DE USO ────────────────────────────────
        c_km, c_uso = st.columns(2)
        kilometraje = c_km.number_input("Kilometraje actual", min_value=0, step=100, value=0)
        tipo_uso    = c_uso.selectbox("Tipo de uso", ["Calle", "Ruta", "Mixto", "Pista", "Off-road"])

        # ─── TRABAJOS ─────────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">🔧 TRABAJOS SOLICITADOS</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        t_service  = c1.checkbox("Service General")
        t_aceite   = c2.checkbox("Cambio de Aceite Motor")
        t_f_aceite = c3.checkbox("Filtro de Aceite")
        c4, c5, c6 = st.columns(3)
        t_f_aire   = c4.checkbox("Filtro de Aire")
        t_bujias   = c5.checkbox("Cambio de Bujías")
        t_valvulas = c6.checkbox("Regulación de Válvulas")
        c7, c8, c9 = st.columns(3)
        t_diag     = c7.checkbox("Diagnóstico Electrónico")
        t_ecu      = c8.checkbox("Reprogramación ECU / Mapa")
        t_dyno     = c9.checkbox("Banco de Potencia (Dyno)")
        c10, c11, c12 = st.columns(3)
        t_frenos   = c10.checkbox("Control de Frenos")
        t_transm   = c11.checkbox("Control de Transmisión")
        t_susp     = c12.checkbox("Control de Suspensiones")
        c13, c14, _ = st.columns(3)
        t_electrica = c13.checkbox("Revisión Eléctrica")
        t_lavado    = c14.checkbox("Lavado / Detailing")
        t_otro = st.text_input("Otro trabajo (describir):", placeholder="...")

        # ─── INSPECCIÓN ───────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">🔍 INSPECCIÓN TÉCNICA GENERAL</div>', unsafe_allow_html=True)
        ESTADOS_INSP = ["─", "Bueno", "Regular", "Cambiar"]
        ESTADOS_LUC  = ["─", "Bueno", "Regular", "Reparar"]
        items_insp = [
            ("Aceite Motor",           "insp_aceite",       ESTADOS_INSP),
            ("Refrigerante/Liq. Fr.",  "insp_refrigerante", ESTADOS_INSP),
            ("Pastillas Freno Del.",   "insp_past_del",     ESTADOS_INSP),
            ("Pastillas Freno Tras.",  "insp_past_tras",    ESTADOS_INSP),
            ("Kit de Transmisión",     "insp_transmision",  ESTADOS_INSP),
            ("Neumático Delantero",    "insp_neum_del",     ESTADOS_INSP),
            ("Neumático Trasero",      "insp_neum_tras",    ESTADOS_INSP),
            ("Batería / Carga",        "insp_bateria",      ESTADOS_INSP),
            ("Luces",                  "insp_luces",        ESTADOS_LUC),
            ("Suspensión Delantera",   "insp_susp_del",     ESTADOS_INSP),
            ("Suspensión Trasera",     "insp_susp_tras",    ESTADOS_INSP),
            ("Filtro de Combustible",  "insp_filtro_comb",  ESTADOS_INSP),
        ]
        insp_vals = {}
        cols_insp = st.columns(4)
        for i, (label, key, opts) in enumerate(items_insp):
            with cols_insp[i % 4]:
                val = st.selectbox(label, opts, key=f"insp_{key}")
                insp_vals[key] = None if val == "─" else val

        # ─── PERFORMANCE ──────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">⚡ PERFORMANCE & REPROGRAMACIÓN ECU</div>', unsafe_allow_html=True)
        p1, p2, p3, p4 = st.columns(4)
        ecu_leida = p1.checkbox("ECU Original Leída")
        backup    = p2.checkbox("Backup Realizado")
        mapa      = p3.text_input("Mapa / Calibración Aplicada")
        software  = p4.text_input("Herramienta / Software")
        p5, p6, p7, p8 = st.columns(4)
        hp_orig  = p5.number_input("Potencia Original (HP)", min_value=0.0, step=0.5, value=0.0, format="%.1f")
        hp_final = p6.number_input("Potencia Final (HP)",    min_value=0.0, step=0.5, value=0.0, format="%.1f")
        nm_orig  = p7.number_input("Torque Original (Nm)",   min_value=0.0, step=0.5, value=0.0, format="%.1f")
        nm_final = p8.number_input("Torque Final (Nm)",      min_value=0.0, step=0.5, value=0.0, format="%.1f")

        # ─── OBSERVACIONES ────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">📝 OBSERVACIONES TÉCNICAS</div>', unsafe_allow_html=True)
        observaciones = st.text_area("Observaciones del mecánico",
                                      placeholder="Descripción de trabajos, novedades, recomendaciones...",
                                      height=90)
        tecnico = st.text_input("Técnico Responsable", placeholder="Nombre del mecánico")

        # ─── PRESUPUESTO ──────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">💰 PRESUPUESTO / DETALLE DE TRABAJOS</div>', unsafe_allow_html=True)
        st.caption(f"Completá hasta {MAX_ITEMS} líneas. Las filas sin descripción ni costo se ignoran al guardar.")
        h1, h2, h3, h4 = st.columns([4, 1, 2, 1.5])
        h1.markdown("**Descripción**")
        h2.markdown("**Cant**")
        h3.markdown("**Mi Costo 🔒**")
        h4.markdown("**% Gan. 🔒**")

        b_desc = []; b_cant = []; b_costo = []; b_gan = []
        for idx in range(MAX_ITEMS):
            c1, c2, c3, c4 = st.columns([4, 1, 2, 1.5])
            desc    = c1.text_input("d", key=f"desc_{idx}", placeholder=f"Ítem {idx+1}...",    label_visibility='collapsed')
            cant    = c2.number_input("c", key=f"cant_{idx}", min_value=1, step=1, value=1,    label_visibility='collapsed')
            costo   = c3.number_input("p", key=f"cost_{idx}", min_value=0.0, step=100.0, value=0.0, format="%.2f", label_visibility='collapsed')
            gan_pct = c4.number_input("g", key=f"gan_{idx}",  min_value=0, max_value=99, step=5, value=0, label_visibility='collapsed')
            b_desc.append(desc); b_cant.append(cant); b_costo.append(costo); b_gan.append(gan_pct)

        # ─── IVA y ESTADO ─────────────────────────────────────────────
        st.markdown("---")
        ci, ce, _ = st.columns([1, 2, 1])
        iva_pct    = ci.number_input("IVA %", min_value=0.0, max_value=100.0, step=0.5, value=0.0, format="%.1f")
        estado_srv = ce.selectbox("Estado del servicio", ["Pendiente", "En proceso", "Completado", "Entregado"])

        # ─── BOTÓN GUARDAR ────────────────────────────────────────────
        submitted = st.form_submit_button(
            "💾  GUARDAR FICHA Y GENERAR PDF",
            type="primary", use_container_width=True
        )

    # ══════════════════════════════════════════════════════════════════
    # PROCESAMIENTO AL GUARDAR
    # ══════════════════════════════════════════════════════════════════
    if submitted:
        if cli_sel == "+ Nuevo cliente" and not cli_nombre.strip():
            st.error("El nombre del cliente es obligatorio.")
            return
        if moto_nueva and not moto_dom.strip():
            st.error("El dominio/patente de la moto es obligatorio.")
            return

        with st.spinner("Guardando y generando PDF..."):
            # Cliente
            if cli_sel == "+ Nuevo cliente":
                cid = upsert_cliente(nombre=cli_nombre, dni_cuit=cli_dni, telefono=cli_tel,
                                     email=cli_email, direccion=cli_dir, ciudad=cli_ciu)
            else:
                cid = cliente_id_existente

            # Moto
            if moto_nueva:
                mid = upsert_moto(cliente_id=cid, marca=moto_marca, modelo=moto_modelo,
                                  anio=int(moto_anio), dominio=moto_dom, vin=moto_vin,
                                  nro_motor=moto_motor, color=moto_color)
            else:
                mid = moto_id_existente

            # Calcular presupuesto
            items_out        = []
            subtotal         = 0.0
            ganancia_total_f = 0.0
            for idx in range(MAX_ITEMS):
                desc    = b_desc[idx]
                cant    = b_cant[idx]
                costo   = b_costo[idx]
                gan_pct = b_gan[idx]
                if not desc.strip() and costo == 0:
                    continue
                if 0 < gan_pct < 100:
                    precio_unit = costo / (1 - gan_pct / 100)
                else:
                    precio_unit = costo
                total_item    = cant * precio_unit
                ganancia_item = cant * (precio_unit - costo)
                subtotal         += total_item
                ganancia_total_f += ganancia_item
                items_out.append({
                    'desc': desc, 'cant': cant,
                    'costo': f"{costo:.2f}", 'ganancia_pct': gan_pct,
                    'precio': f"{precio_unit:.2f}", 'total': f"{total_item:.2f}"
                })

            iva_monto = subtotal * iva_pct / 100
            total     = subtotal + iva_monto

            srv_data = dict(
                numero_orden=numero_orden,
                fecha_ingreso=str(fecha_ing),
                hora_ingreso=str(hora_ing),
                fecha_entrega_est=str(fecha_ent),
                prioridad=prioridad, estado=estado_srv,
                cliente_id=cid, moto_id=mid,
                kilometraje=int(kilometraje), tipo_uso=tipo_uso,
                trab_service=int(t_service), trab_aceite=int(t_aceite),
                trab_filtro_aceite=int(t_f_aceite), trab_filtro_aire=int(t_f_aire),
                trab_bujias=int(t_bujias), trab_valvulas=int(t_valvulas),
                trab_diagnostico=int(t_diag), trab_ecu=int(t_ecu),
                trab_dyno=int(t_dyno), trab_frenos=int(t_frenos),
                trab_transmision=int(t_transm), trab_suspension=int(t_susp),
                trab_electrica=int(t_electrica), trab_lavado=int(t_lavado),
                trab_otro=t_otro,
                **{k: v for k, v in insp_vals.items()},
                ecu_leida=int(ecu_leida), backup_realizado=int(backup),
                mapa_aplicado=mapa, hp_original=hp_orig or None, hp_final=hp_final or None,
                nm_original=nm_orig or None, nm_final=nm_final or None,
                software_herramienta=software, tecnico=tecnico,
                observaciones=observaciones,
                items_presupuesto=json.dumps(items_out),
                subtotal=subtotal, iva_porcentaje=iva_pct, iva_monto=iva_monto,
                ganancia_total=ganancia_total_f, total=total,
            )

            sid = insert_servicio(srv_data)

            cli_full  = get_cliente(cid) or {'nombre': cli_nombre}
            moto_full = get_moto(mid) or {'marca': moto_marca, 'modelo': moto_modelo,
                                          'dominio': moto_dom, 'anio': moto_anio}
            pdf_dir  = os.path.join(os.path.dirname(__file__), '..', 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, f"{numero_orden}.pdf")
            generate_pdf(srv_data, cli_full, moto_full, pdf_path)

            # Invalidar caché para que el nuevo cliente/moto aparezcan la próxima vez
            _clientes.clear()
            _motos_de.clear()

            st.session_state.srv_guardado  = {'orden': numero_orden, 'id': sid}
            st.session_state.srv_pdf_path  = pdf_path

        st.rerun()
