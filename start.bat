@echo off
setlocal

set "ROOT=%~dp0"
set "WEBAPP_START=%ROOT%webapp\start.bat"

if not exist "%WEBAPP_START%" (
  echo [ERROR] Missing launcher: %WEBAPP_START%
  exit /b 1
)

call "%WEBAPP_START%"
exit /b %ERRORLEVEL%

