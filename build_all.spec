# build_all.spec — spec PyInstaller onefile (tout embarque dans un seul exe)
# Produit : dist/StuGoCO2_Explorer.exe + dist/Admin_Logs.exe

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
import os

# ── PyQt6 : uniquement les DLLs + plugins indispensables ──────────────────────
bins_qt  = collect_dynamic_libs('PyQt6')
datas_qt = collect_data_files('PyQt6', includes=[
    'Qt6/plugins/platforms/*',
    'Qt6/plugins/styles/*',
    'Qt6/plugins/imageformats/*',
    'Qt6/plugins/iconengines/*',
    'Qt6/plugins/printsupport/*',
])

# ── matplotlib : donnees de configuration (fonts, backends) ───────────────────
datas_mpl = collect_data_files('matplotlib')

# ── Assets locaux : images de fond + GIF spinner du splash screen ─────────────
datas_assets = [('assets', 'assets')]

# ── pandas : uniquement les extensions internes utilisees ─────────────────────
# (pas collect_submodules qui tire 2000+ modules de test)
hidden_pandas = [
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.timestamps',
    'pandas._libs.tslibs.offsets',
    'pandas._libs.tslibs.period',
    'pandas._libs.tslibs.parsing',
    'pandas._libs.tslibs.dtypes',
    'pandas._libs.tslibs.vectorized',
    'pandas._libs.tslibs.conversion',
    'pandas._libs.tslibs.strptime',
    'pandas._libs.tslibs.timezones',
    'pandas._libs.tslibs.fields',
    'pandas._libs.tslibs.ccalendar',
    'pandas._libs.lib',
    'pandas._libs.ops',
    'pandas._libs.ops_dispatch',
    'pandas._libs.missing',
    'pandas._libs.hashtable',
    'pandas._libs.index',
    'pandas._libs.indexing',
    'pandas._libs.internals',
    'pandas._libs.interval',
    'pandas._libs.join',
    'pandas._libs.reshape',
    'pandas._libs.sparse',
    'pandas._libs.writers',
    'pandas._libs.window.aggregations',
    'pandas._libs.window.indexers',
    'pandas._libs.arrays',
    'pandas._libs.json',
    'pandas.core.arrays.datetimes',
    'pandas.core.arrays.timedeltas',
    'pandas.core.arrays.period',
    'pandas.io.formats.style',
    'pandas.io.excel._openpyxl',
    'pandas.io.excel._base',
]

block_cipher = None

# ── Imports caches communs aux deux executables ────────────────────────────────
QT_HIDDEN = [
    'PyQt6.sip',
    'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
    'PyQt6.QtPrintSupport', 'PyQt6.QtOpenGL', 'PyQt6.QtOpenGLWidgets',
    'PyQt6.QtSvg', 'PyQt6.QtSvgWidgets',
]

