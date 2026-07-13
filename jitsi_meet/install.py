#!/usr/bin/env python3
"""
Installer script for KognitoAI Jitsi Meet Extension.

Usage:
  python install.py           Installs/Enables the extension, builds frontend & restarts server
  python install.py --uninstall Reverts KognitoAI to its stock base state
"""

import os
import sys
import shutil
import asyncio
import subprocess

EXT_DIR = os.path.dirname(os.path.abspath(__file__))


def _find_kognito_base() -> str:
    """Detect KognitoAI installation directory."""
    candidates = [
        os.path.expanduser("~/KognitoAI"),  # Standard install
        os.path.abspath(os.path.join(EXT_DIR, "../..")),  # Inside extensions/ dir
    ]
    for path in candidates:
        if os.path.isfile(os.path.join(path, "run_api.py")):
            return path
    raise RuntimeError(
        "No se encontró la instalación de KognitoAI. "
        "Asegúrate de que esté en ~/KognitoAI o ejecuta el instalador principal primero."
    )


BASE_DIR = _find_kognito_base()

# Paths for Frontend Modifications
MEET_PAGE_TARGET = os.path.join(BASE_DIR, "src/app/(dashboard)/meet/page.tsx")
MEET_PAGE_BACKUP = os.path.join(BASE_DIR, "src/app/(dashboard)/meet/page.tsx.bak")
SIDEBAR_TARGET = os.path.join(BASE_DIR, "src/components/Sidebar.tsx")
SIDEBAR_BACKUP = os.path.join(BASE_DIR, "src/components/Sidebar.tsx.bak")

# Paths for Backend Modifications
API_MAIN_TARGET = os.path.join(BASE_DIR, "api/main.py")
API_MAIN_BACKUP = os.path.join(BASE_DIR, "api/main.py.bak")

# Component installation paths in the base project
COMPONENTS_DIR = os.path.join(BASE_DIR, "src/components")
JITSI_PANEL_TARGET = os.path.join(COMPONENTS_DIR, "JitsiMeetPanel.tsx")

# Internal import paths (within the project)
JITSI_PANEL_IMPORT_PATH = "@/components/JitsiMeetPanel"

# Extension backend router path
EXT_ROUTER_PATH = os.path.join(EXT_DIR, "backend", "router.py")
EXT_MODELS_PATH = os.path.join(EXT_DIR, "backend", "models.py")

# Database migration
MIGRATION_DIR = os.path.join(BASE_DIR, "migrations")
MIGRATION_FILE = os.path.join(MIGRATION_DIR, "create_jitsi_rooms_table.sql")

# Extension backend installation paths in the base project
EXT_BACKEND_DIR = os.path.join(BASE_DIR, "extensions", "jitsi_meet", "backend")


def _ensure_migration_dir():
    os.makedirs(MIGRATION_DIR, exist_ok=True)


def _create_migration():
    _ensure_migration_dir()
    migration_sql = """
-- Jitsi Meet Extension: create jitsi_rooms table
CREATE TABLE IF NOT EXISTS jitsi_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    album_id UUID REFERENCES albums(id) ON DELETE SET NULL,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    room_name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    password VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_jitsi_rooms_account_id ON jitsi_rooms(account_id);
CREATE INDEX IF NOT EXISTS idx_jitsi_rooms_album_id ON jitsi_rooms(album_id);
"""
    with open(MIGRATION_FILE, "w", encoding="utf-8") as f:
        f.write(migration_sql)
    print(f"  ✓ Archivo de migración SQL creado en: {MIGRATION_FILE}")


