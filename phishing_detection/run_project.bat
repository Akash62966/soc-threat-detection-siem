@echo off
title Phishing URL Detection Using Machine Learning
echo =======================================================
echo   Starting Phishing URL Detection System...
echo =======================================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Open default browser to port 5051 after a brief delay
start http://127.0.0.1:5051

:: Launch Flask application on port 5051
python app.py

pause