# ───────────────────────────────────────────────────────────────────────────────
# ANALYSE main.py
# ───────────────────────────────────────────────────────────────────────────────
a_main = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=bins_qt,
    datas=datas_qt + datas_mpl + datas_assets,
    hiddenimports=QT_HIDDEN + hidden_pandas + [
        # matplotlib backend Qt
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_qt',
        'matplotlib.backends.qt_compat',
        # librairies de donnees
        'openpyxl',
        'openpyxl.cell._writer',
        'openpyxl.styles.stylesheet',
        'openpyxl.drawing.spreadsheet_drawing',
        'squarify',
        # couche shared
        'shared.constants',
        'shared.scaling',
        'shared.paths',
        'shared.color_utils',
        'shared.logging.action_logger',
        'shared.logging.file_logger',
        # couche app
        'app.bootstrap',
        'app.commands.base_command',
        'app.commands.apply_filter_command',
        'app.commands.load_files_command',
        'app.events.event_bus',
        'app.events.app_events',
        'app.services.data_service',
        'app.services.chart_service',
        'app.services.export_service',
        # couche domain
        'domain.value_objects.chart_config',
        'domain.value_objects.color_value',
        'domain.repositories.i_session_repo',
        # couche infrastructure
        'infrastructure.extractors.excel_extractor',
        'infrastructure.extractors.csv_extractor',
        'infrastructure.extractors.extractor_factory',
        'infrastructure.models.pandas_model',
        'infrastructure.persistence.session_repository',
        'infrastructure.persistence.preferences_repository',
        'infrastructure.persistence._compat_session_manager',
        'infrastructure.persistence.session_manager_compat',
        # presentation
        'presentation.main_window',
        'presentation.splash_screen',
        'presentation.mediator.ui_mediator',
        'presentation.pages.base_page',
        'presentation.pages.home.home_page',
        'presentation.pages.import_.import_page',
        'presentation.pages.table.table_page',
        'presentation.pages.chart.chart_page',
        'presentation.pages.comparison.comparison_page',
        'presentation.pages.settings.settings_page',
        'presentation.pages.help.help_page',
        'presentation.sidebar.nav_sidebar',
        'presentation.sidebar.filter_sidebar',
        'presentation.sidebar.log_panel',
        'presentation.state.app_state',
        'presentation.state.states',
        'presentation.theme.stylesheet_builder',
        'presentation.theme.theme_manager',
        'presentation.theme.preset_completer',
        'presentation.widgets.primitives',
        'presentation.widgets.chart_controls',
        'presentation.widgets.factory.widget_factory',
        # rendering
        'rendering.factory',
        'rendering.strategies.renderer_2d',
        'rendering.strategies.renderer_3d',
        'rendering.strategies.special_renderer',
        'rendering.axes.axes_2d',
        'rendering.axes.axes_3d',
        'rendering.geometry.cube_3d',
        'rendering.geometry.pie_3d',
        'rendering.interfaces.i_chart_renderer',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'tkinter', '_tkinter',
        'PyQt5', 'PySide2', 'PySide6',
        'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtQuick3D',
        'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtBluetooth', 'PyQt6.QtNfc', 'PyQt6.QtPositioning',
        'PyQt6.QtRemoteObjects', 'PyQt6.QtSensors', 'PyQt6.QtSerialPort',
        'PyQt6.QtSpatialAudio', 'PyQt6.QtSql', 'PyQt6.QtTextToSpeech',
        'PyQt6.QtVirtualKeyboard', 'PyQt6.QtWebChannel', 'PyQt6.QtWebSockets',
        'test', '_pytest', 'pytest',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz_main = PYZ(a_main.pure, a_main.zipped_data, cipher=block_cipher)

exe_main = EXE(
    pyz_main, a_main.scripts,
    [],
    name='StuGoCO2_Explorer',
    debug=False, strip=False, upx=True, console=False,
    icon='assets/logo.ico',
)

# ───────────────────────────────────────────────────────────────────────────────
# ANALYSE admin.py
# ───────────────────────────────────────────────────────────────────────────────
a_admin = Analysis(
    ['admin.py'],
    pathex=['.'],
    binaries=bins_qt,
    datas=datas_qt,
    hiddenimports=QT_HIDDEN,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'tkinter', '_tkinter',
        'PyQt5', 'PySide2', 'PySide6',
        'matplotlib', 'pandas', 'numpy', 'scipy',
        'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtWebEngine',
        'test', '_pytest', 'pytest',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz_admin = PYZ(a_admin.pure, a_admin.zipped_data, cipher=block_cipher)

exe_admin = EXE(
    pyz_admin, a_admin.scripts,
    [],
    name='Admin_Logs',
    debug=False, strip=False, upx=True, console=False,
    icon='assets/logo.ico',
)

coll = COLLECT(
    exe_main,
    a_main.binaries, a_main.zipfiles, a_main.datas,
    exe_admin,
    a_admin.binaries, a_admin.zipfiles, a_admin.datas,
    strip=False, upx=True, upx_exclude=[],
    name='StuGoCO2',
)
