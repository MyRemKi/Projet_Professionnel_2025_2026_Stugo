# admin.spec — PyInstaller spec pour Admin Logs (admin.py)

from PyInstaller.utils.hooks import collect_all

datas_qt, bins_qt, hidden_qt = collect_all('PyQt6')

block_cipher = None

a = Analysis(
    ['admin.py'],
    pathex=['.'],
    binaries=bins_qt,
    datas=datas_qt,
    hiddenimports=hidden_qt + [
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PyQt5', 'PySide2', 'PySide6', 'matplotlib', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Admin_Logs',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
