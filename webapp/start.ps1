param(
  [switch]$Headless,
  [int]$FrontendPort = 10862,
  [int]$BackendPort = 10863

# Fast port helpers (scripts/PortHelpers.ps1)
param(
  [switch]$Headless,
  [int]$FrontendPort = 10862,
  [int]$BackendPort = 10863
)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $procIds = Get-PortListenerPidsFast -Port $port
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


_RepoRootForPorts = Split-Path -Parent $PSScriptRoot
param(
  [switch]$Headless,
  [int]$FrontendPort = 10862,
  [int]$BackendPort = 10863
)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $procIds = Get-PortListenerPidsFast -Port $port
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


_PortHelpers = Join-Path param(
  [switch]$Headless,
  [int]$FrontendPort = 10862,
  [int]$BackendPort = 10863
)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $procIds = Get-PortListenerPidsFast -Port $port
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


_RepoRootForPorts 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath param(
  [switch]$Headless,
  [int]$FrontendPort = 10862,
  [int]$BackendPort = 10863
)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $procIds = Get-PortListenerPidsFast -Port $port
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


_PortHelpers) { . param(
  [switch]$Headless,
  [int]$FrontendPort = 10862,
  [int]$BackendPort = 10863
)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $procIds = Get-PortListenerPidsFast -Port $port
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


_PortHelpers }
)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$ErrorActionPreference = "Stop"

function Stop-PortProcess {
  param([int]$Port)
  $procIds = Get-PortListenerPidsFast -Port $port
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



