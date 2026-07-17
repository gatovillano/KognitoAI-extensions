#!/usr/bin/env bash
set -e

# Obtener directorio del script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Iniciando instalación de la extensión del Fediverso..."

# Ejecutar el instalador de Python
python3 "$DIR/install.py"

echo "¡Listo! La instalación de Fediverso ha concluido."
