"""Dashboard de estadísticas AGM Performance."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database import get_stats, get_servicios_full

COLORS = {
    'red':    '#CC0000',
    'gold':   '#D4AF37',
    'dark':   '#1A1A1A',
    'gray':   '#888888',
    'green':  '#228844',
    'blue':   '#1a6dc0',
    'orange': '#CC8800',
}

PALETTE = ['#CC0000','#D4AF37','#228844','#1a6dc0','#CC8800','#AA44AA','#44AACC']


def kpi(label, value, sub='', color='#CC0000'):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)


def show():
    st.markdown('<div class="agm-header"><span>PANEL DE CONTROL</span><h2>Dashboard — Estadísticas del Taller</h2></div>',
                unsafe_allow_html=True)

    stats = get_stats()
    kpis  = stats['kpis']

    total_srv = kpis.get('total_servicios') or 0
    total_cli = kpis.get('total_clientes') or 0
    fact_tot  = kpis.get('facturacion_total') or 0
    completos = kpis.get('completados') or 0
    pendientes= kpis.get('pendientes') or 0
    hp_avg    = kpis.get('ganancia_hp_avg') or 0

    # ── KPIs ─────────────────────────────────────────────────────────
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi("SERVICIOS TOTALES", total_srv, "desde el inicio")
    with c2: kpi("CLIENTES ACTIVOS",  total_cli, "registrados")
    with c3: kpi("FACTURACIÓN TOTAL", f"${fact_tot:,.0f}", "acumulada", COLORS['gold'])
    with c4: kpi("COMPLETADOS",       completos, f"de {total_srv}", COLORS['green'])
    with c5: kpi("PENDIENTES",        pendientes, "en espera", COLORS['orange'])
    with c6: kpi("GANANCIA HP PROM.", f"+{hp_avg:.1f}" if hp_avg else "─", "por ECU tuneada", COLORS['blue'])

    st.markdown("---")

    # ── GRÁFICOS FILA 1 ───────────────────────────────────────────────
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown('<div class="sec-hdr">📈 SERVICIOS Y FACTURACIÓN POR MES</div>', unsafe_allow_html=True)
        df_mes = pd.DataFrame(stats['servicios_mes'])
        if not df_mes.empty:
            df_mes['mes_label'] = pd.to_datetime(df_mes['mes']).dt.strftime('%b %Y')
            fig = go.Figure()
            fig.add_bar(x=df_mes['mes_label'], y=df_mes['cantidad'],
                        name='Servicios', marker_color=COLORS['red'],
                        yaxis='y')
            fig.add_scatter(x=df_mes['mes_label'], y=df_mes['facturacion'],
                            name='Facturación $', line=dict(color=COLORS['gold'], width=3),
                            mode='lines+markers', yaxis='y2')
            fig.update_layout(
                plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                font=dict(color='white'),
                yaxis=dict(title='Servicios', color='white', gridcolor='#2A2A2A'),
                yaxis2=dict(title='$ Facturación', overlaying='y', side='right', color=COLORS['gold']),
                legend=dict(bgcolor='#1A1A1A', bordercolor='#333'),
                height=320, margin=dict(l=0,r=0,t=10,b=0),
                xaxis=dict(gridcolor='#2A2A2A'),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de servicios aún.")

    with col_b:
        st.markdown('<div class="sec-hdr">🔵 ESTADO DE SERVICIOS</div>', unsafe_allow_html=True)
        df_est = pd.DataFrame(stats['estados'])
        if not df_est.empty:
            color_map = {'Pendiente': COLORS['orange'], 'En proceso': COLORS['blue'],
                         'Completado': COLORS['green'], 'Entregado': COLORS['gray']}
            colors = [color_map.get(e, COLORS['red']) for e in df_est['estado']]
            fig = go.Figure(go.Pie(
                labels=df_est['estado'], values=df_est['n'],
                hole=0.55,
                marker=dict(colors=colors, line=dict(color='#0D0D0D', width=2)),
                textinfo='label+percent',
                textfont=dict(size=11, color='white'),
            ))
            fig.update_layout(
                plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                font=dict(color='white'), showlegend=False,
                height=320, margin=dict(l=0,r=0,t=10,b=0),
                annotations=[dict(text=f'<b>{total_srv}</b><br>total', x=0.5, y=0.5,
                                  font=dict(size=16,color='white'), showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos aún.")

    # ── GRÁFICOS FILA 2 ───────────────────────────────────────────────
    col_c, col_d = st.columns([2, 3])

    with col_c:
        st.markdown('<div class="sec-hdr">🏆 TOP CLIENTES</div>', unsafe_allow_html=True)
        df_cli = pd.DataFrame(stats['top_clientes'])
        if not df_cli.empty:
            df_cli = df_cli.sort_values('servicios')
            fig = px.bar(df_cli, x='servicios', y='nombre', orientation='h',
                         color='servicios', color_continuous_scale=['#2A0000','#CC0000'],
                         text='servicios')
            fig.update_traces(textposition='outside', textfont=dict(color='white', size=11))
            fig.update_layout(
                plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                font=dict(color='white'),
                xaxis=dict(gridcolor='#2A2A2A', color='white'),
                yaxis=dict(color='white'),
                coloraxis_showscale=False,
                height=340, margin=dict(l=0,r=30,t=10,b=0),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin clientes aún.")

    with col_d:
        st.markdown('<div class="sec-hdr">🔧 TRABAJOS MÁS SOLICITADOS</div>', unsafe_allow_html=True)
        df_trab = pd.DataFrame(stats['trabajos'])
        df_trab = df_trab[df_trab['cantidad'] > 0].sort_values('cantidad', ascending=False)
        if not df_trab.empty:
            fig = px.bar(df_trab, x='trabajo', y='cantidad',
                         color='cantidad', color_continuous_scale=['#1A0000','#CC0000'],
                         text='cantidad')
            fig.update_traces(textposition='outside', textfont=dict(color='white', size=11))
            fig.update_layout(
                plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                font=dict(color='white', size=10),
                xaxis=dict(gridcolor='#2A2A2A', color='white', tickangle=-30),
                yaxis=dict(gridcolor='#2A2A2A', color='white'),
                coloraxis_showscale=False,
                height=340, margin=dict(l=0,r=0,t=10,b=60),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin trabajos registrados aún.")

    # ── GRÁFICOS FILA 3 ───────────────────────────────────────────────
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown('<div class="sec-hdr">🏍️ MARCAS MÁS ATENDIDAS</div>', unsafe_allow_html=True)
        df_marc = pd.DataFrame(stats['marcas'])
        if not df_marc.empty:
            fig = px.pie(df_marc, names='marca', values='cantidad',
                         color_discrete_sequence=PALETTE, hole=0.4)
            fig.update_traces(textinfo='label+percent',
                              textfont=dict(size=11, color='white'),
                              marker=dict(line=dict(color='#0D0D0D', width=2)))
            fig.update_layout(
                plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                font=dict(color='white'), showlegend=True,
                legend=dict(bgcolor='#1A1A1A', bordercolor='#333', font=dict(size=10)),
                height=320, margin=dict(l=0,r=0,t=10,b=0),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de motos aún.")

    with col_f:
        st.markdown('<div class="sec-hdr">💰 FACTURACIÓN ACUMULADA (ÚLTIMOS 12 MESES)</div>', unsafe_allow_html=True)
        df_mes2 = pd.DataFrame(stats['servicios_mes']).tail(12)
        if not df_mes2.empty and 'facturacion' in df_mes2.columns:
            df_mes2['mes_label'] = pd.to_datetime(df_mes2['mes']).dt.strftime('%b %Y')
            df_mes2['acumulado'] = df_mes2['facturacion'].cumsum()
            fig = go.Figure()
            fig.add_scatter(
                x=df_mes2['mes_label'], y=df_mes2['acumulado'],
                fill='tozeroy',
                fillcolor='rgba(204,0,0,0.15)',
                line=dict(color=COLORS['red'], width=2.5),
                mode='lines+markers',
                marker=dict(size=7, color=COLORS['gold']),
            )
            fig.update_layout(
                plot_bgcolor='#0D0D0D', paper_bgcolor='#0D0D0D',
                font=dict(color='white'),
                xaxis=dict(gridcolor='#2A2A2A', color='white'),
                yaxis=dict(gridcolor='#2A2A2A', color='white', tickprefix='$'),
                height=320, margin=dict(l=0,r=0,t=10,b=0),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de facturación aún.")

    # ── ÚLTIMOS SERVICIOS ──────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">🕐 ÚLTIMOS 10 SERVICIOS</div>', unsafe_allow_html=True)
    servicios = get_servicios_full(limit=10)
    if servicios:
        df_last = pd.DataFrame(servicios)[[
            'numero_orden','fecha_ingreso','cliente_nombre',
            'marca','modelo','dominio','total','estado','tecnico'
        ]].rename(columns={
            'numero_orden':'Orden','fecha_ingreso':'Ingreso','cliente_nombre':'Cliente',
            'marca':'Marca','modelo':'Modelo','dominio':'Dominio',
            'total':'Total $','estado':'Estado','tecnico':'Técnico'
        })
        df_last['Total $'] = df_last['Total $'].apply(lambda x: f"${x:,.2f}" if x else "─")
        st.dataframe(df_last, use_container_width=True, hide_index=True,
                     column_config={
                         'Estado': st.column_config.TextColumn(width='small'),
                         'Total $': st.column_config.TextColumn(width='small'),
                     })
    else:
        st.info("No hay servicios registrados. ¡Ingresá la primera ficha!")
