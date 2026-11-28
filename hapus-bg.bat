@echo off
chcp 65001 >nul 2>&1
title Hapus Background Gambar - PNG Transparan

set "SCRIPT_DIR=%~dp0"

REM Jika tidak ada file yang di-drag & drop ke file .bat ini, langsung buka jendela aplikasi (GUI)
if "%~1"=="" (
    python "%SCRIPT_DIR%hapus-bg.py"
    exit /b
)

REM Jika pengguna men-drag & drop file/folder ke atas hapus-bg.bat
echo.
echo   [*] Memproses file yang di-drop...
python "%SCRIPT_DIR%hapus-bg.py" %*
echo.
pause
