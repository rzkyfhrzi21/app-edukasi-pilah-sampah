@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Edukasi Recycle Bin - Run Menu

set "PROJECT_DIR=%~dp0"
set "ROOT_DIR=%PROJECT_DIR:~0,-1%"
set "PS1=%PROJECT_DIR%dev-menu.ps1"

set "CONSTRUCT_DIR=D:\Apps\Construct 2"
set "CONSTRUCT_EXE=D:\Apps\Construct 2\Construct2.exe"
set "DOWNLOADS_DIR=C:\Users\rizky\Downloads"
set "URL_GEMINI=https://gemini.google.com/notebook/1a4fb2d1-ee63-4170-899a-e1ff2aff3aa8"
set "URL_CHATGPT=https://chatgpt.com/share/6af25e4c-74c0-83ec-8f0a-a2aa0009e4c8?ogimg=plain"

REM ============================================================
REM  Mode panggil langsung:  call dev-menu.bat <nomor>
REM  (dipakai run.bat)
REM ============================================================
set "DIRECT=%~1"
if not "%DIRECT%"=="" (
    set "CHOICE=%DIRECT%"
    goto DISPATCH
)

:MENU_LOOP
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Action menu
set "CHOICE="
set /p "CHOICE= Pilih opsi [1-8/E/0]: "

:DISPATCH
if "%CHOICE%"=="" exit /b
if "%CHOICE%"=="1" goto CMD_1
if "%CHOICE%"=="2" goto CMD_2
if "%CHOICE%"=="3" goto CMD_3
if "%CHOICE%"=="4" goto CMD_4
if /i "%CHOICE%"=="E" goto CMD_4
if "%CHOICE%"=="5" goto CMD_5
if "%CHOICE%"=="6" goto CMD_6
if "%CHOICE%"=="7" goto CMD_7
if "%CHOICE%"=="8" goto CMD_8
if "%CHOICE%"=="0" exit /b

echo.
echo   [!] Pilihan tidak valid. Silakan coba lagi.
timeout /t 2 /nobreak >nul
goto MENU_LOOP

REM ============================================================
REM  [1] Buka Semua: Construct 2, 3 tab terminal di jendela WT
REM      yang sama (OpenCode, OMP, Root CMD), Explorer 3 tab,
REM      dan Browser (Gemini + ChatGPT).
REM ============================================================
:CMD_1
echo.
echo   [*] Buka semua (Construct 2, tab terminal, Explorer, browser)...
call :OPEN_CONSTRUCT
call :OPEN_TAB_IF_ABSENT "OpenCode" "%ROOT_DIR%" "opencode"
call :OPEN_TAB_IF_ABSENT "OMP"      "%ROOT_DIR%" "omp"
call :OPEN_BLANK_IF_ABSENT "Root CMD" "%ROOT_DIR%"
call :OPEN_EXPLORER
call :OPEN_BROWSER
echo   [OK] Semua komponen terbuka. Salin teks perintah di tiap tab, tempel, ENTER.
goto DONE

:CMD_2
echo.
echo   [*] Membuka Construct 2...
call :OPEN_CONSTRUCT
goto DONE

:CMD_3
echo.
echo   [*] Membuka browser: tab Gemini dan tab ChatGPT...
call :OPEN_BROWSER
goto DONE

:CMD_4
echo.
echo   [*] Membuka File Explorer: 1 jendela, 4 tab (root, assets, docs, downloads)...
call :OPEN_EXPLORER
echo   [OK] File Explorer terbuka (4 tab).
goto DONE

:CMD_5
echo.
echo   [*] Membuka Hapus Background Gambar (GUI)...
start "" pythonw "%PROJECT_DIR%hapus-bg.py"
if errorlevel 1 (
    call :RUN_TAB "Hapus Background GUI" "%ROOT_DIR%" "python \"%PROJECT_DIR%hapus-bg.py\""
)
echo   [OK] GUI Hapus Background Gambar dijalankan.
goto DONE

:CMD_6
echo.
echo   [*] Membuka tab terminal (OpenCode, OMP, Root CMD) di jendela ini...
call :OPEN_TAB_IF_ABSENT "OpenCode"   "%ROOT_DIR%" "opencode"
call :OPEN_TAB_IF_ABSENT "OMP"        "%ROOT_DIR%" "omp"
call :OPEN_BLANK_IF_ABSENT "Root CMD" "%ROOT_DIR%"
echo   [OK] Tab terminal siap di jendela Windows Terminal yang sama.
goto DONE

:CMD_7
echo.
echo   [*] Membuka Konversi Audio MP3 ke WAV Construct 2 (GUI)...
start "" pythonw "%PROJECT_DIR%audio-to-wav.py"
if errorlevel 1 (
    call :RUN_TAB "Konversi Audio WAV" "%ROOT_DIR%" "python \"%PROJECT_DIR%audio-to-wav.py\""
)
echo   [OK] GUI Konversi Audio WAV dijalankan.
goto DONE

