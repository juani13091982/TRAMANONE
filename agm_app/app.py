"""
AGM Performance — Sistema de Gestión de Service
Aplicación Streamlit principal
"""
import streamlit as st
from database import init_db

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
/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D0D 0%, #1A1A1A 100%);
}
[data-testid="stSidebar"] * { color: #EEEEEE !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 14px; }

/* Header strip */
.agm-header {
    background: linear-gradient(90deg, #1A1A1A 0%, #2A2A2A 100%);
    border-left: 5px solid #CC0000;
    padding: 12px 20px 8px 20px;
    border-radius: 4px;
    margin-bottom: 18px;
}
.agm-header h2 { color: #FFFFFF !important; margin: 0; font-size: 22px; }
.agm-header span { color: #CC0000; font-weight: bold; font-size: 12px; letter-spacing: 2px; }

/* KPI cards */
.kpi-card {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-top: 3px solid #CC0000;
    border-radius: 6px;
    padding: 16px 20px;
    text-align: center;
    color: white;
}
.kpi-card .kpi-value { font-size: 32px; font-weight: 800; color: #CC0000; }
.kpi-card .kpi-label { font-size: 11px; color: #AAAAAA; letter-spacing: 1px; text-transform: uppercase; }
.kpi-card .kpi-sub   { font-size: 12px; color: #DDDDDD; }

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
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("../LOGO TRAMA.JPG.jpeg", width=180)
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
