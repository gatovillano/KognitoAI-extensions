# 🧩 KognitoAI Extensions

Official extensions repository for **[KognitoAI](https://github.com/gatovillano/KognitoAI)**.

Extensions modularize specialized features, custom UI panels, and multi-agent skills without cluttering the core framework. Each extension is self-contained with an automated installer (`install.sh` / `install.py`).

---

## 📦 Available Extensions / Extensiones Disponibles

| Extension | Category | Description | Installation |
|---|---|---|---|
| 📸 **[gallery_selection_panel](./gallery_selection_panel)** | UI / Media | Google Photos-style gallery UI with collaborative photo selection | `cd extensions/gallery_selection_panel && ./install.sh` |
| 📧 **[email_management](./email_management)** | AI / Productivity | AI-powered email inbox management, smart drafting, and thread summarization | `cd extensions/email_management && ./install.sh` |
| 📹 **[jitsi_meet](./jitsi_meet)** | Integration | Video conferencing, meeting room management, and automated room link generation | `cd extensions/jitsi_meet && ./install.sh` |
| 🌐 **[fediverso](./fediverso)** | Social / AI | Mastodon & Fediverse client with AI composing, thread summarization, and account management | `cd extensions/fediverso && ./install.sh` |
| 📜 **[kai_ethno](./kai_ethno)** | Research / AI | Multi-agent suite for ethnographic research, discourse analysis, PII detection, and academic literature synthesis | `cd extensions/kai_ethno && ./install.sh` |

---

## 🚀 How to Install an Extension / Cómo Instalar una Extensión

### Method 1: Local Installation (Recommended)
Navigate to the extension directory in your KognitoAI workspace and run the installer:

```bash
cd extensions/<extension_name>
./install.sh
```

Alternatively, invoke `install.py` directly:

```bash
python3 extensions/<extension_name>/install.py
```

### Method 2: Remote One-Line Installer
Install directly from GitHub into your local KognitoAI instance:

```bash
curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/<extension_name>/install.sh | bash
```

---

## 📋 Requirements / Requisitos

- **KognitoAI** installation running locally or in `~/KognitoAI` / `kognito-ai/`.
- Python 3.10+ with active virtual environment (automatically detected by `install.py`).
- Active database connection (for extensions requiring SQLAlchemy/Neo4j migrations).

---

## 🛠️ Creating a New Extension / Crear una Nueva Extensión

Each extension repository folder should follow this structure:

```
extensions/your_extension_name/
├── README.md           # Extension documentation & user guide
├── install.sh          # Shell wrapper script
├── install.py          # Python installer & database migration runner
├── backend/            # FastAPI routes, schemas, models (if applicable)
├── frontend/           # Next.js/React components (if applicable)
└── skill/              # Agent skills, SKILL.md, and LangChain BaseTools (if applicable)
```
