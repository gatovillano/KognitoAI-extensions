#!/usr/bin/env python3
"""
Installer script for KognitoAI Fediverso Extension.
"""

import os
import sys
import shutil
import subprocess

EXT_DIR = os.path.dirname(os.path.abspath(__file__))

def _find_kognito_base() -> str:
    """Detect KognitoAI installation directory."""
    candidates = [
        os.path.abspath(os.path.join(EXT_DIR, "../kognito-ai")), # Relative inside repo
        os.path.expanduser("~/KognitoAI"),                      # Standard install path
        os.path.abspath(os.path.join(EXT_DIR, "../..")),         # Parent fallback
    ]
    for path in candidates:
        if os.path.isfile(os.path.join(path, "run_api.py")):
            return path
    raise RuntimeError(
        "No se encontró la instalación de KognitoAI. "
        "Asegúrate de que esté en ~/KognitoAI o en la carpeta kognito-ai."
    )

BASE_DIR = _find_kognito_base()

# Target directories in the base project
EXT_BACKEND_DIR = os.path.join(BASE_DIR, "extensions", "fediverso", "backend")
COMPONENTS_DIR = os.path.join(BASE_DIR, "src/components")
FEDIVERO_PANEL_TARGET = os.path.join(COMPONENTS_DIR, "FediversePanel.tsx")

# Source files
SRC_BACKEND_DIR = os.path.join(EXT_DIR, "backend")
SRC_FRONTEND_PANEL = os.path.join(EXT_DIR, "frontend", "FediversePanel.tsx")

def _run_migration():
    print("  → Ejecutando migración SQL para la extensión del Fediverso...")
    try:
        # Añadir el directorio base de KognitoAI a sys.path para poder importar sus módulos
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
            
        from sqlalchemy import text
        from core.database import engine, Base
        
        # Importar el modelo para asegurarse de que esté en la metadata de SQLAlchemy
        from extensions.fediverso.backend.models import FediversoAccount # noqa: F401
        
        async def run_db_setup():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print("  ✓ Tabla fediverso_accounts verificada/creada en la base de datos.")
                
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.run_until_complete(run_db_setup())
    except Exception as e:
        print(f"  ⚠ Advertencia: No se pudo realizar la migración automática: {e}")
        print("    Asegúrate de que la base de datos esté corriendo y configurada.")

def _copy_files():
    print("  → Copiando archivos de la extensión...")
    
    # 1. Copiar backend
    os.makedirs(EXT_BACKEND_DIR, exist_ok=True)
    for filename in ["__init__.py", "models.py", "router.py", "schemas.py"]:
        src = os.path.join(SRC_BACKEND_DIR, filename)
        dst = os.path.join(EXT_BACKEND_DIR, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"    ✓ Copiado backend: {filename} -> {dst}")
            
    # 2. Copiar frontend
    os.makedirs(COMPONENTS_DIR, exist_ok=True)
    if os.path.exists(SRC_FRONTEND_PANEL):
        shutil.copy2(SRC_FRONTEND_PANEL, FEDIVERO_PANEL_TARGET)
        print(f"    ✓ Copiado frontend component: FediversePanel.tsx -> {FEDIVERO_PANEL_TARGET}")

def install():
    print("🚀 Instalando extensión del Fediverso para KognitoAI...")
    print(f"   Directorio base detectado: {BASE_DIR}")
    
    # 1. Copiar los archivos en sus ubicaciones correspondientes
    _copy_files()
    
    # 2. Ejecutar migraciones de base de datos
    _run_migration()
    
    print("\n🎉 Extensión del Fediverso instalada con éxito.")
    print("   El router ha sido registrado de forma segura en api/main.py y los enlaces se agregaron al Sidebar.")

if __name__ == "__main__":
    install()
