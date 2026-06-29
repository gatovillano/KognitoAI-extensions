# Cambios - Gallery Selection Panel Extension

## [2025-06-29] Fix: Rutas de importación dinámicas en install.py

**Problema:**
El instalador (`install.py`) tenía hardcodeadas rutas relativas incorrectas para las importaciones del frontend. Cuando la extensión se instalaba fuera del directorio del core (ej. en `/home/gato/Proyectos/KognitoAI/extensions/gallery_selection_panel/` mientras el core está en `/home/gato/Proyectos/KognitoAI/kognito-ai/`), las importaciones fallaban con `Module not found` durante el build de producción.

**Causa:**
- `PAGE_TRANSFORMED_CONTENT` usaba `../../../../extensions/...` (4 niveles)
- `SHARE_ROUTE_CONTENT` usaba `../../../../../extensions/...` (5 niveles)
- La estructura real requiere 5 y 6 niveles respectivamente para llegar desde `kognito-ai/src/app/...` hasta `extensions/...`

**Solución:**
Se reemplazaron las rutas hardcodeadas por cálculo dinámico de rutas relativas usando `os.path.relpath()`:
- `KOGNIPHOTOS_IMPORT_PATH`: calcula la ruta desde `galleries/page.tsx` hasta `KogniPhotosGalleryView.tsx`
- `SELECTION_PUBLIC_IMPORT_PATH`: calcula la ruta desde `selection/[token]/page.tsx` hasta `SelectionPublicPage.tsx`

**Archivos modificados:**
- `install.py`: funciones de cálculo de rutas y generación de contenido de páginas

**Verificación:**
- Ruta galería: `../../../../../extensions/gallery_selection_panel/frontend/KogniPhotosGalleryView.tsx`
- Ruta selección: `../../../../../../extensions/gallery_selection_panel/frontend/SelectionPublicPage.tsx`
