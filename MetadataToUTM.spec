# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['MetadataToUTM.py'],
    pathex=['C:\\Users\\Cameron\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages'],
    binaries=[],
    datas=[],
    hiddenimports=['tablib[xlsx]', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MetadataToUTM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
