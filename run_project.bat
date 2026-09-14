@echo off
title SOC Threat Detection & SIEM Dashboard
echo =======================================================
echo   Starting SOC Threat Detection & SIEM Dashboard...
echo =======================================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Open default browser to port 5050 after a brief delay
start http://127.0.0.1:5050

:: Launch Flask application on port 5050
python app.py

pause
