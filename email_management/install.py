#!/usr/bin/env python3
"""
Installer script for KogniMail KognitoAI Email Extension.

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
    candidates = [
        os.path.expanduser("~/KognitoAI"),
        os.path.abspath(os.path.join(EXT_DIR, "../..")),
        os.path.abspath(os.path.join(EXT_DIR, "../../kognito-ai")),
    ]
    for path in candidates:
        if os.path.isfile(os.path.join(path, "run_api.py")):
            return path
    raise RuntimeError(
        "No se encontró la instalación de KognitoAI. "
        "Asegúrate de que esté en ~/KognitoAI o ejecuta el instalador principal primero."
    )

BASE_DIR = _find_kognito_base()

# Target paths in the main repository
COMPONENTS_DIR = os.path.join(BASE_DIR, "src/components")
EMAIL_ROUTE_DIR = os.path.join(BASE_DIR, "src/app/(dashboard)/email")
EMAIL_ROUTE_FILE = os.path.join(EMAIL_ROUTE_DIR, "page.tsx")
API_MAIN_TARGET = os.path.join(BASE_DIR, "api/main.py")
SIDEBAR_TARGET = os.path.join(BASE_DIR, "src/components/Sidebar.tsx")
SETTINGS_TARGET = os.path.join(BASE_DIR, "src/app/(dashboard)/settings/page.tsx")

# Backup paths
API_MAIN_BACKUP = os.path.join(BASE_DIR, "api/main.py.bak")
SIDEBAR_BACKUP = os.path.join(BASE_DIR, "src/components/Sidebar.tsx.bak")
SETTINGS_BACKUP = os.path.join(BASE_DIR, "src/app/(dashboard)/settings/page.tsx.bak")

FRONTEND_FILES = [
    ("EmailInboxView.tsx", os.path.join(COMPONENTS_DIR, "EmailInboxView.tsx")),
    ("EmailComposeModal.tsx", os.path.join(COMPONENTS_DIR, "EmailComposeModal.tsx")),
    ("EmailSettingsModal.tsx", os.path.join(COMPONENTS_DIR, "EmailSettingsModal.tsx")),
    ("SafeHtmlViewer.tsx", os.path.join(COMPONENTS_DIR, "SafeHtmlViewer.tsx")),
]

IMPORT_LINE = "from api.email_management.router import router as email_extension_router"
ROUTER_INCLUDE_LINE = "app.include_router(email_extension_router)"

async def create_database_tables():
    print("\n🗄️ Inicializando tabla de base de datos para la extensión...")
    try:
        sys.path.insert(0, BASE_DIR)
        sys.path.insert(0, os.path.dirname(EXT_DIR))
        from sqlalchemy import text
        from core.database import engine, Base
        
        # Define model on the fly to avoid import path issues during install process
        import sqlalchemy as sa
        class UserEmailConfig(Base):
            __tablename__ = "user_email_configs"
            account_id = sa.Column(sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True)
            provider = sa.Column(sa.String(50), nullable=False, default="custom")
            imap_server = sa.Column(sa.String(255), nullable=True)
            imap_port = sa.Column(sa.Integer, nullable=True, default=993)
            imap_ssl = sa.Column(sa.Boolean, nullable=False, default=True)
            imap_user = sa.Column(sa.String(255), nullable=True)
            smtp_server = sa.Column(sa.String(255), nullable=True)
            smtp_port = sa.Column(sa.Integer, nullable=True, default=465)
            smtp_ssl = sa.Column(sa.Boolean, nullable=False, default=True)
            smtp_user = sa.Column(sa.String(255), nullable=True)
            created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
            updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP"))

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("  ✓ Tabla user_email_configs creada o verificada correctamente.")
    except Exception as e:
        print(f"  ⚠ Error al crear tablas de base de datos: {e}")

def run_npm_install():
    print("\n📦 Instalando dependencias del frontend (npm install)...")
    try:
        res = subprocess.run(["npm", "install"], cwd=BASE_DIR, check=False)
        if res.returncode == 0:
            print("  ✓ Dependencias instaladas correctamente.")
        else:
            print("  ⚠ Advertencia: Algunas dependencias no se pudieron instalar.")
    except Exception as e:
        print(f"  ⚠ No se pudo ejecutar npm install: {e}")

def run_build():
    print("\n🛠️ Ejecutando build del frontend (npm run build)...")
    try:
        res = subprocess.run(["npm", "run", "build"], cwd=BASE_DIR, check=False)
        if res.returncode == 0:
            print("  ✓ Build del frontend completado exitosamente.")
        else:
            print("  ⚠ Advertencia: Ocurrió un detalle en el build del frontend.")
    except Exception as e:
        print(f"  ⚠ No se pudo ejecutar npm run build: {e}")

def restart_local_servers():
    print("\n🔄 Reiniciando servicios locales...")
    try:
        subprocess.run(["pkill", "-f", "run_api.py"], check=False)
        print("  ✓ Reiniciada señal del servidor Backend API.")
    except Exception as e:
        print(f"  ⚠ Nota sobre proceso backend: {e}")

def install():
    print("🚀 Instalando Extensión KogniMail...")
    print(f"  BASE_DIR detectado: {BASE_DIR}")
    print(f"  EXT_DIR: {EXT_DIR}")

    # 1. Copy frontend components
    os.makedirs(COMPONENTS_DIR, exist_ok=True)
    for fname, dst in FRONTEND_FILES:
        src = os.path.join(EXT_DIR, "frontend", fname)
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            print(f"  ✓ Copiado component frontend: {fname}")

    # 2. Copy email page route
    os.makedirs(EMAIL_ROUTE_DIR, exist_ok=True)
    page_src = os.path.join(EXT_DIR, "frontend", "page.tsx")
    if os.path.exists(page_src):
        shutil.copyfile(page_src, EMAIL_ROUTE_FILE)
        print("  ✓ Ruta de Next.js /email creada.")

    # 3. Copy backend files
    backend_dst = os.path.join(BASE_DIR, "api", "email_management")
    if os.path.exists(backend_dst):
        shutil.rmtree(backend_dst)
    shutil.copytree(os.path.join(EXT_DIR, "backend"), backend_dst)
    print("  ✓ Código de backend copiado a api/email_management/")

    # 4. Inject router to api/main.py
    if os.path.exists(API_MAIN_TARGET):
        if not os.path.exists(API_MAIN_BACKUP):
            shutil.copyfile(API_MAIN_TARGET, API_MAIN_BACKUP)
            print("  ✓ Copia de seguridad creada para api/main.py.")

        with open(API_MAIN_TARGET, "r", encoding="utf-8") as f:
            content = f.read()

        if ROUTER_INCLUDE_LINE not in content:
            modified = content
            lines = modified.splitlines(keepends=True)
            
            # Step A: Insert import line
            inserted_import = False
            for i, line in enumerate(lines):
                if line.startswith("from api.galleries import router as galleries_router"):
                    lines.insert(i + 1, IMPORT_LINE + "\n")
                    inserted_import = True
                    break
            
            if not inserted_import:
                # Fallback: add at the top before FastAPI startup
                for i, line in enumerate(lines):
                    if "app = FastAPI" in line:
                        lines.insert(i, IMPORT_LINE + "\n")
                        break
            
            # Step B: Insert app.include_router call
            inserted_router = False
            for i, line in enumerate(lines):
                if 'app.include_router(galleries_router, prefix="/api/galleries", tags=["galleries"])' in line:
                    lines.insert(i + 1, f"app.include_router(email_extension_router)\n")
                    inserted_router = True
                    break
            
            if not inserted_router:
                # Fallback
                for i, line in enumerate(lines):
                    if "app.include_router" in line:
                        lines.insert(i + 1, f"app.include_router(email_extension_router)\n")
                        break

            modified = "".join(lines)
            with open(API_MAIN_TARGET, "w", encoding="utf-8") as f:
                f.write(modified)
            print("  ✓ Router backend registrado con éxito en api/main.py.")
        else:
            print("  ✓ Router backend ya registrado en api/main.py.")

    # 5. Inject sidebar link to src/components/Sidebar.tsx
    if os.path.exists(SIDEBAR_TARGET):
        if not os.path.exists(SIDEBAR_BACKUP):
            shutil.copyfile(SIDEBAR_TARGET, SIDEBAR_BACKUP)
            print("  ✓ Copia de seguridad creada para src/components/Sidebar.tsx.")

        with open(SIDEBAR_TARGET, "r", encoding="utf-8") as f:
            content = f.read()

        if 'href="/email"' not in content:
            # Add Mail to lucide-react import
            if "Mail" not in content:
                content = content.replace("Plus, MessageSquare", "Plus, MessageSquare, Mail")
                print("  ✓ Ícono Mail importado en Sidebar.tsx.")

            workspace_link_p1 = '            <Link href="/workspaces" passHref onClick={onLinkClick} title="Workspaces">'
            workspace_link_p2 = '<Link href="/workspaces" passHref onClick={onLinkClick} title="Workspaces" className="w-full block">'
            
            matched_link = None
            if workspace_link_p1 in content:
                matched_link = workspace_link_p1
            elif workspace_link_p2 in content:
                matched_link = workspace_link_p2

            if matched_link:
                indent = "            " if matched_link == workspace_link_p1 else ""
                email_button = indent + '<Link href="/email" passHref onClick={onLinkClick} title="Correo"' + (' className="w-full block">' if "className" in matched_link else '>') + '\n' + \
                               indent + '  <Button\n' + \
                               indent + '    variant={pathname?.startsWith(\'/email\') ? \'secondary\' : \'ghost\'}\n' + \
                               indent + '    className={cn(\n' + \
                               indent + '      "w-full transition-all duration-300 hover:bg-primary/10 hover:text-primary rounded-xl group",\n' + \
                               indent + '      isCollapsed ? "justify-center h-9 w-9 p-0" : "justify-start h-9 px-2",\n' + \
                               indent + '      pathname?.startsWith(\'/email\') && "bg-primary/10 text-primary border border-primary/20"\n' + \
                               indent + '    )}\n' + \
                               indent + '  >\n' + \
                               indent + '    <Mail className={cn("h-4 w-4 transition-transform group-hover:scale-110", showToolText && "mr-2")} />\n' + \
                               indent + '    {showToolText && <span className="text-sm font-medium">Correo</span>}\n' + \
                               indent + '  </Button>\n' + \
                               indent + '</Link>\n\n'
                
                content = content.replace(matched_link, f"{email_button}{matched_link}", 1)
                with open(SIDEBAR_TARGET, "w", encoding="utf-8") as f:
                    f.write(content)
                print("  ✓ Enlace de Correo inyectado en Sidebar.tsx.")
            else:
                print("  ⚠ No se encontró el marcador de Workspaces en Sidebar.tsx para inyectar el botón.")
        else:
            print("  ✓ Botón de Correo ya inyectado en Sidebar.tsx.")

    # 5b. Inject settings tab to src/app/(dashboard)/settings/page.tsx
    if os.path.exists(SETTINGS_TARGET):
        if not os.path.exists(SETTINGS_BACKUP):
            shutil.copyfile(SETTINGS_TARGET, SETTINGS_BACKUP)
            print("  ✓ Copia de seguridad creada para settings/page.tsx.")

        with open(SETTINGS_TARGET, "r", encoding="utf-8") as f:
            content = f.read()

        if 'value="email"' not in content:
            # 1. Add import
            if "EmailSettingsModal" not in content:
                import_marker = "import { useAuth } from '@/contexts/AuthContext';"
                if import_marker in content:
                    content = content.replace(import_marker, f"{import_marker}\nimport {{ EmailSettingsModal }} from '@/components/EmailSettingsModal';", 1)
                else:
                    content = "import { EmailSettingsModal } from '@/components/EmailSettingsModal';\n" + content
                print("  ✓ EmailSettingsModal importado en settings/page.tsx.")

            # 2. Add state
            state_marker = "const [activeTab, setActiveTab] = useState('personal-data');"
            if state_marker in content:
                content = content.replace(state_marker, f"{state_marker}\n  const [isEmailSettingsOpen, setIsEmailSettingsOpen] = useState(false);", 1)
                print("  ✓ Estado de configuración de email añadido en settings/page.tsx.")

            # 3. Add TabsTrigger
            trigger_marker = '<TabsTrigger value="sync">Sincronización</TabsTrigger>'
            if trigger_marker in content:
                content = content.replace(trigger_marker, f"{trigger_marker}\n          <TabsTrigger value=\"email\">Correo Electrónico</TabsTrigger>", 1)
                print("  ✓ Trigger de pestaña de correo añadido en settings/page.tsx.")

            # 4. Add TabsContent and Modal
            content_marker = "</TabsContent>\n      </Tabs>\n    </div>"
            if content_marker in content:
                email_tab_content = """        </TabsContent>
        <TabsContent value="email">
          <Card>
            <CardHeader>
              <CardTitle>Credenciales de Correo Electrónico</CardTitle>
              <CardDescription>
                Configura tus credenciales SMTP/IMAP o vincula tu cuenta de Google de forma segura para usar KogniMail.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                KogniMail te permite recibir y enviar correos directamente desde KognitoAI. 
                Los correos también se indexan localmente en tu cerebro para mejorar el contexto de K Kai.
              </p>
              <Button onClick={() => setIsEmailSettingsOpen(true)} className="rounded-full bg-primary hover:bg-primary/95 text-white">
                Configurar Credenciales de Correo
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      <EmailSettingsModal isOpen={isEmailSettingsOpen} onClose={() => setIsEmailSettingsOpen(false)} />
    </div>"""
                parts = content.rsplit(content_marker, 1)
                if len(parts) == 2:
                    content = parts[0] + email_tab_content + parts[1]
                    print("  ✓ Contenido de pestaña de correo añadido en settings/page.tsx.")

            with open(SETTINGS_TARGET, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print("  ✓ Pestaña de correo ya inyectada en settings/page.tsx.")

    # 6. Database migrations
    asyncio.run(create_database_tables())

    # 7. Rebuild & Restart
    run_npm_install()
    run_build()
    restart_local_servers()
    print("\n🎉 ¡Extensión KogniMail instalada con éxito!")

def uninstall():
    print("🔄 Desinstalando Extensión KogniMail y restaurando sistema base...")

    # 1. Restore Backend main.py
    if os.path.exists(API_MAIN_BACKUP):
        shutil.copyfile(API_MAIN_BACKUP, API_MAIN_TARGET)
        os.remove(API_MAIN_BACKUP)
        print("  ✓ Backend api/main.py restaurado desde copia de seguridad.")
    elif os.path.exists(API_MAIN_TARGET):
        with open(API_MAIN_TARGET, "r", encoding="utf-8") as f:
            content = f.read()
        if "email_extension_router" in content:
            lines = content.splitlines(keepends=True)
            lines = [l for l in lines if "email_extension_router" not in l]
            with open(API_MAIN_TARGET, "w", encoding="utf-8") as f:
                f.write("".join(lines))
            print("  ✓ Router backend eliminado de api/main.py.")

    # 2. Restore Sidebar.tsx
    if os.path.exists(SIDEBAR_BACKUP):
        shutil.copyfile(SIDEBAR_BACKUP, SIDEBAR_TARGET)
        os.remove(SIDEBAR_BACKUP)
        print("  ✓ Componente Sidebar.tsx restaurado desde copia de seguridad.")
    elif os.path.exists(SIDEBAR_TARGET):
        with open(SIDEBAR_TARGET, "r", encoding="utf-8") as f:
            content = f.read()
        if 'href="/email"' in content:
            print("  ⚠ No se pudo desinstalar el botón de Sidebar.tsx automáticamente. Por favor revísalo.")

    # 2b. Restore settings/page.tsx
    if os.path.exists(SETTINGS_BACKUP):
        shutil.copyfile(SETTINGS_BACKUP, SETTINGS_TARGET)
        os.remove(SETTINGS_BACKUP)
        print("  ✓ Configuración de settings/page.tsx restaurada desde copia de seguridad.")

    # 3. Clean copied files
    backend_dst = os.path.join(BASE_DIR, "api", "email_management")
    if os.path.exists(backend_dst):
        shutil.rmtree(backend_dst)
        print("  ✓ Carpeta backend api/email_management/ eliminada.")

    if os.path.exists(EMAIL_ROUTE_DIR):
        shutil.rmtree(EMAIL_ROUTE_DIR)
        print("  ✓ Ruta frontend /email eliminada.")

    for fname, dst in FRONTEND_FILES:
        if os.path.exists(dst):
            os.remove(dst)
            print(f"  ✓ Componente frontend {fname} eliminado.")

    # 4. Rebuild & Restart
    run_build()
    restart_local_servers()
    print("\n🎉 Extensión KogniMail desinstalada y sistema base restaurado.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        uninstall()
    else:
        install()