def _run_migration():
    print("  → Ejecutando migración SQL...")
    try:
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        from sqlalchemy import text
        from core.database import engine, Base
        from extensions.jitsi_meet.backend.models import JitsiRoom  # noqa: F401 - ensure model is loaded

        async def run_db_setup():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # Alter the column to make album_id nullable (DROP NOT NULL) if the table already existed
                await conn.execute(text("ALTER TABLE jitsi_rooms ALTER COLUMN album_id DROP NOT NULL;"))

        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(run_db_setup())
        print("  ✓ Tabla jitsi_rooms creada/verificada en la base de datos (album_id es opcional).")
    except Exception as e:
        print(f"  ⚠ No se pudo crear/actualizar la tabla automáticamente: {e}")
        print("    Aplica manualmente el archivo SQL de migración si es necesario.")


def _copy_frontend_component():
    src = os.path.join(EXT_DIR, "frontend", "JitsiMeetPanel.tsx")
    dst = JITSI_PANEL_TARGET
    shutil.copy2(src, dst)
    print(f"  ✓ Componente frontend copiado a: {dst}")


def _remove_frontend_component():
    if os.path.exists(JITSI_PANEL_TARGET):
        os.remove(JITSI_PANEL_TARGET)
        print(f"  ✓ Componente frontend eliminado: {JITSI_PANEL_TARGET}")


def _inject_backend_router():
    with open(API_MAIN_TARGET, "r", encoding="utf-8") as f:
        content = f.read()

    extension_import_line = "from extensions.jitsi_meet.backend.router import router as jitsi_meet_router"
    router_call_line = "app.include_router(jitsi_meet_router)"

    if extension_import_line in content and router_call_line in content:
        print("  ✓ Router de extensión ya estaba inyectado en api/main.py.")
        return

    import_block = "from api.routers import "
    if import_block in content:
        content = content.replace(
            import_block,
            f"{import_block}\n{extension_import_line}",
            1,
        )
    else:
        content = f"{extension_import_line}\n{content}"

    if router_call_line not in content:
        # Intentar insertar después de la extensión de galerías como ancla
        anchor = "app.include_router(gallery_selection_extension_router)"
        if anchor in content:
            content = content.replace(
                anchor,
                f"{anchor}\n{router_call_line}",
                1,
            )
        else:
            # Fallback: insertar después de la última línea de include_router conocida
            fallback_anchor = 'app.include_router(openai_router, prefix="", tags=["openai-compatible"])'
            if fallback_anchor in content:
                content = content.replace(
                    fallback_anchor,
                    f"{fallback_anchor}\n{router_call_line}",
                    1,
                )
            else:
                # Último recurso: agregar al final del archivo
                content = content.rstrip() + f"\n{router_call_line}\n"

    with open(API_MAIN_TARGET, "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✓ Router de extensión inyectado en api/main.py.")


def _remove_backend_router():
    if not os.path.exists(API_MAIN_TARGET):
        return

    with open(API_MAIN_TARGET, "r", encoding="utf-8") as f:
        content = f.read()

    extension_import_line = "from extensions.jitsi_meet.backend.router import router as jitsi_meet_router"
    router_call_line = "app.include_router(jitsi_meet_router)"

    if extension_import_line in content or router_call_line in content:
        lines = content.splitlines(keepends=True)
        lines = [
            l for l in lines
            if extension_import_line not in l and router_call_line not in l
        ]
        content = "".join(lines)
        with open(API_MAIN_TARGET, "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✓ Inyección de router eliminada de api/main.py.")


