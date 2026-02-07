# Clarionet packaging scripts

## macOS

Requirements:
- macOS with `python3`
- `pyinstaller`
- Apple tools: `iconutil`, `sips`

Build:
```bash
./scripts/build-macos-app.sh
```

Output:
- `dist/packages/macos/Clarionet.app`

## Windows (Inno Setup)

Requirements:
- Windows + Python 3
- PyInstaller
- Inno Setup (`iscc.exe` in PATH)

Build (PowerShell):
```powershell
./scripts/build-windows-installer.ps1
```

Output:
- `dist/packages/windows/clarionet-setup.exe`

## Notes
- Both scripts read version from `APP_VERSION` in `radiocity.py`.
- Icons:
  - macOS uses `assets/icons/clarionet_icon_512x512.png` to build `.icns`.
  - Windows uses `assets/icons/clarionet.ico`.
