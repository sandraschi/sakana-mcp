# Development — sakana-mcp

## Layout

- `src/sakana_mcp/server.py` — FastMCP 3.4 stdio server (8 tools, 3 prompts,
  2 custom REST routes). Entry: `python -m sakana_mcp`.
- `webapp/backend/app.py` — FastAPI dashboard backend (`uvicorn app:app`,
  workdir `webapp/backend`).
- `webapp/frontend/` — React + Vite + Tailwind dashboard (`bun install`,
  `bun x tsc --noEmit`, `bun x @biomejs/biome ci .`).
- `tests/` — pytest smoke suite (manifest/tool sync, backend contract).
- `native/` + `src-tauri/` — Tauri shell (backend.rs: free_port, backend-status emit).
- `research_vault/` — runtime artifacts (gitignored). `vendor/` — upstream clone (gitignored).

## Gates (all must pass)

```powershell
uv run ruff check src/ webapp/backend tests/
uv run ruff format src/ webapp/backend tests/ --check
uv run mypy src/
uv run --extra test pytest tests/ -q
# frontend:
bun x tsc --noEmit; bun x @biomejs/biome ci .
```

Or `just lint` / `just test` / `just check`. CI (`.github/workflows/ci.yml`)
runs the same set on Windows.

## Conventions

- Tools return `{"success", "message", ...}`; docstrings carry `## Return Format`
  + `## Examples`; params use `Annotated[..., Field(...)]` (no `Args:` blocks).
- `/api/health` must stay an instant liveness probe (launcher: 2s timeout).
- Never commit `.env`, `research_vault/`, `logs/`, `*.bak`, `*.mcpb`, `mcpb/src/`.
