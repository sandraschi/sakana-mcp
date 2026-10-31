# Pre-commit Biome gate — resolves tooling absolutely (no PATH dependence).
# Fleet hook-scripts rule: bare `npx` fails under non-interactive pre-commit.
$ErrorActionPreference = "Stop"
$frontend = Join-Path $PSScriptRoot ".." "webapp" "frontend"
$nodeModulesBiome = Join-Path $frontend "node_modules" ".bin" "biome.json.cmd"
$bunx = Join-Path $env:USERPROFILE ".bun" "bin" "bunx.cmd"

if (Test-Path -LiteralPath $nodeModulesBiome) {
  & $nodeModulesBiome ci $frontend
} elseif (Test-Path -LiteralPath $bunx) {
  & $bunx @biomejs/biome ci $frontend
} else {
  & npx @biomejs/biome ci $frontend
}
exit $LASTEXITCODE
