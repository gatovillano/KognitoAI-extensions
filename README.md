# KognitoAI Extensions

Official extensions repository for [KognitoAI](https://github.com/gatovillano/KognitoAI).

Each extension is a self-contained module with its own `install.sh` and `install.py` that integrates directly with an existing KognitoAI installation.

## Available Extensions

| Extension | Description | Install |
|---|---|---|
| [gallery_selection_panel](./gallery_selection_panel) | 📸 KogniPhotos — Google Photos-style gallery UI with collaborative selection | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/gallery_selection_panel/install.sh \| bash` |
| [email_management](./email_management) | 📧 Email Management — AI-powered email inbox, drafting and summarization | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/email_management/install.sh \| bash` |
| [jitsi_meet](./jitsi_meet) | 📹 Jitsi Meet — Integrated video conferencing and meeting room management | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/jitsi_meet/install.sh \| bash` |
| [fediverso](./fediverso) | 🌐 Fediverso — Mastodon client with AI assistant for composing and thread summarization | `curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/fediverso/install.sh \| bash` |

## How to Install an Extension

```bash
curl -sSL https://raw.githubusercontent.com/gatovillano/KognitoAI-extensions/main/<extension_name>/install.sh | bash
```

> Requires a running KognitoAI installation at `~/KognitoAI`.

## Requirements

- KognitoAI installed at `~/KognitoAI` (see [main repo](https://github.com/gatovillano/KognitoAI))
- Python virtual environment at `~/KognitoAI/venv_host`
