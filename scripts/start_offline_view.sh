#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8080}"

cd "${ROOT_DIR}"

echo "[offline-view] Starting local offline server..."
echo "[offline-view] Open: http://127.0.0.1:${PORT}"
echo "[offline-view] Full screen: F11 (Windows/Linux) or Ctrl+Cmd+F (macOS)"
echo "[offline-view] Press Ctrl+C to stop."

python3 -m http.server "${PORT}" --bind 127.0.0.1
