pkgname=clarionet
pkgver=87.5.026
pkgrel=1
pkgdesc="Minimalist autoradio-style internet radio player"
arch=("x86_64")
url=""
license=("MIT")
depends=("python" "gtk3" "python-gobject" "mpv")

package() {
  install -Dm755 /dev/stdin "${pkgdir}/usr/bin/clarionet" <<'EOF'
#!/usr/bin/env bash
exec /usr/bin/python3 /usr/share/clarionet/clarionet.py "$@"
EOF

  install -Dm644 "${srcdir}/clarionet.py" "${pkgdir}/usr/share/clarionet/clarionet.py"
  install -Dm644 "${srcdir}/clarionet.desktop" "${pkgdir}/usr/share/applications/clarionet.desktop"
  install -Dm644 "${srcdir}/assets/clarionet.svg" "${pkgdir}/usr/share/icons/hicolor/scalable/apps/clarionet.svg"
  cp -r "${srcdir}/assets" "${pkgdir}/usr/share/clarionet/"
  install -Dm644 "${srcdir}/README.md" "${pkgdir}/usr/share/doc/clarionet/README.md"
  install -Dm644 "${srcdir}/LICENSE" "${pkgdir}/usr/share/licenses/clarionet/LICENSE"
}
