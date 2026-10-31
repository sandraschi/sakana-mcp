set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Serve ---

# Start backend + frontend via the fleet launcher (run once, certifies the launcher)
serve:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\webapp\start.ps1"

# Backend only (probes /api/health, fails the run when unhealthy)
serve-backend:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\webapp\start.ps1" -BackendOnly

# --- Quality ---

# Execute Ruff lint + format check (repo root only; frontend has its own biome gate)
lint:
    uv run ruff check .; uv run ruff format . --check

# Ruff autofix + format (repo root) and Biome write (frontend)
fix:
    uv run ruff check . --fix --unsafe-fixes; uv run ruff format .; cd "{{justfile_directory()}}\webapp\frontend"; npx @biomejs/biome check --write .

# Typecheck: mypy for the server, tsc for the frontend
check:
    uv run mypy src/
    cd "{{justfile_directory()}}\webapp\frontend"; npx tsc --noEmit

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    uv run safety check

# --- Testing ---

# Fast backend smoke tests (no Docker required)
test:
    uv run pytest tests/ -q

# Run e2e Playwright tests
e2e:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\..\mcp-central-docs\scripts\playwright-audit.ps1" -RepoPath "{{justfile_directory()}}"

# Pre-Tauri browser walk (requires running stack: just serve first)
cua-webapp-test:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\scripts\cua-webapp-test.py"

# --- Packaging ---

# Pack the Claude Desktop (.mcpb) bundle via the fleet shim pipeline
mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\scripts\mcpb-pack.ps1"

# --- Bootstrap ---

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
