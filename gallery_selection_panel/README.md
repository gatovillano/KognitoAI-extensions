# Extensión KognitoAI: Panel de Selección & KogniPhotos UI

Esta extensión añade un flujo colaborativo de selección de imágenes y transforma la interfaz de galerías de KognitoAI en una experiencia moderna y fluida (**KogniPhotos UI**).

## 🚀 Características

1. **Panel de Selección Interactivo**:
   - Genera enlaces de compartición específicos para destinatarios/clientes.
   - Los destinatarios pueden ingresar su nombre, seleccionar sus imágenes preferidas y añadir comentarios opcionales por foto o generales.
2. **Visualización de Selecciones Recibidas**:
   - El creador del álbum puede revisar en su propia galería las selecciones y notas enviadas por cada destinatario.
3. **Rediseño Completo a KogniPhotos UI**:
   - Rejilla de fotos fluida, animaciones avanzadas, barra de acciones y diseño responsivo adaptado a tus álbumes ya existentes.

## 📦 Instalación Modular

Esta extensión es **100% modular**. Para instalarla en cualquier instalación base de KognitoAI, ejecuta:

```bash
python3 extensions/gallery_selection_panel/install.py
```

El script de instalación automatiza:
- Registro dinámico del router backend en `api/main.py`.
- Creación automatizada de tablas en la base de datos (`selection_share_links`, `selection_submissions`, `selection_items`).
- Inyección de la vista transformada y rutas de compartición públicas.
- Ejecución automatizada de `npm run build` y reinicio de servicios locales.

## 🔄 Desinstalación

Para revertir KognitoAI a su estado original sin alterar el sistema base:

```bash
python3 extensions/gallery_selection_panel/install.py --uninstall
```
