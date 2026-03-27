@echo off
setlocal enabledelayedexpansion

echo === Win Whisper local build ===
echo.

:: 1. Install / sync dependencies
echo [1/3] Installing dependencies...
pip install -e . --quiet
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: pyinstaller install failed
    pause
    exit /b 1
)

:: Kill running instance so PyInstaller can overwrite the exe
taskkill /f /im win-whisper.exe >nul 2>&1

:: 2. Build exe
echo [2/3] Building exe with PyInstaller...
pyinstaller win-whisper.spec --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

:: 3. Verify output
echo [3/3] Verifying output...
if not exist "dist\win-whisper.exe" (
    echo ERROR: dist\win-whisper.exe not found
    pause
    exit /b 1
)

for %%F in ("dist\win-whisper.exe") do set SIZE=%%~zF
set /a SIZE_MB=!SIZE! / 1048576
echo OK: dist\win-whisper.exe  (!SIZE_MB! MB)

echo.
echo Build successful.
pause