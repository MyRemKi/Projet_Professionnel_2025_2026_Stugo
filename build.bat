@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ================================================================
echo   StuGo CO2 Explorer v6.1 - Build complet
echo   PyInstaller + Inno Setup
echo ================================================================
echo.

:: ── Verifier Python ──────────────────────────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python introuvable dans le PATH.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo Python    : %%v

:: ── Verifier PyInstaller ─────────────────────────────────────────────────────
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] PyInstaller non installe. Lancez : pip install pyinstaller
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python -m PyInstaller --version 2^>^&1') do echo PyInstaller : %%v

:: ── Localiser Inno Setup (guillemets autour de la valeur entiere) ─────────────
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if "!ISCC!"=="" (
    if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
    )
)
if "!ISCC!"=="" (
    echo [ERREUR] Inno Setup 6 introuvable.
    echo          Telechargez : https://jrsoftware.org/isdl.php
    pause & exit /b 1
)
echo Inno Setup : !ISCC!

:: ── Verifier les dependances Python ─────────────────────────────────────────
echo.
echo [*] Verification des dependances...
python -c "import PyQt6, matplotlib, pandas, openpyxl, squarify; print('    OK')" 2>&1
if errorlevel 1 (
    echo [ERREUR] Dependances manquantes :
    echo          pip install PyQt6 matplotlib pandas openpyxl squarify
    pause & exit /b 1
)

:: ── Etape 1 : PyInstaller ────────────────────────────────────────────────────
echo.
echo [1/2] Compilation PyInstaller (5-10 minutes, mode onefile)...
echo       Sortie : dist\StuGoCO2_Explorer.exe + dist\Admin_Logs.exe
echo.

if exist "build"                       rmdir /s /q "build"
if exist "dist\StuGoCO2"               rmdir /s /q "dist\StuGoCO2"
if exist "dist\StuGoCO2_Explorer.exe"  del /f /q "dist\StuGoCO2_Explorer.exe"
if exist "dist\Admin_Logs.exe"         del /f /q "dist\Admin_Logs.exe"

python -m PyInstaller build_all.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERREUR] PyInstaller a echoue.
    pause & exit /b 1
)

if not exist "dist\StuGoCO2_Explorer.exe" (
    echo [ERREUR] StuGoCO2_Explorer.exe introuvable dans dist\
    pause & exit /b 1
)
if not exist "dist\Admin_Logs.exe" (
    echo [ERREUR] Admin_Logs.exe introuvable dans dist\
    pause & exit /b 1
)
echo     OK : dist\ pret.

:: ── Etape 2 : Inno Setup ─────────────────────────────────────────────────────
echo.
echo [2/2] Compilation de l'installeur Inno Setup (3-10 minutes)...
echo       Sortie : dist\StuGoCO2_Setup_v6.1.exe
echo.

"!ISCC!" installer.iss
if errorlevel 1 (
    echo.
    echo [ERREUR] Inno Setup a echoue.
    pause & exit /b 1
)

if not exist "dist\StuGoCO2_Setup_v6.1.exe" (
    echo [ERREUR] L'installeur n'a pas ete cree.
    pause & exit /b 1
)

:: ── Resume ───────────────────────────────────────────────────────────────────
echo.
echo ================================================================
echo   BUILD TERMINE AVEC SUCCES
echo ================================================================
echo.
echo   Installeur : dist\StuGoCO2_Setup_v6.1.exe
echo.
echo   Mode onefile (tout embarque dans chaque exe) :
echo     - dist\StuGoCO2_Explorer.exe  (application principale)
echo     - dist\Admin_Logs.exe         (outil logs)
echo.
echo   Installation : %%LOCALAPPDATA%%\Programs\StuGo CO2 Explorer\
echo   Donnees user : %%LOCALAPPDATA%%\StuGoCO2\
echo ================================================================
pause
