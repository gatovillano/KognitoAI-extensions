# 🧩 KognitoAI Extensions

Official extensions repository for **[KognitoAI](https://github.com/gatovillano/KognitoAI)**.

Extensions modularize specialized features, custom UI panels, and multi-agent skills without cluttering the core framework. Each extension is self-contained with an automated installer (`install.sh` / `install.py`).

---

## 📦 Available Extensions / Extensiones Disponibles

| Extension | Category | Description | Local Install | One-Line Remote Install |
|---|---|---|---|---|
| 📸 **[gallery_selection_panel](./gallery_selection_panel)** | UI / Media | Google Photos-style gallery UI with collaborative photo selection | `cd extensions/gallery_selection_panel && ./install.sh` | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/gallery_selection_panel/install.sh \| bash` |
| 📧 **[email_management](./email_management)** | AI / Productivity | AI-powered email inbox management, smart drafting, and thread summarization | `cd extensions/email_management && ./install.sh` | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/email_management/install.sh \| bash` |
| 📹 **[jitsi_meet](./jitsi_meet)** | Integration | Video conferencing, meeting room management, and automated room link generation | `cd extensions/jitsi_meet && ./install.sh` | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/jitsi_meet/install.sh \| bash` |
| 🌐 **[fediverso](./fediverso)** | Social / AI | Mastodon & Fediverse client with AI composing, thread summarization, and account management | `cd extensions/fediverso && ./install.sh` | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/fediverso/install.sh \| bash` |
| 📜 **[kai_ethno](./kai_ethno)** | Research / AI | Multi-agent suite for ethnographic research, discourse analysis, PII detection, and academic literature synthesis | `cd extensions/kai_ethno && ./install.sh` | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/kai_ethno/install.sh \| bash` |

---

## 🚀 Direct Installation Commands / Comandos Directos de Instalación

Puedes instalar cualquier extensión ejecutando el comando correspondiente directamente en tu terminal:

### 📸 KogniPhotos (Gallery Selection Panel)
```bash
# Remoto (One-Line)
curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/gallery_selection_panel/install.sh | bash

# Local
cd extensions/gallery_selection_panel && ./install.sh
```

### 📧 Email Management
```bash
# Remoto (One-Line)
curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/email_management/install.sh | bash

# Local
cd extensions/email_management && ./install.sh
```

### 📹 Jitsi Meet
```bash
# Remoto (One-Line)
curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/jitsi_meet/install.sh | bash

# Local
cd extensions/jitsi_meet && ./install.sh
```

### 🌐 Fediverso (Mastodon Client)
```bash
# Remoto (One-Line)
curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/fediverso/install.sh | bash

# Local
cd extensions/fediverso && ./install.sh
```

### 📜 KAI Ethno (Ethnographic Research Suite)
```bash
# Remoto (One-Line)
curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/kai_ethno/install.sh | bash

# Local
cd extensions/kai_ethno && ./install.sh
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
