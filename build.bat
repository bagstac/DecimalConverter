@echo off
setlocal

echo ============================================================
echo  Decimal Convertor - Build Script
echo ============================================================
echo.

:: ── Step 1: Verify Python ────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Make sure Python is installed and on PATH.
    pause
    exit /b 1
)

:: ── Step 2: Install / upgrade build and runtime dependencies ─────────────────
echo Installing dependencies...
pip install --upgrade pyinstaller pystray Pillow
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

:: ── Step 3: Clean previous build output ──────────────────────────────────────
if exist build              rmdir /s /q build
if exist dist               rmdir /s /q dist
if exist installer_output   rmdir /s /q installer_output

:: ── Step 4: Build standalone executable ──────────────────────────────────────
echo.
echo Building executable...
pyinstaller --onefile --windowed --name "DecimalConverter" --icon "DecimalConverter.png" --add-data "DecimalConverter.png;." --add-data "version.txt;." decimal_convertor.py
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)
echo Executable built: dist\DecimalConvertor.exe

:: ── Step 5: Locate Inno Setup compiler (ISCC.exe) ────────────────────────────
echo.
echo Locating Inno Setup compiler...

set ISCC=

:: Check PATH first
where ISCC.exe >nul 2>&1
if not errorlevel 1 (
    set ISCC=ISCC.exe
    goto :found_iscc
)

:: Check common installation directories
for %%D in (
    "%ProgramFiles(x86)%\Inno Setup 6"
    "%ProgramFiles%\Inno Setup 6"
    "%ProgramFiles(x86)%\Inno Setup 5"
    "%ProgramFiles%\Inno Setup 5"
) do (
    if exist "%%~D\ISCC.exe" (
        set "ISCC=%%~D\ISCC.exe"
        goto :found_iscc
    )
)

echo ERROR: Inno Setup compiler (ISCC.exe) not found.
echo        Download and install Inno Setup from https://jrsoftware.org/isinfo.php
echo        then re-run this script.
pause
exit /b 1

:found_iscc
echo Found: %ISCC%

:: ── Step 6: Compile the installer ────────────────────────────────────────────
echo.
echo Compiling installer...
"%ISCC%" installer.iss
if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed.
    pause
    exit /b 1
)

:: ── Done ──────────────────────────────────────────────────────────────────────
echo.
echo ============================================================
echo  All done!
echo  Installer : installer_output\DecimalConvertorSetup.exe
echo ============================================================
echo.
pause
