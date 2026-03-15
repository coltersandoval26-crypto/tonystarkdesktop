#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[bootstrap] initializing Stark workspace at: ${ROOT_DIR}"

mkdir -p "${ROOT_DIR}/runtime/logs"
mkdir -p "${ROOT_DIR}/runtime/cache"

cp --update=none "${ROOT_DIR}/desktop/layout/monitors.json" "${ROOT_DIR}/runtime/monitors.active.json"
cp --update=none "${ROOT_DIR}/desktop/layout/widgets.json" "${ROOT_DIR}/runtime/widgets.active.json"

cat <<'STATUS'
[bootstrap] done.
- active monitor profile: runtime/monitors.active.json
- active widget profile:  runtime/widgets.active.json
- runtime logs dir:       runtime/logs
STATUS
