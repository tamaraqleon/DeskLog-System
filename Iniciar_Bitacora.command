#!/bin/bash
cd "$(dirname "$0")"

# 1. Verificar si Python está instalado en el Mac
if ! command -v python3 &> /dev/null
then
    echo "[ATENCIÓN] No se encontró Python instalado en este Mac."
    echo "Por favor instálalo desde python.org o asegúrate de tenerlo listo."
    exit
fi

# 2. Verificar si Streamlit está instalado, si no, instalarlo automáticamente
if ! python3 -c "import streamlit" &> /dev/null
then
    echo "[INFO] Instalando dependencias por primera vez..."
    python3 -m pip install --upgrade pip
    python3 -m pip install streamlit
fi

# 3. Iniciar la aplicación
echo "[INFO] Abriendo la Bitácora de Recepción..."
python3 -m streamlit run app.py