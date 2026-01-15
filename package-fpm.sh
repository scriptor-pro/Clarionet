#!/usr/bin/env bash
set -euo pipefail

NAME="clarionet"
VERSION="0.2.1"
DESC="Minimalist autoradio-style internet radio player"
LICENSE="MIT"

if ! command -v fpm >/dev/null 2>&1; then
  echo "fpm not found. Install with: sudo gem install --no-document fpm"
  exit 1
fi

ICON_DIR="/usr/share/icons/hicolor"

COMMON_ARGS=(
  -s dir
  -n "${NAME}"
  -v "${VERSION}"
  --description "${DESC}"
  --license "${LICENSE}"
  --depends "python"
  --depends "mpv"
  --depends "gtk3"
  --depends "python-gobject"
  --prefix /usr
  "clarionet=/usr/bin/clarionet"
  "clarionet.desktop=/usr/share/applications/clarionet.desktop"
  "radiocity.py=/usr/share/clarionet/clarionet.py"
  "assets/clarionet.svg=/usr/share/icons/hicolor/scalable/apps/clarionet.svg"
  "README.md=/usr/share/doc/clarionet/README.md"
  "LICENSE=/usr/share/licenses/clarionet/LICENSE"
)

ICON_FILES=()
for size in 16 24 32 48 64 96 128 256 512; do
  path="assets/icons/clarionet_icon_${size}x${size}.png"
  if [ -f "${path}" ]; then
    ICON_FILES+=("${path}=${ICON_DIR}/${size}x${size}/apps/clarionet.png")
  fi
done

build() {
  local target="$1"
  shift
  fpm -t "${target}" "${COMMON_ARGS[@]}" "${ICON_FILES[@]}"
}

case "${1:-}" in
  deb|rpm|pacman)
    build "$1"
    ;;
  all|"" )
    build deb
    build rpm
    build pacman
    ;;
  *)
    echo "Usage: $0 [deb|rpm|pacman|all]"
    exit 1
    ;;
esac
