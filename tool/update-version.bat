@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
if errorlevel 1 (
  echo [ERROR] 저장소 루트로 이동하지 못했습니다.
  pause
  exit /b 1
)

set "SCRIPT=%~dp0update-version.py"
if not exist "%SCRIPT%" (
  echo [ERROR] 파일이 없습니다: %SCRIPT%
  pause
  exit /b 1
)

echo [버전 업데이트] SITE_ASSET_VERSION 갱신 및 HTML ?v= 일괄 적용
echo.

set "PY="
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 set "PY=python"
)

if not defined PY (
  echo.
  echo [ERROR] Python 3을 찾을 수 없습니다.
  echo Python 3을 설치하고 PATH에 추가한 뒤 다시 실행하세요.
  echo.
  pause
  exit /b 1
)

%PY% "%SCRIPT%"
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] update-version 실패. exit=%ERR%
  pause
  exit /b %ERR%
)
echo.
pause
endlocal