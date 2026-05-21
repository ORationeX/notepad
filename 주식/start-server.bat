@echo off
cd /d "%~dp0"
echo Smart Asset Rebalancer local server
echo.
echo Open this address in your browser:
echo   http://localhost:8787/
echo.
node server.js
pause
