import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
"""Formulario de carga de nueva Ficha de Service — AGM Performance."""
import streamlit as st
import json, os, tempfile
from datetime import date, datetime
from database import (get_clientes, upsert_cliente, get_motos_cliente,
                      upsert_moto, next_orden, insert_servicio)
from pdf_export import generate_pdf
from database import get_cliente, get_moto


def show():
    st.markdown('<div class="agm-header"><span>CARGA DE DATOS</span><h2>Nueva Ficha de Service y Diagnóstico</h2></div>',
                unsafe_allow_html=True)

    # ── ESTADO DE LA SESIÓN ────────────────────────────────────────────
    if 'srv_guardado' not in st.session_state:
        st.session_state.srv_guardado = None
    if 'srv_pdf_path' not in st.session_state:
        st.session_state.srv_pdf_path = None

    # ── SI YA SE GUARDÓ: mostrar botón de PDF ─────────────────────────
    if st.session_state.srv_guardado:
        st.success(f"✅ Servicio **{st.session_state.srv_guardado['orden']}** guardado correctamente.")
        col_pdf, col_new = st.columns([2,1])
        with col_pdf:
            if st.session_state.srv_pdf_path and os.path.exists(st.session_state.srv_pdf_path):
                with open(st.session_state.srv_pdf_path, 'rb') as f:
                    st.download_button(
                        "⬇️  Descargar Ficha PDF (Diseño Professional White)",
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

    # ── FORMULARIO ────────────────────────────────────────────────────
    numero_orden = next_orden()
    st.markdown(f"**N° de Orden generado automáticamente:** `{numero_orden}`")

    # ─── SECCIÓN 1: ENCABEZADO ────────────────────────────────────────
    st.markdown('<div class="sec-hdr">📋 ENCABEZADO DE LA ORDEN</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    fecha_ing  = c1.date_input("Fecha de Ingreso", value=date.today())
    hora_ing   = c2.time_input("Hora de Ingreso",  value=datetime.now().time())
    fecha_ent  = c3.date_input("Entrega Estimada",  value=date.today())
    prioridad  = c4.selectbox("Prioridad", ["Normal","Urgente"])

    # ─── SECCIÓN 2: CLIENTE ───────────────────────────────────────────
    st.markdown('<div class="sec-hdr">👤 DATOS DEL CLIENTE</div>', unsafe_allow_html=True)

    clientes = get_clientes()
    cli_nombres = ["+ Nuevo cliente"] + [f"{c['nombre']} ({c['dni_cuit'] or 'sin DNI'})" for c in clientes]
    cli_sel = st.selectbox("Seleccionar cliente existente o crear nuevo", cli_nombres)

    if cli_sel == "+ Nuevo cliente":
        c1,c2 = st.columns(2)
        cli_nombre = c1.text_input("Nombre y Apellido *")
        cli_dni    = c2.text_input("D.N.I. / C.U.I.T.")
        c3,c4 = st.columns(2)
        cli_tel    = c3.text_input("Teléfono / Celular")
        cli_email  = c4.text_input("E-mail")
        c5,c6 = st.columns(2)
        cli_dir    = c5.text_input("Dirección")
        cli_ciu    = c6.text_input("Ciudad")
        cliente_data = dict(nombre=cli_nombre, dni_cuit=cli_dni, telefono=cli_tel,
                            email=cli_email, direccion=cli_dir, ciudad=cli_ciu)
        cliente_id_existente = None
    else:
        idx = cli_nombres.index(cli_sel) - 1
        cli_obj = clientes[idx]
        st.info(f"📞 {cli_obj.get('telefono','─')}  ·  ✉️ {cli_obj.get('email','─')}  ·  📍 {cli_obj.get('ciudad','─')}")
        cliente_data = cli_obj
        cliente_id_existente = cli_obj['id']

    # ─── SECCIÓN 3: MOTO ──────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">🏍️ DATOS DE LA MOTOCICLETA</div>', unsafe_allow_html=True)

    moto_nueva = True
    moto_data  = {}

    if cliente_id_existente:
        motos = get_motos_cliente(cliente_id_existente)
        moto_opts = ["+ Nueva moto"] + [f"{m['marca']} {m['modelo']} — {m['dominio']}" for m in motos]
        moto_sel = st.selectbox("Moto del cliente", moto_opts)
        if moto_sel != "+ Nueva moto":
            idx2 = moto_opts.index(moto_sel) - 1
            moto_obj = motos[idx2]
            st.info(f"VIN: {moto_obj.get('vin','─')}  ·  Motor: {moto_obj.get('nro_motor','─')}")
            moto_data = moto_obj
            moto_nueva = False

    if moto_nueva:
        c1,c2,c3 = st.columns(3)
        moto_marca  = c1.text_input("Marca")
        moto_modelo = c2.text_input("Modelo")
        moto_anio   = c3.number_input("Año", min_value=1950, max_value=2030,
                                       value=datetime.now().year, step=1)
        c4,c5,c6 = st.columns(3)
        moto_dom    = c4.text_input("Dominio / Patente")
        moto_vin    = c5.text_input("N° de Chasis (VIN)")
        moto_motor  = c6.text_input("N° de Motor")
        c7,_ = st.columns([1,2])
        moto_color  = c7.text_input("Color")
        moto_data = dict(marca=moto_marca, modelo=moto_modelo, anio=moto_anio,
                         dominio=moto_dom, vin=moto_vin, nro_motor=moto_motor, color=moto_color)

    c_km, c_uso = st.columns(2)
    kilometraje = c_km.number_input("Kilometraje actual", min_value=0, step=100, value=0)
    tipo_uso    = c_uso.selectbox("Tipo de uso", ["Calle","Ruta","Mixto","Pista","Off-road"])

    # ─── SECCIÓN 4: TRABAJOS ──────────────────────────────────────────
    st.markdown('<div class="sec-hdr">🔧 TRABAJOS SOLICITADOS</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    t_service    = c1.checkbox("Service General")
    t_aceite     = c2.checkbox("Cambio de Aceite Motor")
    t_f_aceite   = c3.checkbox("Filtro de Aceite")
    c4,c5,c6 = st.columns(3)
    t_f_aire     = c4.checkbox("Filtro de Aire")
    t_bujias     = c5.checkbox("Cambio de Bujías")
    t_valvulas   = c6.checkbox("Regulación de Válvulas")
    c7,c8,c9 = st.columns(3)
    t_diag       = c7.checkbox("Diagnóstico Electrónico")
    t_ecu        = c8.checkbox("Reprogramación ECU / Mapa")
    t_dyno       = c9.checkbox("Banco de Potencia (Dyno)")
    c10,c11,c12 = st.columns(3)
    t_frenos     = c10.checkbox("Control de Frenos")
    t_transm     = c11.checkbox("Control de Transmisión")
    t_susp       = c12.checkbox("Control de Suspensiones")
    c13,c14,_ = st.columns(3)
    t_electrica  = c13.checkbox("Revisión Eléctrica")
    t_lavado     = c14.checkbox("Lavado / Detailing")
    t_otro       = st.text_input("Otro trabajo (describir):", placeholder="...")

    # ─── SECCIÓN 5: INSPECCIÓN ────────────────────────────────────────
    st.markdown('<div class="sec-hdr">🔍 INSPECCIÓN TÉCNICA GENERAL</div>', unsafe_allow_html=True)
    ESTADOS_INSP = ["─", "Bueno","Regular","Cambiar"]
    ESTADOS_LUC  = ["─", "Bueno","Regular","Reparar"]

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

    # ─── SECCIÓN 6: PERFORMANCE ───────────────────────────────────────
    st.markdown('<div class="sec-hdr">⚡ PERFORMANCE & REPROGRAMACIÓN ECU</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    ecu_leida   = c1.checkbox("ECU Original Leída")
    backup      = c2.checkbox("Backup Realizado")
    mapa        = c3.text_input("Mapa / Calibración Aplicada")
    software    = c4.text_input("Herramienta / Software")

    c5,c6,c7,c8 = st.columns(4)
    hp_orig  = c5.number_input("Potencia Original (HP)", min_value=0.0, step=0.5, value=0.0, format="%.1f")
    hp_final = c6.number_input("Potencia Final (HP)",    min_value=0.0, step=0.5, value=0.0, format="%.1f")
    nm_orig  = c7.number_input("Torque Original (Nm)",   min_value=0.0, step=0.5, value=0.0, format="%.1f")
    nm_final = c8.number_input("Torque Final (Nm)",      min_value=0.0, step=0.5, value=0.0, format="%.1f")

    if hp_final > hp_orig > 0:
        st.success(f"⚡ Ganancia de potencia: **+{hp_final - hp_orig:.1f} HP** ({((hp_final-hp_orig)/hp_orig*100):.1f}%)")

    tecnico = st.text_input("Técnico Responsable", placeholder="Nombre del mecánico")

    # ─── SECCIÓN 7: OBSERVACIONES ────────────────────────────────────
    st.markdown('<div class="sec-hdr">📝 OBSERVACIONES TÉCNICAS</div>', unsafe_allow_html=True)
    observaciones = st.text_area("Observaciones del mecánico",
                                  placeholder="Descripción de trabajos, novedades, recomendaciones...",
                                  height=100)

    # ─── SECCIÓN 8: PRESUPUESTO ──────────────────────────────────────
    st.markdown('<div class="sec-hdr">💰 PRESUPUESTO / DETALLE DE TRABAJOS</div>', unsafe_allow_html=True)

    if 'pres_items' not in st.session_state:
        st.session_state.pres_items = [{'desc':'','cant':1,'precio':0.0,'ganancia_pct':0}]

    def add_item():
        st.session_state.pres_items.append({'desc':'','cant':1,'precio':0.0,'ganancia_pct':0})
    def remove_item(i):
        st.session_state.pres_items.pop(i)

    # Encabezados de columnas
    h1,h2,h3,h4,h5 = st.columns([4,1,2,1.5,0.5])
    h1.markdown("**Descripción**")
    h2.markdown("**Cant**")
    h3.markdown("**Precio unit.**")
    h4.markdown("**% Ganancia** 🔒")
    h5.markdown("")

    items_out = []
    subtotal  = 0.0
    for idx, item in enumerate(st.session_state.pres_items):
        c1,c2,c3,c4,c5 = st.columns([4,1,2,1.5,0.5])
        desc     = c1.text_input("Desc",       key=f"desc_{idx}",  value=item.get('desc',''),          label_visibility='collapsed')
        cant     = c2.number_input("Cant",     key=f"cant_{idx}",  value=item.get('cant',1),            min_value=1, step=1,     label_visibility='collapsed')
        prec     = c3.number_input("Precio",   key=f"prec_{idx}",  value=float(item.get('precio',0)),   min_value=0.0, step=100.0, format="%.2f", label_visibility='collapsed')
        gan_pct  = c4.number_input("% Gan",   key=f"gan_{idx}",   value=int(item.get('ganancia_pct',0)), min_value=0, max_value=500, step=5,    label_visibility='collapsed')
        total_item = cant * prec
        subtotal  += total_item
        items_out.append({'desc': desc, 'cant': cant, 'precio': f"{prec:.2f}", 'ganancia_pct': gan_pct, 'total': f"{total_item:.2f}"})
        if c5.button("🗑", key=f"del_{idx}", help="Eliminar línea") and len(st.session_state.pres_items) > 1:
            remove_item(idx)
            st.rerun()

    st.button("➕ Agregar línea", on_click=add_item)

    # IVA y totales
    st.markdown("---")
    col_iva, col_tot = st.columns([3,1])
    col_iva.empty()
    with col_tot:
        iva_pct   = st.number_input("IVA %", min_value=0.0, max_value=100.0, step=0.5, value=0.0, format="%.1f", key="iva_pct_input")
        iva_monto = subtotal * iva_pct / 100
        total     = subtotal + iva_monto
        st.markdown(f"**Subtotal: ${subtotal:,.2f}**")
        if iva_pct > 0:
            st.markdown(f"**IVA ({iva_pct:.0f}%): ${iva_monto:,.2f}**")
        st.markdown(f"### 💵 Total: `${total:,.2f}`")

    estado_srv = st.selectbox("Estado del servicio", ["Pendiente","En proceso","Completado","Entregado"])

    # ─── GUARDAR ─────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("💾  GUARDAR FICHA Y GENERAR PDF", type="primary", use_container_width=True):

        # Validaciones básicas
        nombre_ok = cliente_data.get('nombre','').strip() if cli_sel == "+ Nuevo cliente" else True
        if not nombre_ok:
            st.error("El nombre del cliente es obligatorio.")
            return

        if moto_nueva and not moto_data.get('dominio','').strip():
            st.error("El dominio/patente de la moto es obligatorio.")
            return

        # Capturar valores de IVA del widget antes del spinner
        iva_pct   = st.session_state.get("iva_pct_input", 0.0)
        iva_monto = subtotal * iva_pct / 100
        total     = subtotal + iva_monto

        with st.spinner("Guardando y generando PDF..."):
            # Guardar / obtener cliente
            if cli_sel == "+ Nuevo cliente":
                cid = upsert_cliente(**{k: cliente_data.get(k,'') for k in
                                        ['nombre','dni_cuit','telefono','email','direccion','ciudad']})
            else:
                cid = cliente_id_existente

            # Guardar / obtener moto
            if moto_nueva:
                mid = upsert_moto(
                    cliente_id=cid,
                    marca=moto_data.get('marca',''), modelo=moto_data.get('modelo',''),
                    anio=int(moto_data.get('anio', datetime.now().year)),
                    dominio=moto_data.get('dominio',''), vin=moto_data.get('vin',''),
                    nro_motor=moto_data.get('nro_motor',''), color=moto_data.get('color','')
                )
            else:
                mid = moto_data['id']

            # Construir dict del servicio
            srv_data = dict(
                numero_orden=numero_orden,
                fecha_ingreso=str(fecha_ing),
                hora_ingreso=str(hora_ing),
                fecha_entrega_est=str(fecha_ent),
                prioridad=prioridad,
                estado=estado_srv,
                cliente_id=cid,
                moto_id=mid,
                kilometraje=int(kilometraje),
                tipo_uso=tipo_uso,
                # trabajos
                trab_service=int(t_service), trab_aceite=int(t_aceite),
                trab_filtro_aceite=int(t_f_aceite), trab_filtro_aire=int(t_f_aire),
                trab_bujias=int(t_bujias), trab_valvulas=int(t_valvulas),
                trab_diagnostico=int(t_diag), trab_ecu=int(t_ecu),
                trab_dyno=int(t_dyno), trab_frenos=int(t_frenos),
                trab_transmision=int(t_transm), trab_suspension=int(t_susp),
                trab_electrica=int(t_electrica), trab_lavado=int(t_lavado),
                trab_otro=t_otro,
                # inspección
                **{k: v for k,v in insp_vals.items()},
                # performance
                ecu_leida=int(ecu_leida), backup_realizado=int(backup),
                mapa_aplicado=mapa, hp_original=hp_orig or None, hp_final=hp_final or None,
                nm_original=nm_orig or None, nm_final=nm_final or None,
                software_herramienta=software, tecnico=tecnico,
                observaciones=observaciones,
                # presupuesto
                items_presupuesto=json.dumps(items_out),
                subtotal=subtotal,
                iva_porcentaje=iva_pct,
                iva_monto=iva_monto,
                total=total,
            )

            sid = insert_servicio(srv_data)

            # Generar PDF
            srv_full = srv_data.copy()
            cli_full = get_cliente(cid) or cliente_data
            moto_full = get_moto(mid) or moto_data

            pdf_dir = os.path.join(os.path.dirname(__file__), '..', 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, f"{numero_orden}.pdf")
            generate_pdf(srv_full, cli_full, moto_full, pdf_path)

            # Reset items presupuesto
            st.session_state.pres_items = [{'desc':'','cant':1,'precio':0.0}]

            st.session_state.srv_guardado = {'orden': numero_orden, 'id': sid}
            st.session_state.srv_pdf_path = pdf_path

        st.rerun()
