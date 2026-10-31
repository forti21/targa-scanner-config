@echo off
cd /d "%~dp0"
py --version >nul 2>&1
if errorlevel 1 (
 echo Python non trovato. Installa Python da https://www.python.org/downloads/windows/ e riprova.
 pause
 exit /b 1
)
py pannello\admin.py
if errorlevel 1 pause
