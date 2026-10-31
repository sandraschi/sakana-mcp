# Fleet shim (do not vendor the pipeline here): canonical pack lives in mcp-central-docs.
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$reposRoot = Split-Path -Parent $repoRoot
$engine = Join-Path $reposRoot "mcp-central-docs\scripts\fleet-mcpb-pack.ps1"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $engine -RepoRoot $repoRoot
exit $LASTEXITCODE
