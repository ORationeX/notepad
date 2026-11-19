@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>&1
if errorlevel 1 (
  echo Node.js is required. Install it from https://nodejs.org
  pause
  exit /b 1
)
set HOST=0.0.0.0
set PORT=8086
set EXTERNAL_PORT=7086
node server.js --open
pause
