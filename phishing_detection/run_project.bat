@echo off
title Phishing URL Detection Using Machine Learning
echo =======================================================
echo   Starting Phishing URL Detection System...
echo =======================================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

echo Launching Flask Server on http://127.0.0.1:5051...
echo Opening browser automatically...
echo.

python app.py

pause
