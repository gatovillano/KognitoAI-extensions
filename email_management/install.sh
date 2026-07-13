#!/bin/bash
# Wrapper script to run the installer inside KognitoAI's virtual environment.

set -e

# Find the Python virtual environment
VENV_PATH="/home/gato/KognitoAI/venv_host"

if [ -d "$VENV_PATH" ]; then
    echo "🐍 Activando entorno virtual de KognitoAI..."
    source "$VENV_PATH/bin/activate"
    python install.py "$@"
else
    echo "⚠ Entorno virtual no encontrado en $VENV_PATH. Ejecutando con python3 del sistema..."
    python3 install.py "$@"
fi
