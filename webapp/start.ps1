Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

param(
  [int]$FrontendPort = 10862,
  [int]$BackendPort = 10863
)

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
  if (-not $conns) { return }
  $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($procId in $pids) {
    if ($procId -and $procId -ne 0) {
      try { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } catch {}
    }
  }
}

Stop-PortProcess -Port $FrontendPort
Stop-PortProcess -Port $BackendPort

Write-Host "Starting sakana-mcp webapp..."
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "Backend:  http://localhost:$BackendPort"

Push-Location (Join-Path $PSScriptRoot "backend")
$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
if ($pythonCmd) {
  Start-Process -FilePath "py" -ArgumentList @("-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "$BackendPort", "--reload")
} else {
  Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "$BackendPort", "--reload")
}
Pop-Location

Push-Location (Join-Path $PSScriptRoot "frontend")
$frontendDir = (Get-Location).Path
# Use cmd.exe so npm.cmd is resolved reliably even when npm.ps1 policy differs.
Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", "cd /d `"$frontendDir`" && npm install && npm run dev -- --port $FrontendPort --host 127.0.0.1")
Pop-Location


