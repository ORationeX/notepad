@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Wall Street Intent Tracker
set "PY=.venv\Scripts\python.exe"
set "TRIES=0"

:ensure_venv
if exist "%PY%" goto check_streamlit

echo [setup] creating .venv
call :find_python
if not defined SYSPY (
  echo [error] Python not found. Install Python 3 and retry.
  pause
  exit /b 1
)
"%SYSPY%" -m venv .venv
if errorlevel 1 (
  echo [error] venv create failed
  pause
  exit /b 1
)

:check_streamlit
"%PY%" -c "import streamlit" 1>nul 2>nul
if errorlevel 1 goto install_deps
goto launch

:install_deps
echo [setup] installing requirements
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [warn] pip failed; recreating .venv
  rmdir /s /q .venv 2>nul
  set /a TRIES+=1
  if !TRIES! GEQ 3 (
    echo [error] setup failed 3 times. See run.log
    pause
    exit /b 1
  )
  goto ensure_venv
)

:launch
"%PY%" launch.py
if errorlevel 1 (
  echo [warn] server exited; restarting in 3s
  timeout /t 3 /nobreak >nul
  set /a TRIES+=1
  if !TRIES! GEQ 5 (
    echo [error] could not keep the server up. See run.log
    pause
    exit /b 1
  )
  goto check_streamlit
)

echo [info] server stopped.
pause
exit /b 0

:find_python
set "SYSPY="
where py >nul 2>nul
if not errorlevel 1 (
  for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "SYSPY=%%I"
)
if defined SYSPY goto :eof
where python >nul 2>nul
if not errorlevel 1 (
  for /f "delims=" %%I in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "SYSPY=%%I"
)
goto :eof
