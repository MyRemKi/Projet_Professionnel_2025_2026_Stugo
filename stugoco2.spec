# stugoco2.spec — PyInstaller spec pour StuGo CO2 Explorer (main.py)

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collecter tous les fichiers/plugins de PyQt6 et matplotlib
datas_qt,  bins_qt,  hidden_qt  = collect_all('PyQt6')
datas_mpl, bins_mpl, hidden_mpl = collect_all('matplotlib')

hidden_pandas = collect_submodules('pandas')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=bins_qt + bins_mpl,
    datas=datas_qt + datas_mpl,
    hiddenimports=(
        hidden_qt + hidden_mpl + hidden_pandas + [
            'openpyxl',
            'openpyxl.cell._writer',
            'squarify',
            'pkg_resources.py2_warn',
            'shared.constants',
            'shared.scaling',
            'shared.color_utils',
            'shared.logging.action_logger',
            'shared.logging.file_logger',
            'app.bootstrap',
            'app.commands.base_command',
            'app.commands.apply_filter_command',
            'app.commands.load_files_command',
            'app.events.event_bus',
            'app.events.app_events',
            'app.services.data_service',
            'app.services.chart_service',
            'app.services.export_service',
            'domain.value_objects.chart_config',
            'domain.value_objects.color_value',
            'domain.repositories.i_session_repo',
            'infrastructure.extractors.excel_extractor',
            'infrastructure.extractors.extractor_factory',
            'infrastructure.models.pandas_model',
            'infrastructure.persistence.session_repository',
            'infrastructure.persistence.preferences_repository',
            'infrastructure.persistence._compat_session_manager',
            'infrastructure.persistence.session_manager_compat',
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
            'rendering.factory',
            'rendering.strategies.renderer_2d',
            'rendering.strategies.renderer_3d',
            'rendering.strategies.special_renderer',
            'rendering.axes.axes_2d',
            'rendering.axes.axes_3d',
            'rendering.geometry.cube_3d',
            'rendering.geometry.pie_3d',
            'rendering.interfaces.i_chart_renderer',
        ]
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PyQt5', 'PySide2', 'PySide6'],
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
    name='StuGoCO2_Explorer',
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