def _install_backend():
    os.makedirs(EXT_BACKEND_DIR, exist_ok=True)
    for filename in ["__init__.py", "models.py", "router.py", "schemas.py"]:
        src = os.path.join(EXT_DIR, "backend", filename)
        dst = os.path.join(EXT_BACKEND_DIR, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    print(f"  ✓ Backend de extensión copiado a: {EXT_BACKEND_DIR}")


def _remove_backend():
    if os.path.isdir(EXT_BACKEND_DIR):
        shutil.rmtree(EXT_BACKEND_DIR)
        print(f"  ✓ Backend de extensión eliminado: {EXT_BACKEND_DIR}")
def _create_meet_page():
    page_content = f"""\"use client\";

import {{ JitsiMeetPanel }} from \'{JITSI_PANEL_IMPORT_PATH}\';

export default function MeetPage() {{
  return (
    <div className=\"space-y-6\">
      <div>
        <h1 className=\"text-3xl font-bold tracking-tight\">Meet</h1>
        <p className=\"text-muted-foreground\">
          Administra tus salas de Jitsi Meet y colabora en tiempo real.
        </p>
      </div>
      <JitsiMeetPanel />
    </div>
  );
}}
"""

    if os.path.exists(MEET_PAGE_TARGET):
        with open(MEET_PAGE_TARGET, "r", encoding="utf-8") as f:
            existing = f.read()
        if "JitsiMeetPanel" in existing:
            print("  ✓ Página Meet ya estaba creada.")
            return

    os.makedirs(os.path.dirname(MEET_PAGE_TARGET), exist_ok=True)
    with open(MEET_PAGE_TARGET, "w", encoding="utf-8") as f:
        f.write(page_content)
    print(f"  ✓ Página Meet creada en: {MEET_PAGE_TARGET}")


def _remove_meet_page():
    if os.path.exists(MEET_PAGE_TARGET):
        os.remove(MEET_PAGE_TARGET)
        print(f"  ✓ Página Meet eliminada: {MEET_PAGE_TARGET}")


def _inject_sidebar():
    if not os.path.exists(SIDEBAR_TARGET):
        print("  ⚠ Sidebar.tsx no encontrado.")
        return

    with open(SIDEBAR_TARGET, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Asegurar la importación del ícono Video
    if "Video" not in content:
        import_marker = "} from 'lucide-react';"
        if import_marker in content:
            content = content.replace(import_marker, ", Video } from 'lucide-react';", 1)
            print("  ✓ Importación de Video agregada a Sidebar.tsx.")

    # 2. Inyectar el botón
    meet_link = 'href="/meet"'
    if meet_link in content:
        print("  ✓ Botón Meet ya estaba inyectado en Sidebar.tsx.")
        return

    workspace_link = '<Link href="/workspaces" passHref onClick={onLinkClick} title="Workspaces" className="w-full block">'
    if workspace_link in content:
        meet_button = """            <Link href="/meet" passHref onClick={onLinkClick} title="Meet" className="w-full block">
              <Button
                variant={pathname?.startsWith('/meet') ? 'secondary' : 'ghost'}
                className={cn(
                  "w-full transition-all duration-300 hover:bg-primary/10 hover:text-primary rounded-xl group",
                  isCollapsed ? "justify-center h-9 w-9 p-0" : "justify-start h-9 px-2",
                  pathname?.startsWith('/meet') && "bg-primary/10 text-primary border border-primary/20"
                )}
              >
                <Video className={cn("h-4 w-4 transition-transform group-hover:scale-110", showToolText && "mr-2")} />
                {showToolText && <span className="text-sm font-medium">Meet</span>}
              </Button>
            </Link>

"""
        content = content.replace(workspace_link, f"{meet_button}{workspace_link}", 1)
        with open(SIDEBAR_TARGET, "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✓ Botón Meet inyectado en Sidebar.tsx.")
    else:
        print("  ⚠ No se encontró el marcador de Workspaces en Sidebar.tsx para inyectar el botón.")


def _remove_sidebar():
    if not os.path.exists(SIDEBAR_TARGET):
        return

    with open(SIDEBAR_TARGET, "r", encoding="utf-8") as f:
        content = f.read()

    # Restaurar la importación del ícono Video si se inyectó
    if ", Video } from 'lucide-react';" in content:
        content = content.replace(", Video } from 'lucide-react';", "} from 'lucide-react';", 1)

    # Eliminar el bloque del botón
    meet_button = """            <Link href="/meet" passHref onClick={onLinkClick} title="Meet" className="w-full block">
              <Button
                variant={pathname?.startsWith('/meet') ? 'secondary' : 'ghost'}
                className={cn(
                  "w-full transition-all duration-300 hover:bg-primary/10 hover:text-primary rounded-xl group",
                  isCollapsed ? "justify-center h-9 w-9 p-0" : "justify-start h-9 px-2",
                  pathname?.startsWith('/meet') && "bg-primary/10 text-primary border border-primary/20"
                )}
              >
                <Video className={cn("h-4 w-4 transition-transform group-hover:scale-110", showToolText && "mr-2")} />
                {showToolText && <span className="text-sm font-medium">Meet</span>}
              </Button>
            </Link>

"""
    if meet_button in content:
        content = content.replace(meet_button, "")
        with open(SIDEBAR_TARGET, "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✓ Botón Meet eliminado de Sidebar.tsx.")




def _run_build():
    print("  → Ejecutando build del frontend...")
    try:
        subprocess.run(
            ["npm", "run", "build"],
            cwd=BASE_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        print("  ✓ Build del frontend completado.")
    except FileNotFoundError:
        print("  ⚠ npm no encontrado, omitiendo build del frontend.")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ Error en build del frontend: {e.stderr}")


def _restart_local_servers():
    print("  → Reiniciando servidores locales...")
    scripts = ["restart_servers.sh", "restart.sh"]
    for script in scripts:
        path = os.path.join(BASE_DIR, script)
        if os.path.exists(path):
            try:
                subprocess.run(["bash", path], cwd=BASE_DIR, check=True, capture_output=True, text=True)
                print(f"  ✓ Servidores reiniciados con {script}.")
                return
            except Exception as e:
                print(f"  ⚠ Error al reiniciar con {script}: {e}")
    print("  ⚠ No se encontró script de reinicio. Reinicia manualmente si es necesario.")


def install():
    print("🚀 Instalando extensión Jitsi Meet para KognitoAI...")
    print(f"   Directorio base detectado: {BASE_DIR}")

    # 1. Backup
    for src, dst in [
        (MEET_PAGE_TARGET, MEET_PAGE_BACKUP),
        (API_MAIN_TARGET, API_MAIN_BACKUP),
        (SIDEBAR_TARGET, SIDEBAR_BACKUP),
    ]:
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  ✓ Copia de seguridad creada: {dst}")
        elif os.path.exists(dst):
            print(f"  ✓ Copia de seguridad ya existente: {dst}")

    # 2. Database
    _create_migration()
    _run_migration()

    # 3. Frontend
    _copy_frontend_component()
    _create_meet_page()
    _inject_sidebar()

    # 4. Backend
    _install_backend()
    _inject_backend_router()

    # 5. Build & Restart
    _run_build()
    _restart_local_servers()

    print("\n🎉 Extensión Jitsi Meet instalada correctamente.")
    print("   Accede al panel desde /meet en el dashboard.")


def uninstall():
    print("🗑️  Desinstalando extensión Jitsi Meet para KognitoAI...")

    # 1. Restore backups if available
    for src, dst in [
        (MEET_PAGE_BACKUP, MEET_PAGE_TARGET),
        (API_MAIN_BACKUP, API_MAIN_TARGET),
        (SIDEBAR_BACKUP, SIDEBAR_TARGET),
    ]:
        if os.path.exists(dst) and os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  ✓ {dst} restaurado desde copia de seguridad.")
        elif os.path.exists(dst):
            print(f"  ⚠ No se encontró copia de seguridad para {dst}, se omite restauración.")

    # 2. Remove injected changes
    _remove_meet_page()
    _remove_frontend_component()
    _remove_sidebar()
    _remove_backend_router()

    # 3. Remove migration file
    if os.path.exists(MIGRATION_FILE):
        os.remove(MIGRATION_FILE)
        print(f"  ✓ Archivo de migración eliminado: {MIGRATION_FILE}")

    # 4. Rebuild & Restart
    _run_build()
    _restart_local_servers()

    print("\n🎉 Extensión desinstalada correctamente y sistema base restaurado.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        uninstall()
    else:
        install()
