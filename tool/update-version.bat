@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0.."
if errorlevel 1 (
  echo [ERROR] Failed to change to project root.
  pause
  exit /b 1
)

set "SCRIPT=%~dp0update-version.py"
if not exist "%SCRIPT%" (
  echo [ERROR] Missing: %SCRIPT%
  pause
  exit /b 1
)

echo [update-version] Rebuild food recommend catalog + bump SITE_ASSET_VERSION + HTML ?v=
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
  echo [ERROR] Python 3 not found.
  echo Install Python 3 and add it to PATH, then retry.
  echo.
  pause
  exit /b 1
)

%PY% "%SCRIPT%"
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] update-version failed. exit=%ERR%
  pause
  exit /b %ERR%
)
echo.
pause
endlocal
