@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  라인소프트를 브라우저에서 http 로 엽니다.
echo  이 창을 닫으면 서버도 함께 종료됩니다.
echo.

start "" "http://127.0.0.1:5500/"
py -m http.server 5500 --bind 127.0.0.1
if errorlevel 1 (
  echo Python으로 서버를 켜지 못했습니다. Node로 다시 시도합니다.
  npx --yes serve -l 5500 .
)
pause
