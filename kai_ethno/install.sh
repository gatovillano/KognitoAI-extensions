#!/usr/bin/env bash

# KAI-Ethno - Extension Installer
# Installs the KAI-Ethno extension into an existing KognitoAI installation.

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🧩 Instalador de Extensión: KAI-Ethno (Investigación Antropológica)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Detect Python
PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -f "${SCRIPT_DIR}/install.py" ]; then
    ${PYTHON_CMD} "${SCRIPT_DIR}/install.py"
else
    echo -e "${RED}❌ Error: No se encontró install.py en ${SCRIPT_DIR}${NC}"
    exit 1
fi
