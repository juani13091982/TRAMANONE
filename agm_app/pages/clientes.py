import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
"""Gestión de clientes — AGM Performance."""
import streamlit as st
import pandas as pd
from database import update_servicio
import data_cache

ESTADOS = ['Pendiente', 'En proceso', 'Completado', 'Entregado']


def show():
    st.markdown("""
    <div class="agm-header" style="padding:18px 20px 14px 24px;">
        <span class="hdr-tag">◆ GESTIÓN ◆</span>
        <span class="hdr-title">CLIENTES <span class="hdr-dash"> — </span><span class="hdr-sub">Gestión de Clientes</span></span>
        <span class="hdr-brand">AGM Performance Service &amp; Chiptunning</span>
    </div>""", unsafe_allow_html=True)

    clientes = data_cache.clientes()
    if not clientes:
        st.info("Sin clientes aún. Creá el primero al cargar una nueva ficha de service.")
        return

    # Estadísticas por cliente en una sola query SQL (sin cargar todos los servicios)
    stats_map = {r['cliente_id']: r for r in data_cache.stats_clientes()}
    for c in clientes:
        st_row = stats_map.get(c['id'], {})
        c['servicios']   = st_row.get('servicios', 0)
        c['facturacion'] = float(st_row.get('facturacion') or 0)

    df = pd.DataFrame(clientes)

    # ── BUSCADOR ─────────────────────────────────────────────────────
    busq = st.text_input("🔎 Buscar cliente por nombre, DNI o ciudad")
    if busq:
        mask = (df['nombre'].str.contains(busq, case=False, na=False) |
                df['dni_cuit'].str.contains(busq, case=False, na=False) |
                df['ciudad'].str.contains(busq, case=False, na=False))
        df = df[mask]

    st.markdown(f"**{len(df)} clientes registrados**")

    # ── TABLA ─────────────────────────────────────────────────────────
    df_show = df[['nombre','dni_cuit','telefono','email','ciudad','servicios','facturacion']].copy()
    df_show['facturacion'] = df_show['facturacion'].apply(lambda x: f"${x:,.2f}")
    df_show = df_show.rename(columns={
        'nombre':'Nombre','dni_cuit':'DNI/CUIT','telefono':'Teléfono',
        'email':'E-mail','ciudad':'Ciudad','servicios':'Servicios','facturacion':'Facturación'
    })

    selected = st.dataframe(
        df_show, use_container_width=True, hide_index=True,
        on_select='rerun', selection_mode='single-row',
    )

    # ── FICHA DEL CLIENTE SELECCIONADO ───────────────────────────────
    sel = selected.selection.rows if hasattr(selected, 'selection') else []
    if sel:
        cli = clientes[df.index[sel[0]]] if busq else clientes[sel[0]]

        st.markdown("---")
        st.markdown(f"### 👤 {cli['nombre']}")
        c1,c2,c3 = st.columns(3)
        c1.info(f"📞 **Tel:** {cli.get('telefono','─')}")
        c2.info(f"✉️ **Email:** {cli.get('email','─')}")
        c3.info(f"📍 **Ciudad:** {cli.get('ciudad','─')}")

        c4,c5 = st.columns(2)
        c4.metric("Total servicios", cli['servicios'])
        c5.metric("Facturación total", f"${cli['facturacion']:,.2f}")

        # Motos del cliente
        motos = data_cache.motos_de(cli['id'])
        if motos:
            st.markdown("#### 🏍️ Motos registradas")
            df_motos = pd.DataFrame(motos)[['marca','modelo','anio','dominio','vin','nro_motor','color']]
            df_motos = df_motos.rename(columns={
                'marca':'Marca','modelo':'Modelo','anio':'Año',
                'dominio':'Dominio','vin':'VIN','nro_motor':'N° Motor','color':'Color'
            })
            st.dataframe(df_motos, use_container_width=True, hide_index=True)

        # Historial del cliente (cargado solo cuando se abre la ficha)
        todos = data_cache.servicios_full()
        hist = [s for s in todos if s['cliente_id'] == cli['id']]
        if hist:
            st.markdown("#### 📋 Historial de servicios")
            df_hist = pd.DataFrame(hist)[['numero_orden','fecha_ingreso','marca','modelo',
                                           'dominio','total','estado','tecnico']].copy()
            df_hist['total'] = df_hist['total'].apply(lambda x: f"${float(x or 0):,.2f}")
            df_hist = df_hist.rename(columns={
                'numero_orden':'Orden','fecha_ingreso':'Ingreso','marca':'Marca',
                'modelo':'Modelo','dominio':'Dominio','total':'Total','estado':'Estado',
                'tecnico':'Técnico'
            })
            st.dataframe(df_hist, use_container_width=True, hide_index=True)

            # ── CAMBIAR ESTADO ────────────────────────────────────────
            st.markdown('<div class="sec-hdr">🔄 CAMBIAR ESTADO DEL SERVICIO</div>', unsafe_allow_html=True)
            with st.form("form_cambio_estado"):
                ordenes = [s['numero_orden'] for s in hist]
                col_a, col_b, col_c = st.columns([2,2,1])
                orden_sel   = col_a.selectbox("Orden", ordenes)
                nuevo_estado = col_b.selectbox("Nuevo estado", ESTADOS)
                guardar = col_c.form_submit_button("✅ Guardar", use_container_width=True)

                if guardar:
                    srv_match = next((s for s in hist if s['numero_orden'] == orden_sel), None)
                    if srv_match:
                        update_servicio(srv_match['id'], {'estado': nuevo_estado})
                        data_cache.clear_all()
                        st.success(f"Estado de {orden_sel} actualizado a **{nuevo_estado}**.")
                        st.rerun()
