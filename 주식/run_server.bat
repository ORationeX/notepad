@echo off
title ETF Portfolio Analyzer Server
cd /d "%~dp0"
echo ===================================================
echo   ETF Portfolio Analyzer Server Starting...
echo ===================================================
echo.
echo Launching dashboard in browser: http://127.0.0.1:5000
start "" "http://127.0.0.1:5000"
echo.
echo Running server... (Press Ctrl+C in this window to stop)
python app.py
pause
