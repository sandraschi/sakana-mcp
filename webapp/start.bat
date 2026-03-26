@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PS1=%SCRIPT_DIR%start.ps1"

if not exist "%PS1%" (
  echo [ERROR] Missing PowerShell launcher: %PS1%
  exit /b 1
)

where pwsh >nul 2>nul
if %ERRORLEVEL%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
  exit /b %ERRORLEVEL%
)

where powershell >nul 2>nul
if %ERRORLEVEL%==0 (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
  exit /b %ERRORLEVEL%
)

echo [ERROR] Neither pwsh nor powershell found in PATH.
exit /b 1

