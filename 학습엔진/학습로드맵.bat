@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
  start "roadmap-server" py -m http.server 8765
  goto open
)
where python >nul 2>&1
if %errorlevel%==0 (
  start "roadmap-server" python -m http.server 8765
  goto open
)
echo Python is required. Install Python, then run this file again.
pause
exit /b 1
:open
timeout /t 1 /nobreak >nul
rem %% is a literal %; otherwise cmd treats URL escapes like %ED% as variables.
start "" "http://127.0.0.1:8765/%%ED%%95%%99%%EC%%8A%%B5%%EB%%A1%%9C%%EB%%93%%9C%%EB%%A7%%B5.html"
