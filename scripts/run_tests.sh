#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-.}"

if [[ "$PROJECT_DIR" = /* ]]; then
  TARGET_DIR="$PROJECT_DIR"
else
  TARGET_DIR="$SCRIPT_DIR/$PROJECT_DIR"
fi

VENV_PATH="$TARGET_DIR/.venv"
if [ ! -f "$VENV_PATH/bin/python" ]; then
  echo "Virtual environment not found at $VENV_PATH. Create it with scripts/setup_venv.sh"
  exit 1
fi

PY="$VENV_PATH/bin/python"
echo "Using Python: $PY"

echo "Ensuring pytest is installed in venv..."
"$PY" -m pip install --upgrade pip
"$PY" -m pip install pytest

echo "Running tests..."
"$PY" -m pytest -q tests
exit $?
