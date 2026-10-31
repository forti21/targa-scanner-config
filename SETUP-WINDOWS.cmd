@echo off
cd /d "%~dp0"
py --version >nul 2>&1
if errorlevel 1 (
 echo Python non trovato. Installa Python da https://www.python.org/downloads/windows/ e riprova.
 pause
 exit /b 1
)
py -m pip install cryptography
if errorlevel 1 (pause & exit /b 1)
py scripts\setup_keys.py
if errorlevel 1 (pause & exit /b 1)
echo Apri GitHub: Settings - Secrets and variables - Actions - New repository secret.
echo Nome: REMOTE_CONFIG_SIGNING_KEY. Incolla il valore dagli appunti.
echo Poi apri Actions e avvia Pubblica configurazione firmata.
pause
