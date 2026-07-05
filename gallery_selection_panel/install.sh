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

# 1. Detect target KognitoAI directory (prioritizing the home directory installation)
DEFAULT_REPO_DIR="${HOME}/KognitoAI"
if [ ! -d "${DEFAULT_REPO_DIR}" ] && [ -f "${KOGNITO_CONFIG}" ]; then
    CONFIG_REPO_DIR=$(grep -E '^KOGNITO_REPO_DIR=' "${KOGNITO_CONFIG}" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    DEFAULT_REPO_DIR="${CONFIG_REPO_DIR:-${DEFAULT_REPO_DIR}}"
fi

echo -e "  Instalación de Kognito AI detectada: ${BOLD}${DEFAULT_REPO_DIR}${NC}"
printf "  ¿Instalar en esta ruta? [S/n]: "
read -r CONFIRM_PATH

if [[ "${CONFIRM_PATH}" =~ ^[nN]$ ]]; then
    printf "  Por favor ingresa la ruta de destino: "
    read -r KOGNITO_DIR
else
    KOGNITO_DIR="${DEFAULT_REPO_DIR}"
fi

# Expand tilde ~ if user entered it
KOGNITO_DIR="${KOGNITO_DIR/#\~/$HOME}"

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
    # Running inside the already-cloned extensions repo
    echo -e "${BLUE}📦 Copiando extensión local a la carpeta de extensiones de KognitoAI...${NC}"
    rm -rf "${TARGET_GALLERY_DIR}"
    cp -r "${SCRIPT_DIR}" "${TARGET_GALLERY_DIR}"
else
    # Clone/update extensions repo from github
    echo -e "${YELLOW}🌐 Descargando la extensión desde GitHub...${NC}"
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
    echo -e "${RED}❌ No se encontró el entorno virtual en ${KOGNITO_DIR}/venv_host.${NC}"
    exit 1
fi

# 4. Prompt Option Menu (or auto-select via argument)
OPTION=""
if [ "$1" == "--uninstall" ]; then
    OPTION="2"
fi

if [ -z "${OPTION}" ]; then
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${GREEN}1)${NC} 📸 Instalar KogniPhotos Gallery"
    echo -e "  ${RED}2)${NC} 🗑️  Desinstalar (restaurar galería original)"
    echo -e "  ${YELLOW}3)${NC} ❌ Salir"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    printf "  Selecciona una opción [1-3]: "
    read -r OPTION
fi

case "${OPTION}" in
    1)
        echo -e "\n${GREEN}🚀 Instalando extensión KogniPhotos...${NC}"
        (cd "${KOGNITO_DIR}" && PYTHONPATH=. "${PYTHON}" "${TARGET_GALLERY_DIR}/install.py")
        ;;
    2)
        echo -e "\n${YELLOW}🔄 Desinstalando extensión KogniPhotos...${NC}"
        (cd "${KOGNITO_DIR}" && PYTHONPATH=. "${PYTHON}" "${TARGET_GALLERY_DIR}/install.py" --uninstall)
        echo -e "${YELLOW}🗑️  Eliminando archivos de la extensión...${NC}"
        rm -rf "${TARGET_GALLERY_DIR}"
        echo -e "${GREEN}✅ Extensión desinstalada con éxito.${NC}"
        ;;
    3)
        echo "Saliendo."
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Opción no reconocida. Ejecutando instalación...${NC}"
        (cd "${KOGNITO_DIR}" && PYTHONPATH=. "${PYTHON}" "${TARGET_GALLERY_DIR}/install.py")
        ;;
esac

