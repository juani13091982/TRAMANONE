@echo off
title AGM Performance — Service Manager
echo.
echo  ============================================
echo   AGM PERFORMANCE - Sistema de Service
echo  ============================================
echo.
echo  Iniciando aplicacion...
echo  Una vez cargada, se abrira en tu navegador.
echo  Para cerrar: presiona Ctrl+C o cierra esta ventana.
echo.

cd /d "%~dp0"

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python no esta instalado.
    echo  Baja Python desde: https://python.org
    echo  Asegurate de marcar "Add to PATH" durante la instalacion.
    pause
    exit /b 1
)

REM Instalar dependencias si no estan
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo  Instalando dependencias por primera vez...
    pip install -r requirements.txt
)

REM Arrancar Streamlit
streamlit run app.py --server.port 8501

pause
