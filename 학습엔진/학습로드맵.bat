@echo off
setlocal
cd /d "%~dp0"
set PORT=
set MODE=
for /f "tokens=1,2" %%A in ('powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0roadmap-port.ps1"') do (
  set PORT=%%A
  set MODE=%%B
)
if not defined PORT (
  echo 사용할 수 있는 포트를 찾지 못했습니다.
  pause
  exit /b 1
)
if /I "%MODE%"=="open" goto open

:startserver
where py >nul 2>&1
if %errorlevel%==0 (
  start "roadmap-server" /D "%~dp0" py "%~dp0roadmap-server.py" %PORT%
  goto waitopen
)
where python >nul 2>&1
if %errorlevel%==0 (
  start "roadmap-server" /D "%~dp0" python "%~dp0roadmap-server.py" %PORT%
  goto waitopen
)
echo Python is required. Install Python, then run this file again.
pause
exit /b 1

:waitopen
powershell -NoProfile -ExecutionPolicy Bypass -Command "for($i=0;$i -lt 25;$i++){try{$r=Invoke-WebRequest -Uri 'http://127.0.0.1:%PORT%/api/health' -UseBasicParsing -TimeoutSec 1;if($r.StatusCode -eq 200){exit 0}}catch{};Start-Sleep -Milliseconds 200}" >nul 2>&1

:open
rem %% is a literal percent. cmd would otherwise treat %ED as a variable.
start "" "http://127.0.0.1:%PORT%/%%ED%%95%%99%%EC%%8A%%B5%%EB%%A1%%9C%%EB%%93%%9C%%EB%%A7%%B5.html"
endlocal
