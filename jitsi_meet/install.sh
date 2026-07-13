#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "--uninstall" ]]; then
  python3 "$SCRIPT_DIR/install.py" --uninstall
else
  python3 "$SCRIPT_DIR/install.py"
fi
