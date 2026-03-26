param(
  [int]$FrontendPort = 10720,
  [int]$BackendPort = 10721
)

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
  if (-not $conns) { return }
  $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
  foreach ($pid in $pids) {
    if ($pid -and $pid -ne 0) {
      try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
    }
  }
}

Stop-PortProcess -Port $FrontendPort
Stop-PortProcess -Port $BackendPort

Write-Host "Starting sakana-mcp webapp..."
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "Backend:  http://localhost:$BackendPort"

Push-Location (Join-Path $PSScriptRoot "backend")
Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "$BackendPort", "--reload")
Pop-Location

Push-Location (Join-Path $PSScriptRoot "frontend")
Start-Process -FilePath "npm" -ArgumentList @("install")
Start-Process -FilePath "npm" -ArgumentList @("run", "dev", "--", "--port", "$FrontendPort", "--host", "127.0.0.1")
Pop-Location

