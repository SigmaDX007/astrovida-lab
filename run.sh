#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
MODE="${1:-}"
if [[ "$#" -gt 1 ]]; then echo 'Uso: bash run.sh [--check]' >&2; exit 2; fi
if [[ ! -x .venv/Scripts/python.exe && ! -x .venv/bin/python ]]; then
  python -m venv .venv
fi
if [[ -x .venv/Scripts/python.exe ]]; then PY=.venv/Scripts/python.exe; else PY=.venv/bin/python; fi
hash=$("$PY" -c 'from hashlib import sha256; from pathlib import Path; print(sha256(Path("requirements.txt").read_bytes()).hexdigest())')
marker=.venv/.astrovida-deps.sha256
if [[ ! -f "$marker" || "$(cat "$marker")" != "$hash" ]]; then
  "$PY" -m pip install --disable-pip-version-check -r requirements.txt
  printf '%s\n' "$hash" > "$marker"
fi
"$PY" -m compileall -q alienlab app.py
"$PY" -m unittest discover -s tests -v
if [[ "$MODE" == "--check" ]]; then echo 'AstroVida: testes offline OK'; exit 0; fi
exec "$PY" -m streamlit run app.py --server.address 127.0.0.1
