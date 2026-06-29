#!/usr/bin/env bash

# KogniPhotos Gallery Selection Panel - Remote Installer
# Installs the extension into an existing KognitoAI installation.
# Can be run directly from GitHub:
#   curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/gallery_selection_panel/install.sh | bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

EXT_REPO_URL="https://github.com/gatovillano/KognitoAI-extensions.git"
EXT_REPO_DIR="${HOME}/KognitoAI-extensions"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}  📸 KogniPhotos Gallery Selection Panel${NC}"
echo -e "${BOLD}  Instalador de Extensión${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Detect KognitoAI installation
if [ -f "${HOME}/KognitoAI/run_api.py" ]; then
    KOGNITO_DIR="${HOME}/KognitoAI"
elif [ -f "./run_api.py" ]; then
    KOGNITO_DIR="$(pwd)"
else
    echo -e "${RED}❌ No se encontró KognitoAI en ~/KognitoAI.${NC}"
    echo -e "   Ejecuta primero el instalador principal de KognitoAI."
    exit 1
fi
echo -e "  KognitoAI detectado en: ${GREEN}${KOGNITO_DIR}${NC}"

# Ensure extensions repo is available
if [ -n "${SCRIPT_DIR}" ] && [ -f "${SCRIPT_DIR}/install.py" ]; then
    # Running inside the already-cloned extensions repo
    EXT_GALLERY_DIR="${SCRIPT_DIR}"
else
    # Clone/update extensions repo
    if [ ! -d "${EXT_REPO_DIR}" ]; then
        echo -e "${YELLOW}🌐 Clonando repositorio de extensiones...${NC}"
        git clone "${EXT_REPO_URL}" "${EXT_REPO_DIR}"
    else
        echo -e "${YELLOW}🔄 Actualizando repositorio de extensiones...${NC}"
        git -C "${EXT_REPO_DIR}" fetch origin && git -C "${EXT_REPO_DIR}" reset --hard origin/main || true
    fi
    EXT_GALLERY_DIR="${EXT_REPO_DIR}/gallery_selection_panel"
fi

PYTHON="${KOGNITO_DIR}/venv_host/bin/python"
if [ ! -f "${PYTHON}" ]; then
    echo -e "${RED}❌ No se encontró el entorno virtual en ${KOGNITO_DIR}/venv_host.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${GREEN}1)${NC} 📸 Instalar KogniPhotos Gallery"
echo -e "  ${RED}2)${NC} 🗑️  Desinstalar (restaurar galería original)"
echo -e "  ${YELLOW}3)${NC} ❌ Salir"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
printf "  Selecciona una opción [1-3]: "
read -r OPTION

case "${OPTION}" in
    1)
        echo -e "\n${GREEN}🚀 Instalando extensión KogniPhotos...${NC}"
        (cd "${KOGNITO_DIR}" && PYTHONPATH=. "${PYTHON}" "${EXT_GALLERY_DIR}/install.py")
        ;;
    2)
        echo -e "\n${YELLOW}🔄 Desinstalando extensión KogniPhotos...${NC}"
        (cd "${KOGNITO_DIR}" && PYTHONPATH=. "${PYTHON}" "${EXT_GALLERY_DIR}/install.py" --uninstall)
        ;;
    3)
        echo "Saliendo."
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Opción no reconocida. Ejecutando instalación...${NC}"
        (cd "${KOGNITO_DIR}" && PYTHONPATH=. "${PYTHON}" "${EXT_GALLERY_DIR}/install.py")
        ;;
esac