:CMD_8
echo.
echo   [*] Konversi Gambar ke Hitam-Putih / Locked Grayscale...
echo.
echo   Drag ^& drop file/folder ke atas hapus-bg.bat setelah menekan Enter,
echo   ATAU masukkan path file/folder di bawah ini:
echo.
set "BW_INPUT="
set /p "BW_INPUT= Path file atau folder (Enter = batal): "
if "%BW_INPUT%"=="" (
    echo   [!] Dibatalkan.
    goto DONE
)
echo.
echo   [*] Memproses ke hitam-putih: %BW_INPUT%
python "%PROJECT_DIR%hapus-bg.py" --bw "%BW_INPUT%"
echo.
echo   [OK] Konversi hitam-putih selesai. Cek folder output_bw di lokasi file sumber.
goto DONE

REM ------------------------------------------------------------
:DONE
if not "%DIRECT%"=="" (
    timeout /t 2 /nobreak >nul
    exit /b
)
timeout /t 3 /nobreak >nul
goto MENU_LOOP

REM ============================================================
REM  OPEN_CONSTRUCT
REM  Menjalankan Construct 2 jika belum berjalan.
REM ============================================================
:OPEN_CONSTRUCT
if not exist "%CONSTRUCT_EXE%" (
    echo   [X] Tidak ditemukan: %CONSTRUCT_EXE%
    goto :eof
)
tasklist /FI "IMAGENAME eq Construct2.exe" 2>nul | find /I "Construct2.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo   [~] Construct 2 sudah berjalan, dilewati.
    goto :eof
)
echo   [+] Membuka Construct 2...
start "" /d "%CONSTRUCT_DIR%" "%CONSTRUCT_EXE%"
timeout /t 1 /nobreak >nul
goto :eof

REM ============================================================
REM  OPEN_BROWSER
REM  Membuka URL yang belum terbuka di browser (anti-duplikat).
REM ============================================================
:OPEN_BROWSER
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Action browser -Urls "%URL_GEMINI%,%URL_CHATGPT%"
goto :eof

REM ============================================================
REM  OPEN_EXPLORER
REM  Membuka 4 folder sebagai TAB di SATU jendela Explorer
REM  (root, assets, docs, downloads) dan reuse jendela jika sudah ada.
REM ============================================================
:OPEN_EXPLORER
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -Action explorer -RootDir "%ROOT_DIR%" -AssetsDir "%ROOT_DIR%\assets" -DocsDir "%ROOT_DIR%\docs" -DownloadsDir "%DOWNLOADS_DIR%"
goto :eof

REM ============================================================
REM  OPEN_TAB_IF_ABSENT <Judul> <Folder> <Perintah>
REM ============================================================
:OPEN_TAB_IF_ABSENT
powershell -NoProfile -ExecutionPolicy Bypass -Command "$t = '%~1'; $found = Get-Process WindowsTerminal -ErrorAction SilentlyContinue | ForEach-Object { $_.MainWindowTitle } | Where-Object { $_ -like ('*' + $t + '*') }; if ($found) { exit 0 } else { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    echo   [~] Tab "%~1" sudah terbuka, dilewati.
    timeout /t 1 /nobreak >nul
    goto :eof
)
call :OPEN_TAB "%~1" "%~2" "%~3"
goto :eof

REM ============================================================
REM  OPEN_BLANK_IF_ABSENT <Judul> <Folder>
REM ============================================================
:OPEN_BLANK_IF_ABSENT
powershell -NoProfile -ExecutionPolicy Bypass -Command "$t = '%~1'; $found = Get-Process WindowsTerminal -ErrorAction SilentlyContinue | ForEach-Object { $_.MainWindowTitle } | Where-Object { $_ -like ('*' + $t + '*') }; if ($found) { exit 0 } else { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    echo   [~] Tab "%~1" sudah terbuka, dilewati.
    timeout /t 1 /nobreak >nul
    goto :eof
)
call :OPEN_BLANK "%~1" "%~2"
goto :eof

REM ============================================================
REM  OPEN_TAB <Judul> <Folder> <Perintah>
REM  Membuka tab baru di jendela Windows Terminal aktif (-w 0).
REM ============================================================
:OPEN_TAB
where wt >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    wt -w 0 new-tab -d "%~2" --title "%~1" cmd.exe /K "echo %~3"
) else (
    start "%~1" /d "%~2" cmd /K "echo %~3"
)
timeout /t 1 /nobreak >nul
goto :eof

REM ============================================================
REM  RUN_TAB <Judul> <Folder> <Perintah>
REM  Membuka tab baru di jendela Windows Terminal aktif (-w 0)
REM  dan langsung mengeksekusi perintahnya.
REM ============================================================
:RUN_TAB
where wt >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    wt -w 0 new-tab -d "%~2" --title "%~1" cmd.exe /K "%~3"
) else (
    start "%~1" /d "%~2" cmd /K "%~3"
)
timeout /t 1 /nobreak >nul
goto :eof

REM ============================================================
REM  OPEN_BLANK <Judul> <Folder>
REM  Membuka tab CMD kosong di jendela Windows Terminal aktif (-w 0).
REM ============================================================
:OPEN_BLANK
where wt >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    wt -w 0 new-tab -d "%~2" --title "%~1" cmd.exe
) else (
    start "%~1" /d "%~2" cmd
)
timeout /t 1 /nobreak >nul
goto :eof
