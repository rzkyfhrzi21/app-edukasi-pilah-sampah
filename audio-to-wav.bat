@echo off
chcp 65001 >nul 2>&1
title Konversi Audio (MP3) ke WAV Construct 2

set "SCRIPT_DIR=%~dp0"

if "%~1"=="" (
    python "%SCRIPT_DIR%audio-to-wav.py"
    exit /b
)

echo.
echo   [*] Mengonversi file audio ke WAV Construct 2...
python "%SCRIPT_DIR%audio-to-wav.py" %*
echo.
pause
