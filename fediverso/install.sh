#!/usr/bin/env bash
set -e

# Obtener directorio del script
# Detectar ubicación del script o archivos locales
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -f "$SCRIPT_DIR/install.py" ]; then
    INSTALLER_PATH="$SCRIPT_DIR/install.py"
elif [ -f "./install.py" ]; then
    INSTALLER_PATH="./install.py"
elif [ -f "./fediverso/install.py" ]; then
    INSTALLER_PATH="./fediverso/install.py"
else
    echo "⚠ No se encontró install.py localmente. Por favor, asegúrate de estar dentro del repositorio clonado."
    exit 1
fi

echo "Iniciando instalación de la extensión del Fediverso..."

# Usar el venv de KognitoAI si existe para evitar problemas de dependencias en python
VENV_PATH="/home/gato/KognitoAI/venv_host"
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Ejecutando instalador con el entorno virtual de KognitoAI..."
    "$VENV_PATH/bin/python" "$INSTALLER_PATH" "$@"
else
    python3 "$INSTALLER_PATH" "$@"
fi

echo "¡Listo! La instalación de Fediverso ha concluido."
