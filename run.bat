@echo off
TITLE Edukasi Recycle Bin Launcher

REM Buka VS Code mengarah ke folder proyek lewat CLI launcher agar detached (tidak bocor log Electron ke CMD)
call "C:\Users\rizky\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd" "D:\@UNDERGROUND DEV\@edukasi-recycle-bin" >nul 2>&1

call "%~dp0dev-menu.bat" %*
