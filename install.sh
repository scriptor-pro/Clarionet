#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON_SOURCE="${SCRIPT_DIR}/assets/radiocity.svg"
DESKTOP_SOURCE="${SCRIPT_DIR}/radiocity.desktop"

XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
ICON_TARGET_DIR="${XDG_DATA_HOME}/icons/hicolor/scalable/apps"
DESKTOP_TARGET_DIR="${XDG_DATA_HOME}/applications"
DESKTOP_TARGET="${DESKTOP_TARGET_DIR}/radiocity.desktop"

mkdir -p "${ICON_TARGET_DIR}" "${DESKTOP_TARGET_DIR}"
cp "${ICON_SOURCE}" "${ICON_TARGET_DIR}/radiocity.svg"

sed \
  -e "s|^TryExec=.*|TryExec=${SCRIPT_DIR}/radiocity|" \
  -e "s|^Exec=.*|Exec=${SCRIPT_DIR}/radiocity|" \
  "${DESKTOP_SOURCE}" > "${DESKTOP_TARGET}"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DESKTOP_TARGET_DIR}"
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  if [ -f "${XDG_DATA_HOME}/icons/hicolor/index.theme" ]; then
    gtk-update-icon-cache "${XDG_DATA_HOME}/icons/hicolor"
  fi
fi
