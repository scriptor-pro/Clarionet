#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(grep -E '^APP_VERSION' "$ROOT_DIR/radiocity.py" | head -n1 | cut -d '"' -f2)
VERSION=${VERSION:-0.0.0}

VENV_DIR="$ROOT_DIR/.venv-macos"
DIST_DIR="$ROOT_DIR/dist"
APP_NAME="Clarionet"
ICON_PNG="$ROOT_DIR/assets/icons/clarionet_icon_512x512.png"
ICON_ICNS="$ROOT_DIR/assets/icons/clarionet.icns"

mkdir -p "$DIST_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

pip install --upgrade pip >/dev/null
if [[ -f "$ROOT_DIR/requirements.txt" ]]; then
  pip install -r "$ROOT_DIR/requirements.txt" pyinstaller >/dev/null
else
  pip install pyinstaller >/dev/null
fi

if [[ ! -f "$ICON_ICNS" ]] && [[ -f "$ICON_PNG" ]]; then
  if command -v iconutil >/dev/null 2>&1 && command -v sips >/dev/null 2>&1; then
    TMP_DIR="$(mktemp -d)"
    ICONSET_DIR="$TMP_DIR/icon.iconset"
    mkdir -p "$ICONSET_DIR"

    sips -z 16 16 "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
    sips -z 32 32 "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
    sips -z 32 32 "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
    sips -z 64 64 "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
    sips -z 128 128 "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
    sips -z 256 256 "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
    sips -z 256 256 "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
    sips -z 512 512 "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
    sips -z 512 512 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
    sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null

    iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"
    rm -rf "$TMP_DIR"
  fi
fi

ICON_ARGS=()
if [[ -f "$ICON_ICNS" ]]; then
  ICON_ARGS=(--icon "$ICON_ICNS")
fi

"$VENV_DIR/bin/pyinstaller" \
  --noconfirm \
  --name "$APP_NAME" \
  --windowed \
  --osx-bundle-identifier "com.clarionet.app" \
  --add-data "$ROOT_DIR/assets:assets" \
  "${ICON_ARGS[@]}" \
  "$ROOT_DIR/radiocity.py"

echo "Built $APP_NAME.app in $DIST_DIR"
