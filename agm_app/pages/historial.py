import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
"""Historial de servicios con búsqueda, filtros y descarga de PDF."""
import streamlit as st
import pandas as pd
import json, os, tempfile
from database import get_servicios_full, get_servicio, get_cliente, get_moto, update_servicio, delete_servicio
from pdf_export import generate_pdf


def show():
    st.markdown("""
    <div class="agm-header" style="padding:18px 20px 14px 24px;">
        <span class="hdr-tag">◆ REGISTROS ◆</span>
        <span class="hdr-title">HISTORIAL <span class="hdr-dash"> — </span><span class="hdr-sub">Servicios Realizados</span></span>
        <span class="hdr-brand">AGM Performance Service &amp; Chiptunning</span>
    </div>""", unsafe_allow_html=True)

    servicios = get_servicios_full(limit=500)
    if not servicios:
        st.info("No hay servicios registrados aún. Cargá la primera ficha en **Nueva Ficha de Service**.")
        return

    df = pd.DataFrame(servicios)

    # ── FILTROS ───────────────────────────────────────────────────────
    with st.expander("🔎 Filtros de búsqueda", expanded=True):
        c1,c2,c3,c4 = st.columns(4)
        f_cliente = c1.text_input("Cliente (nombre)")
        f_moto    = c2.text_input("Moto (marca / modelo / dominio)")
        f_estado  = c3.selectbox("Estado", ["Todos","Pendiente","En proceso","Completado","Entregado"])
        c_desde, c_hasta = st.columns(2)
        from datetime import date as dt
        f_desde   = c_desde.date_input("Desde", value=dt(dt.today().year, 1, 1))
        f_hasta   = c_hasta.date_input("Hasta", value=dt.today())

    # Aplicar filtros
    mask = pd.Series([True]*len(df))
    if f_cliente:
        mask &= df['cliente_nombre'].str.contains(f_cliente, case=False, na=False)
    if f_moto:
        mask &= (df['marca'].str.contains(f_moto, case=False, na=False) |
                 df['modelo'].str.contains(f_moto, case=False, na=False) |
                 df['dominio'].str.contains(f_moto, case=False, na=False))
    if f_estado != "Todos":
        mask &= df['estado'] == f_estado
    mask &= (df['fecha_ingreso'] >= str(f_desde)) & (df['fecha_ingreso'] <= str(f_hasta))
    df_f = df[mask].reset_index(drop=True)

    st.markdown(f"**{len(df_f)} servicios encontrados**")

    if df_f.empty:
        st.warning("No hay resultados con esos filtros.")
        return

    # ── TABLA RESUMEN ─────────────────────────────────────────────────
    display_cols = {
        'numero_orden': 'Orden',
        'fecha_ingreso': 'Ingreso',
        'cliente_nombre': 'Cliente',
        'marca': 'Marca',
        'modelo': 'Modelo',
        'dominio': 'Dominio',
        'kilometraje': 'KM',
        'total': 'Total $',
        'estado': 'Estado',
        'tecnico': 'Técnico',
    }
    df_show = df_f[list(display_cols.keys())].rename(columns=display_cols)
    df_show['Total $'] = df_show['Total $'].apply(lambda x: f"${float(x or 0):,.2f}")

    selected = st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
        on_select='rerun',
        selection_mode='single-row',
        column_config={
            'Estado': st.column_config.TextColumn(width='small'),
            'KM':     st.column_config.NumberColumn(width='small', format="%d"),
        }
    )

    # ── DETALLE DEL SERVICIO SELECCIONADO ─────────────────────────────
    sel_rows = selected.selection.rows if hasattr(selected,'selection') else []
    if sel_rows:
        idx = sel_rows[0]
        row = df_f.iloc[idx]
        sid = int(row['id'])
        srv = get_servicio(sid)
        cli = get_cliente(srv['cliente_id'])
        moto = get_moto(srv['moto_id'])

        st.markdown("---")
        col_titulo, col_del = st.columns([5,1])
        col_titulo.markdown(f"### Detalle: `{srv['numero_orden']}`")

        # Botón eliminar con confirmación
        with col_del:
            if st.button("🗑️ Eliminar", key=f"del_srv_{sid}", help="Eliminar este servicio"):
                st.session_state[f"confirm_del_{sid}"] = True
        if st.session_state.get(f"confirm_del_{sid}"):
            st.error(f"⚠️ ¿Confirmar eliminación de **{srv['numero_orden']}**? Esta acción no se puede deshacer.")
            c_si, c_no = st.columns(2)
            if c_si.button("✅ Sí, eliminar", key=f"confirm_yes_{sid}"):
                delete_servicio(sid)
                st.session_state.pop(f"confirm_del_{sid}", None)
                st.success("Servicio eliminado.")
                st.rerun()
            if c_no.button("❌ Cancelar", key=f"confirm_no_{sid}"):
                st.session_state.pop(f"confirm_del_{sid}", None)
                st.rerun()

        tab1, tab2, tab3, tab4 = st.tabs(["📋 Resumen", "🔧 Trabajos & Inspección", "⚡ Performance", "💰 Presupuesto"])

        with tab1:
            c1,c2,c3 = st.columns(3)
            c1.metric("Cliente", cli.get('nombre','') if cli else '─')
            c2.metric("Moto", f"{moto.get('marca','')} {moto.get('modelo','')}" if moto else '─')
            c3.metric("Estado", srv.get('estado','─'))
            c4,c5,c6 = st.columns(3)
            c4.metric("Ingreso", srv.get('fecha_ingreso','─'))
            c5.metric("Kilómetros", f"{srv.get('kilometraje',0):,}")
            c6.metric("Total", f"${float(srv.get('total',0) or 0):,.2f}")

            # Cambio de estado
            nuevo_estado = st.selectbox("Cambiar estado",
                                        ["Pendiente","En proceso","Completado","Entregado"],
                                        index=["Pendiente","En proceso","Completado","Entregado"].index(srv.get('estado','Pendiente')),
                                        key=f"estado_sel_{sid}")
            if st.button("💾 Actualizar estado", key=f"upd_{sid}"):
                update_servicio(sid, {'estado': nuevo_estado})
                st.success("Estado actualizado.")
                st.rerun()

        with tab2:
            trab_map = [
                ('trab_service','Service General'), ('trab_aceite','Cambio Aceite'),
                ('trab_filtro_aceite','Filtro Aceite'), ('trab_filtro_aire','Filtro Aire'),
                ('trab_bujias','Bujías'), ('trab_valvulas','Válvulas'),
                ('trab_diagnostico','Diagnóstico'), ('trab_ecu','ECU/Reprog.'),
                ('trab_dyno','Dyno'), ('trab_frenos','Frenos'),
                ('trab_transmision','Transmisión'), ('trab_suspension','Suspensión'),
                ('trab_electrica','Eléctrica'), ('trab_lavado','Lavado'),
            ]
            st.markdown("**Trabajos solicitados:**")
            cols = st.columns(4)
            for i, (k, lbl) in enumerate(trab_map):
                mark = "✅" if srv.get(k) else "☐"
                cols[i%4].markdown(f"{mark} {lbl}")
            if srv.get('trab_otro'):
                st.markdown(f"➕ Otro: {srv['trab_otro']}")

            st.markdown("---")
            st.markdown("**Inspección técnica:**")
            insp_items = [
                ('insp_aceite','Aceite Motor'), ('insp_refrigerante','Refrigerante'),
                ('insp_past_del','Past. Del.'), ('insp_past_tras','Past. Tras.'),
                ('insp_transmision','Transmisión'), ('insp_neum_del','Neumático Del.'),
                ('insp_neum_tras','Neumático Tras.'), ('insp_bateria','Batería'),
                ('insp_luces','Luces'), ('insp_susp_del','Susp. Del.'),
                ('insp_susp_tras','Susp. Tras.'), ('insp_filtro_comb','Filtro Comb.'),
            ]
            color_map = {'Bueno':'🟢','Regular':'🟡','Cambiar':'🔴','Reparar':'🔴'}
            cols2 = st.columns(4)
            for i, (k, lbl) in enumerate(insp_items):
                val = srv.get(k) or '─'
                ico = color_map.get(val, '⚪')
                cols2[i%4].markdown(f"{ico} **{lbl}**: {val}")

        with tab3:
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("ECU Leída", "✅ Sí" if srv.get('ecu_leida') else "❌ No")
            c2.metric("Backup", "✅ Sí" if srv.get('backup_realizado') else "❌ No")
            c3.metric("Mapa", srv.get('mapa_aplicado') or '─')
            c4.metric("Software", srv.get('software_herramienta') or '─')
            c5,c6,c7,c8 = st.columns(4)
            hp_o = srv.get('hp_original') or 0
            hp_f = srv.get('hp_final') or 0
            c5.metric("HP Original", f"{hp_o:.1f}" if hp_o else '─')
            c6.metric("HP Final", f"{hp_f:.1f}" if hp_f else '─',
                      delta=f"+{hp_f-hp_o:.1f}" if hp_f and hp_o else None)
            c7.metric("Nm Original", f"{srv.get('nm_original') or '─'}")
            c8.metric("Nm Final",    f"{srv.get('nm_final') or '─'}")
            if srv.get('observaciones'):
                st.markdown(f"**Observaciones:** {srv['observaciones']}")

        with tab4:
            items = json.loads(srv.get('items_presupuesto','[]') or '[]')
            if items:
                df_owner = pd.DataFrame(items)
                # Columnas disponibles según versión del registro
                col_order  = ['desc','cant','costo','ganancia_pct','precio','total']
                col_labels = {'desc':'Descripción','cant':'Cant','costo':'Mi Costo 🔒',
                              'ganancia_pct':'% Gan. 🔒','precio':'Precio cliente','total':'Total'}
                cols_show  = [c for c in col_order if c in df_owner.columns]
                st.markdown("**Detalle de ítems (vista propietario):**")
                st.dataframe(df_owner[cols_show].rename(columns=col_labels),
                             use_container_width=True, hide_index=True)

            subtotal       = float(srv.get('subtotal', 0) or 0)
            iva_pct        = float(srv.get('iva_porcentaje', 0) or 0)
            iva_monto      = float(srv.get('iva_monto', 0) or 0)
            total          = float(srv.get('total', 0) or 0)
            ganancia_total = float(srv.get('ganancia_total', 0) or 0)

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal", f"${subtotal:,.2f}")
            if iva_pct > 0:
                c1.metric(f"IVA ({iva_pct:.0f}%)", f"${iva_monto:,.2f}")
            c2.metric("TOTAL A PAGAR", f"${total:,.2f}")
            c3.metric("GANANCIA NETA 🔒", f"${ganancia_total:,.2f}")

        # ── DESCARGA PDF ──────────────────────────────────────────────
        st.markdown("---")
        pdf_dir = os.path.join(os.path.dirname(__file__), '..', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"{srv['numero_orden']}.pdf")

        if st.button("🖨️ Generar / Descargar PDF", type="primary"):
            with st.spinner("Generando PDF..."):
                generate_pdf(srv, cli or {}, moto or {}, pdf_path)
            with open(pdf_path, 'rb') as f:
                st.download_button(
                    "⬇️ Descargar PDF",
                    data=f.read(),
                    file_name=f"{srv['numero_orden']}.pdf",
                    mime='application/pdf',
                )
