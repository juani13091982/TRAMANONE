#!/bin/bash
# AGM Performance — Launcher para Mac/Linux
echo ""
echo "============================================"
echo " AGM PERFORMANCE - Sistema de Service"
echo "============================================"
echo ""
echo " Iniciando aplicacion..."
echo " Abre tu navegador en: http://localhost:8501"
echo " Para cerrar: Ctrl+C"
echo ""

cd "$(dirname "$0")"

# Instalar deps si faltan
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo " Instalando dependencias..."
    pip3 install -r requirements.txt
fi

python3 -m streamlit run app.py --server.port 8501
