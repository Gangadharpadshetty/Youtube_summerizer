#!/usr/bin/env bash
# Usage: ./setup_venv.sh [project_dir] [venv_name] [--no-install]
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-.}"
VENV_NAME="${2:-.venv}"
NO_INSTALL=false
if [ "$3" = "--no-install" ]; then
  NO_INSTALL=true
fi

# Resolve project directory relative to script location
if [[ "$PROJECT_DIR" = /* ]]; then
  TARGET_DIR="$PROJECT_DIR"
else
  TARGET_DIR="$SCRIPT_DIR/$PROJECT_DIR"
fi

cd "$TARGET_DIR" || { echo "Project directory not found: $TARGET_DIR"; exit 1; }

VENV_PATH="$TARGET_DIR/$VENV_NAME"
if [ -d "$VENV_PATH" ]; then
  echo "Virtual environment '$VENV_NAME' already exists in $TARGET_DIR"
  echo "To activate: source $VENV_PATH/bin/activate"
  exit 0
fi

echo "Creating virtual environment '$VENV_NAME'..."
python3 -m venv "$VENV_PATH" || python -m venv "$VENV_PATH"

if [ ! -f "$VENV_PATH/bin/python" ]; then
  echo "Failed to create virtual environment. Ensure Python is installed and on PATH.";
  exit 1
fi

echo "Upgrading pip inside venv..."
"$VENV_PATH/bin/python" -m pip install --upgrade pip

if [ -f "$TARGET_DIR/requirements.txt" ] && [ "$NO_INSTALL" = false ]; then
  echo "Installing requirements from requirements.txt..."
  "$VENV_PATH/bin/python" -m pip install -r "$TARGET_DIR/requirements.txt"
fi

echo "Done. To activate the venv run:"
echo "  source $VENV_PATH/bin/activate"
