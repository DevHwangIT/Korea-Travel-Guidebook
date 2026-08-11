@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0.."
if errorlevel 1 (
  echo [ERROR] Failed to change to project root.
  pause
  exit /b 1
)

set "SCRIPT=%~dp0content-admin.py"
if not exist "%SCRIPT%" (
  echo [ERROR] Missing: %SCRIPT%
  pause
  exit /b 1
)

echo [Content Admin] CMS: http://127.0.0.1:8765/
echo [Content Admin] Viewer: http://127.0.0.1:8765/viewer
echo.
echo ※ Open http://127.0.0.1:8765/ (left sidebar = admin CMS).
echo ※ After save: Ctrl+F5 on the viewer, or reopen /viewer.
echo ※ Do NOT open index.html via file:// — use the server URLs above.
echo ※ If an old server window is still open, press Ctrl+C there first, then re-run.
echo Stop: Ctrl+C
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
  echo [ERROR] content-admin failed. exit=%ERR%
  pause
  exit /b %ERR%
)
endlocal
