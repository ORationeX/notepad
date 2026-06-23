@echo off
:: UTF-8 코드페이지 강제 설정 (한글 깨짐 방지)
chcp 65001 > nul
title 미국 증시 하락 경보 대시보드 원클릭 실행기
color 0b

echo ======================================================================
echo    * 나스닥 하락장 위험 경보 대시보드 - 원클릭 실행기 *
echo ======================================================================
echo.

:: 파이썬 실행 가능 여부 사전 검사
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
echo [1단계] 기존 구동 중인 대시보드 포트(8501) 확인 및 해제 중...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501 ^| findstr LISTENING') do (
    echo   Releasing PID %%a ...
    taskkill /f /pid %%a 2>nul
)
echo.

echo [2단계] 야후 파이낸스 실시간 데이터 동기화 진행 중...
echo   (10년치 일별 데이터 로컬 Parquet 캐시 갱신 중. 잠시만 기다려 주세요...)
echo.
python run.py --fetch-only
if errorlevel 1 goto sync_fail
echo.
echo   [성공] 최신 데이터 동기화 완료!
goto sync_end

:sync_fail
echo.
echo   [경고] 야후 파이낸스 API 호출 실패. 기존에 캐싱된 데이터로 대시보드를 실행합니다.

:sync_end
echo.

echo [3단계] Streamlit 대시보드 웹 서버 실행 중...
echo   웹 브라우저를 통해 http://localhost:8501 주소로 연결됩니다.
echo   대시보드를 종료하려면 이 CMD 창을 닫아주십시오.
echo.
python -m streamlit run app.py --server.port 8501

echo.
exit
