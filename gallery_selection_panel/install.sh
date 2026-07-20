#!/usr/bin/env bash

# KogniPhotos Gallery Selection Panel - Extension Installer
# Installs the extension into an existing KognitoAI installation.
# Can be run locally or directly from GitHub via curl.

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

EXT_REPO_URL="https://github.com/gatovillano/KognitoAI-extensions.git"
KOGNITO_CONFIG="${HOME}/.kognito/config/.env"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🧩 Instalador de Extensión: KogniPhotos / Gallery Selection${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 1. Detect target KognitoAI directory
DEFAULT_REPO_DIR="${HOME}/KognitoAI"
if [ ! -d "${DEFAULT_REPO_DIR}" ] && [ -f "${KOGNITO_CONFIG}" ]; then
    CONFIG_REPO_DIR=$(grep -E '^KOGNITO_REPO_DIR=' "${KOGNITO_CONFIG}" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    DEFAULT_REPO_DIR="${CONFIG_REPO_DIR:-${DEFAULT_REPO_DIR}}"
fi

if [ ! -d "${DEFAULT_REPO_DIR}" ] && [ -d "${HOME}/Proyectos/KognitoAI" ]; then
    DEFAULT_REPO_DIR="${HOME}/Proyectos/KognitoAI"
fi

if [ ! -d "${DEFAULT_REPO_DIR}" ] && [ -f "${PWD}/run_api.py" ]; then
    DEFAULT_REPO_DIR="${PWD}"
fi

KOGNITO_DIR="${DEFAULT_REPO_DIR}"
echo -e "  Ruta de Kognito AI: ${BOLD}${KOGNITO_DIR}${NC}"

if [ ! -d "${KOGNITO_DIR}" ] || [ ! -f "${KOGNITO_DIR}/run_api.py" ]; then
    echo -e "${RED}❌ Error: No se encontró la instalación de Kognito AI en: ${BOLD}${KOGNITO_DIR}${NC}"
    exit 1
fi

# 2. Ensure target extensions directory exists inside KognitoAI
TARGET_EXTENSIONS_DIR="${KOGNITO_DIR}/extensions"
TARGET_GALLERY_DIR="${TARGET_EXTENSIONS_DIR}/gallery_selection_panel"
mkdir -p "${TARGET_EXTENSIONS_DIR}"

# 3. Download/clone from GitHub or copy local files
if [ -n "${SCRIPT_DIR}" ] && [ -f "${SCRIPT_DIR}/install.py" ]; then
    echo -e "${BLUE}📦 Copiando extensión local a la carpeta de extensiones de KognitoAI...${NC}"
    rm -rf "${TARGET_GALLERY_DIR}"
    cp -r "${SCRIPT_DIR}" "${TARGET_GALLERY_DIR}"
else
    echo -e "${YELLOW}🌐 Descargando extensión desde GitHub...${NC}"
    TMP_DIR=$(mktemp -d -t kognito_ext_XXXXXX)
    if git clone --depth 1 "${EXT_REPO_URL}" "${TMP_DIR}"; then
        rm -rf "${TARGET_GALLERY_DIR}"
        cp -r "${TMP_DIR}/gallery_selection_panel" "${TARGET_GALLERY_DIR}"
        rm -rf "${TMP_DIR}"
    else
        echo -e "${RED}❌ Error al clonar el repositorio desde GitHub.${NC}"
        rm -rf "${TMP_DIR}"
        exit 1
    fi
fi

PYTHON="${KOGNITO_DIR}/venv_host/bin/python"
if [ ! -f "${PYTHON}" ]; then
    PYTHON=$(command -v python3 || command -v python)
fi

# 4. Execute Installation
echo -e "\n${GREEN}🚀 Instalando extensión KogniPhotos...${NC}"
(cd "${KOGNITO_DIR}" && PYTHONPATH=. "${PYTHON}" "${TARGET_GALLERY_DIR}/install.py")
