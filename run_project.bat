@echo off
title SOC Threat Detection & SIEM Dashboard
echo =======================================================
echo   Starting SOC Threat Detection & SIEM Dashboard...
echo =======================================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

echo Launching Flask Server on http://127.0.0.1:5050...
echo Opening browser automatically...
echo.

python app.py

pause
