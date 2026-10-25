# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/Baudouin/Documents/Projets/radiocity/clarionet.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/Baudouin/Documents/Projets/radiocity/assets', 'assets')],
    hiddenimports=['cairo'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources', 'setuptools'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Clarionet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Clarionet',
)
