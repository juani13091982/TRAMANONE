"""
Caché central de datos — AGM Performance.
Todas las páginas leen de acá. TTL largo (5 min) porque cada operación
de escritura llama a clear_all(), así el caché nunca queda desactualizado.
"""
import streamlit as st
from database import (get_stats, get_servicios_full, get_clientes,
                      get_motos_cliente, get_stats_clientes)

TTL = 300  # 5 minutos


@st.cache_data(ttl=TTL, show_spinner=False)
def stats():
    return get_stats()


@st.cache_data(ttl=TTL, show_spinner=False)
def servicios_recientes():
    return get_servicios_full(limit=10)


@st.cache_data(ttl=TTL, show_spinner=False)
def servicios_full():
    return get_servicios_full(limit=500)


@st.cache_data(ttl=TTL, show_spinner=False)
def clientes():
    return get_clientes()


@st.cache_data(ttl=TTL, show_spinner=False)
def motos_de(cliente_id):
    return get_motos_cliente(cliente_id)


@st.cache_data(ttl=TTL, show_spinner=False)
def stats_clientes():
    return get_stats_clientes()


def clear_all():
    """Invalida todo el caché. Llamar después de guardar/editar/eliminar."""
    for f in (stats, servicios_recientes, servicios_full,
              clientes, motos_de, stats_clientes):
        f.clear()
