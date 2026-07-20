#!/usr/bin/env python3
"""
Installer script for KognitoAI KAI-Ethno Extension.
"""

import os
import sys
import shutil
import subprocess

EXT_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_kognito_base() -> str:
    """Detect KognitoAI installation directory."""
    candidates = [
        os.path.abspath(os.path.join(EXT_DIR, "../../kognito-ai")),  # Relative inside repo
        os.path.abspath(os.path.join(EXT_DIR, "../kognito-ai")),
        os.path.expanduser("~/KognitoAI"),                        # Standard install path
        os.path.abspath(os.path.join(EXT_DIR, "../..")),           # Parent fallback
    ]
    for path in candidates:
        if os.path.isfile(os.path.join(path, "run_api.py")) or os.path.isdir(os.path.join(path, "core")):
            return path
    raise RuntimeError(
        "No se encontró la instalación de KognitoAI. "
        "Asegúrate de que KognitoAI esté instalado en ~/KognitoAI o en la carpeta kognito-ai."
    )


BASE_DIR = _find_kognito_base()
TARGET_SKILL_DIR = os.path.join(BASE_DIR, "skills", "kai_ethno_skill")
SRC_SKILL_DIR = os.path.join(EXT_DIR, "skill")


def _get_python_executable():
    """Find the appropriate python executable (preferring project venv)."""
    venv_candidates = [
        os.path.join(BASE_DIR, ".venv", "bin", "python"),
        os.path.join(BASE_DIR, "..", ".venv", "bin", "python"),
        os.path.join(BASE_DIR, "venv", "bin", "python"),
        os.path.join(BASE_DIR, "venv_host", "bin", "python"),
    ]
    for candidate in venv_candidates:
        candidate_path = os.path.abspath(candidate)
        if os.path.isfile(candidate_path) and os.access(candidate_path, os.X_OK):
            return candidate_path
    return sys.executable


def _install_requirements():
    req_file = os.path.join(SRC_SKILL_DIR, "requirements.txt")
    if os.path.exists(req_file):
        python_bin = _get_python_executable()
        print(f"  → Instalando dependencias usando {python_bin}...")
        cmd = [python_bin, "-m", "pip", "install", "-r", req_file]
        # Si no estamos en un venv, añadir --break-system-packages para entornos Linux modernos
        if "venv" not in python_bin:
            cmd.append("--break-system-packages")
        try:
            subprocess.run(cmd, check=True)
            print("  ✓ Dependencias de Python instaladas con éxito.")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠ Advertencia: Error al instalar dependencias con pip: {e}")


def _copy_skill_files():
    print(f"  → Instalando skill en: {TARGET_SKILL_DIR}")
    
    if os.path.abspath(SRC_SKILL_DIR) == os.path.abspath(TARGET_SKILL_DIR):
        print("  ✓ La skill ya se encuentra en la ubicación de destino.")
        return

    # Si ya existe el directorio de destino, lo actualizamos
    if os.path.exists(TARGET_SKILL_DIR):
        shutil.rmtree(TARGET_SKILL_DIR)
        
    shutil.copytree(SRC_SKILL_DIR, TARGET_SKILL_DIR)
    print("  ✓ Archivos de la skill copiados correctamente.")


def install():
    print("🚀 Instalando extensión KAI-Ethno (Investigación Antropológica) para KognitoAI...")
    print(f"   Directorio base detectado: {BASE_DIR}")
    
    _install_requirements()
    _copy_skill_files()
    
    print("\n✅ ¡Extensión KAI-Ethno instalada exitosamente en KognitoAI!")
    print("   El agente de KognitoAI ahora dispone de las herramientas de investigación etnográfica.")


if __name__ == "__main__":
    install()
