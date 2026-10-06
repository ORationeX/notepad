@echo off
cd /d "%~dp0"
:: UTF-8 코드페이지 강제 설정 (한글 깨짐 방지)
chcp 65001 > nul
title 나스닥 리밸런싱 공식 탐색
color 0b

echo ======================================================================
echo    * 나스닥 리밸런싱 공식 탐색 *
echo ======================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 goto python_error
goto python_ok

:python_error
echo [오류] 시스템에서 'python' 명령어를 실행할 수 없습니다.
echo       Python이 설치되어 있고 환경 변수(PATH)에 등록되어 있는지 확인해 주세요.
echo.
pause
exit /b

:python_ok
echo [1단계] 기존 구동 중인 포트(8510) 확인 및 해제 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8510 ^| findstr LISTENING') do (
    echo   Releasing PID %%a ...
    taskkill /f /pid %%a 2>nul
)
echo.

echo [2단계] 야후 파이낸스 시세 동기화 중...
echo.
python run.py --fetch-only
if errorlevel 1 goto sync_fail
echo.
echo   [성공] 최신 시세 동기화 완료
goto sync_end

:sync_fail
echo.
echo   [경고] 시세 갱신에 실패한 종목이 있습니다. 저장된 시세가 있으면 그 데이터로 엽니다.

:sync_end
echo.
echo [3단계] 웹 화면 실행 중...
echo   브라우저에서 http://localhost:8510 으로 연결됩니다.
echo   종료하려면 이 창을 닫으세요.
echo.
python -m streamlit run app.py --server.port 8510

echo.
exit
