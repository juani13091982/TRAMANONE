"""
AGM Performance — Sistema de Gestión de Service
Aplicación Streamlit principal
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))  # garantiza imports en Streamlit Cloud

import streamlit as st
from database import init_db

LOGO = os.path.join(os.path.dirname(__file__), "logo.jpg")

st.set_page_config(
    page_title="AGM Performance — Service Manager",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar BD al arrancar
init_db()

# ── CSS global ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar — siempre visible, no se puede colapsar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D0D 0%, #1A1A1A 100%);
    transform: none !important;
    min-width: 260px !important;
    width: 260px !important;
    display: flex !important;
}
[data-testid="stSidebar"] * { color: #EEEEEE !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 14px; }

/* Ocultar el botón de colapsar/expandir el sidebar */
[data-testid="collapsedControl"]   { display: none !important; }
[data-testid="baseButton-headerNoPadding"] { display: none !important; }

/* Header strip base */
.agm-header {
    background: linear-gradient(100deg, #0D0D0D 0%, #1E1E1E 60%, #2A0000 100%);
    border-left: 5px solid #CC0000;
    border-radius: 6px;
    margin-bottom: 18px;
    overflow: hidden;
}

/* KPI cards — compactas para 7 columnas */
.kpi-card {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-top: 3px solid #CC0000;
    border-radius: 6px;
    padding: 12px 6px;
    text-align: center;
    color: white;
    min-height: 100px;
}
.kpi-card .kpi-value {
    font-size: clamp(16px, 2.4vw, 26px);
    font-weight: 800;
    color: #CC0000;
    line-height: 1.1;
    word-break: break-word;
}
.kpi-card .kpi-label { font-size: 9px; color: #AAAAAA; letter-spacing: 0.8px; text-transform: uppercase; margin-top: 4px; }
.kpi-card .kpi-sub   { font-size: 11px; color: #DDDDDD; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: #1A1A1A; color: #AAAAAA;
    border-radius: 4px 4px 0 0; padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #CC0000 !important; color: white !important;
}

/* Buttons */
.stButton > button {
    background: #CC0000; color: white; border: none;
    font-weight: bold; border-radius: 4px;
}
.stButton > button:hover { background: #AA0000; }

/* Section headers */
.sec-hdr {
    background: #1A1A1A; color: white; padding: 6px 14px;
    border-left: 4px solid #CC0000; border-radius: 3px;
    font-size: 13px; font-weight: bold; margin: 14px 0 8px 0;
    letter-spacing: 1px;
}

/* Status badges */
.badge-pendiente  { background:#CC8800; color:white; padding:2px 10px; border-radius:12px; font-size:11px; }
.badge-proceso    { background:#1a6dc0; color:white; padding:2px 10px; border-radius:12px; font-size:11px; }
.badge-completado { background:#228844; color:white; padding:2px 10px; border-radius:12px; font-size:11px; }
.badge-entregado  { background:#555555; color:white; padding:2px 10px; border-radius:12px; font-size:11px; }

div[data-testid="stMetric"] { background: #F9F9F9; border-radius:6px; padding:10px; }

/* Ocultar navegación automática de Streamlit (usamos la propia del sidebar) */
[data-testid="stSidebarNav"] { display: none !important; }

/* Ocultar SOLO los botones del toolbar (Share, estrella, lápiz, GitHub, menú)
   SIN ocultar el header completo — así el botón del panel lateral sigue funcionando */
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }

/* Dejar el header transparente (invisible pero presente para el toggle del sidebar) */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    border-bottom: none !important;
}

/* Ocultar botón "Manage app" (esquina inferior derecha) */
[data-testid="manage-app-button"]  { display: none !important; }
[data-testid="stBottom"]           { display: none !important; }
.viewerBadge_container__r5tak      { display: none !important; }
#MainMenu                          { display: none !important; }
footer                             { display: none !important; }
footer + div                       { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists(LOGO):
        st.image(LOGO, width=180)
    st.markdown("---")
    st.markdown("### 🏍️ AGM Performance")
    st.markdown("<span style='color:#CC0000;font-size:11px;letter-spacing:1px'>SERVICE · CHIPTUNNING · DIAGNÓSTICO</span>",
                unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("", [
        "🏠  Dashboard",
        "📋  Nueva Ficha de Service",
        "📂  Historial de Servicios",
        "👥  Clientes",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.caption("AGM Performance © 2025")

# ── ROUTING ───────────────────────────────────────────────────────────────────
if "Dashboard" in page:
    from pages.dashboard import show; show()
elif "Nueva Ficha" in page:
    from pages.nueva_ficha import show; show()
elif "Historial" in page:
    from pages.historial import show; show()
elif "Clientes" in page:
    from pages.clientes import show; show()
