# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['immobilien_preis_rechner_clean.py'],
    pathex=[],
    binaries=[],
    datas=[('Logo.png', '.'),  # Include Logo.png in the root of the dist folder
           ('icon.ico', '.')  # Include icon.ico in the root of the dist folder
	],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='immobilien_preis_rechner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
