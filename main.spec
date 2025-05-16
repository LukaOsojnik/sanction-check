# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('__init__.py', '.'), ('config.py', '.'), ('controllers', 'controllers'), 
    ('services', 'services'), ('models', 'models'), ('gui', 'gui'), 
    ('utils', 'utils'), ('repositories','repositories')],
    hiddenimports=['pandas', 'tkinter', 'tkinter.font', 'tkinter.messagebox', 'tkinter.ttk', 'tkinter.filedialog', 
    '__future__', 'numpy', 'pytz', 'dateutil', 'requests', 'rapidfuzz', 'reportlab', 
    'reportlab.pdfbase.ttfonts', 'reportlab.lib.pagesizes', 'reportlab.platypus'],
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
    name='main',
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
