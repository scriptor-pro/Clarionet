#!/usr/bin/env bash
set -euo pipefail

NAME="clarionet"
VERSION="87.5.025"
DESC="Minimalist autoradio-style internet radio player"
LICENSE="MIT"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_ROOT="${ROOT_DIR}/dist/packages/linux"

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
)

FILE_ARGS=(
  "${ROOT_DIR}/clarionet=/usr/bin/clarionet"
  "${ROOT_DIR}/clarionet.desktop=/usr/share/applications/clarionet.desktop"
  "${ROOT_DIR}/clarionet.py=/usr/share/clarionet/clarionet.py"
  "${ROOT_DIR}/assets/clarionet.svg=/usr/share/icons/hicolor/scalable/apps/clarionet.svg"
  "${ROOT_DIR}/README.md=/usr/share/doc/clarionet/README.md"
  "${ROOT_DIR}/LICENSE=/usr/share/licenses/clarionet/LICENSE"
)

ICON_FILES=()
for size in 16 24 32 48 64 96 128 256 512; do
  path="${ROOT_DIR}/assets/icons/clarionet_icon_${size}x${size}.png"
  if [ -f "${path}" ]; then
    ICON_FILES+=("${path}=${ICON_DIR}/${size}x${size}/apps/clarionet.png")
  fi
done

build() {
  local target="$1"
  shift
  local depends=()
  local output_dir="${OUTPUT_ROOT}/${target}"
  mkdir -p "${output_dir}"
  case "${target}" in
    deb)
      depends+=(
        --depends "python3"
        --depends "python3-gi"
        --depends "gir1.2-gtk-3.0"
        --depends "libgtk-3-0"
        --depends "mpv"
      )
      ;;
    rpm)
      depends+=(
        --depends "python3"
        --depends "python3-gobject"
        --depends "gtk3"
        --depends "mpv"
      )
      ;;
    pacman)
      depends+=(
        --depends "python"
        --depends "python-gobject"
        --depends "gtk3"
        --depends "mpv"
      )
      ;;
  esac
  fpm -t "${target}" --package "${output_dir}" "${COMMON_ARGS[@]}" "${depends[@]}" "${ICON_FILES[@]}" "${FILE_ARGS[@]}"
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
