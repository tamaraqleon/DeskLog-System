@echo off
cd /d "%~dp0"

:: 1. Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATENCION] No se encontro Python instalado en este equipo.
    echo Por favor instalalo desde python.org y asegurate de marcar la casilla "Add Python to PATH".
    pause
    exit
)

:: 2. Verificar si Streamlit y Supabase estan instalados, si no, instalarlos
python -c "import streamlit, supabase" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Instalando dependencias por primera vez...
    python -m pip install --upgrade pip
    python -m pip install streamlit supabase
)

:: 3. Iniciar la aplicacion
echo [INFO] Abriendo la Bitacora de Recepcion...
python -m streamlit run app.py