param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser,
    [switch]$NoOpen
)

$delegate = Join-Path $PSScriptRoot "webapp\start.ps1"
if (-not (Test-Path $delegate)) {
    Write-Host "ERROR: Missing $delegate" -ForegroundColor Red
    exit 1
}

$args = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $delegate)
if ($Headless) { $args += '-Headless' }
if ($BackendOnly) { $args += '-BackendOnly' }
if ($FrontendOnly) { $args += '-FrontendOnly' }
if ($NoBrowser) { $args += '-NoBrowser' }
if ($NoOpen) { $args += '-NoOpen' }

& powershell.exe @args
exit $LASTEXITCODE