#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON_SOURCE="${SCRIPT_DIR}/assets/clarionet.svg"
ICON_PNG_DIR="${SCRIPT_DIR}/assets/icons"
DESKTOP_SOURCE="${SCRIPT_DIR}/clarionet.desktop"

XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
ICON_TARGET_DIR="${XDG_DATA_HOME}/icons/hicolor/scalable/apps"
DESKTOP_TARGET_DIR="${XDG_DATA_HOME}/applications"
DESKTOP_TARGET="${DESKTOP_TARGET_DIR}/clarionet.desktop"

mkdir -p "${ICON_TARGET_DIR}" "${DESKTOP_TARGET_DIR}"
rm -f "${DESKTOP_TARGET_DIR}/radiocity.desktop"
rm -f "${ICON_TARGET_DIR}/radiocity.svg"

cp "${ICON_SOURCE}" "${ICON_TARGET_DIR}/clarionet.svg"

for size in 16 24 32 48 64 96 128 256 512; do
  src="${ICON_PNG_DIR}/clarionet_icon_${size}x${size}.png"
  if [ -f "${src}" ]; then
    target_dir="${XDG_DATA_HOME}/icons/hicolor/${size}x${size}/apps"
    mkdir -p "${target_dir}"
    rm -f "${target_dir}/radiocity.png"
    cp "${src}" "${target_dir}/clarionet.png"
  fi
done

ICON_INSTALLED_PATH="${XDG_DATA_HOME}/icons/hicolor/256x256/apps/clarionet.png"

sed \
  -e "s|^TryExec=.*|TryExec=${SCRIPT_DIR}/clarionet|" \
  -e "s|^Exec=.*|Exec=${SCRIPT_DIR}/clarionet|" \
  -e "s|^Icon=.*|Icon=${ICON_INSTALLED_PATH}|" \
  -e "s|^StartupWMClass=.*|StartupWMClass=clarionet|" \
  "${DESKTOP_SOURCE}" > "${DESKTOP_TARGET}"

if ! grep -q '^StartupWMClass=' "${DESKTOP_TARGET}"; then
  echo 'StartupWMClass=clarionet' >> "${DESKTOP_TARGET}"
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DESKTOP_TARGET_DIR}"
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  if [ ! -f "${XDG_DATA_HOME}/icons/hicolor/index.theme" ]; then
    cat > "${XDG_DATA_HOME}/icons/hicolor/index.theme" <<'EOF'
[Icon Theme]
Name=Hicolor
Comment=Fallback theme
Directories=16x16/apps,24x24/apps,32x32/apps,48x48/apps,64x64/apps,96x96/apps,128x128/apps,256x256/apps,512x512/apps,scalable/apps

[16x16/apps]
Size=16
Context=Applications
Type=Threshold

[24x24/apps]
Size=24
Context=Applications
Type=Threshold

[32x32/apps]
Size=32
Context=Applications
Type=Threshold

[48x48/apps]
Size=48
Context=Applications
Type=Threshold

[64x64/apps]
Size=64
Context=Applications
Type=Threshold

[96x96/apps]
Size=96
Context=Applications
Type=Threshold

[128x128/apps]
Size=128
Context=Applications
Type=Threshold

[256x256/apps]
Size=256
Context=Applications
Type=Threshold

[512x512/apps]
Size=512
Context=Applications
Type=Threshold

[scalable/apps]
Size=128
Context=Applications
Type=Scalable
MinSize=8
MaxSize=512
EOF
  fi
  gtk-update-icon-cache "${XDG_DATA_HOME}/icons/hicolor"
  for size in 16 24 32 48 64 96 128 256 512; do
    cache_dir="${XDG_DATA_HOME}/icons/hicolor/${size}x${size}"
    if [ -d "${cache_dir}" ]; then
      gtk-update-icon-cache "${cache_dir}"
    fi
  done
fi
