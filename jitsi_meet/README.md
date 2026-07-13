# Jitsi Meet Extension for KognitoAI

Extensión para KognitoAI que agrega un módulo independiente de videoconferencia mediante Jitsi Meet, accesible desde la ruta `/meet` del dashboard.

## Características

- Crear salas de Jitsi Meet asociadas a álbumes de KognitoAI.
- Generar enlaces públicos a salas (`https://meet.jit.si/<room_name>`).
- Opcionalmente proteger salas con contraseña.
- Listar, abrir, copiar enlace y eliminar salas desde la interfaz.
- Página independiente en el dashboard sin depender de la sección de Galerías.

## Estructura

```
extensions/jitsi_meet/
├── README.md
├── install.py
├── install.sh
├── backend/
│   ├── __init__.py
│   ├── router.py
│   ├── models.py
│   └── schemas.py
└── frontend/
    └── JitsiMeetPanel.tsx
```

## Instalación

Desde el directorio de la extensión:

```bash
python install.py
```

El instalador:
- Detecta la instalación base de KognitoAI.
- Crea la tabla `jitsi_rooms` en la base de datos.
- Crea la página independiente `src/app/(dashboard)/meet/page.tsx`.
- Registra el router backend en `api/main.py`.
- Compila el frontend y reinicia los servidores locales.

## Desinstalación

```bash
python install.py --uninstall
```

Restaura backups y elimina las modificaciones realizadas.

## Endpoints (Backend)

- `POST /api/meet/rooms`
- `GET /api/meet/rooms`
- `GET /api/meet/rooms/{room_id}`
- `DELETE /api/meet/rooms/{room_id}`

## Uso

Después de instalar, abre la sección **Meet** en KognitoAI (`/meet`). Usa el panel para crear salas y administrarlas.

## Notas

- Esta extensión asume que el servidor base de Jitsi Meet es `meet.jit.si`. Si usas un servidor propio, actualiza la URL base en el componente frontend.
- Las salas se asocian a un `album_id` existente. Asegúrate de usar un UUID válido.
