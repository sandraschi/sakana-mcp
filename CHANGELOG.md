# Changelog — sakana-mcp

## Unreleased

- Fix: `/api/health` is now an instant liveness probe (`{"ok": true}`, ~0.2s).
  It previously ran full Docker diagnostics (~6s) and the fleet launcher (2s
  probe timeout) could never start the backend.
- Fix: `mcpb/manifest.json` uses `${__dirname}` instead of `${PWD}` (Claude
  Desktop does not expand `${PWD}` — the packed bundle could never start).
- Fix: justfile `lint`/`fix`/`check-sec`/`audit-deps` no longer `Set-Location`
  on its own recipe line (each `just` line is a separate shell — the follow-up
  command ran in the wrong directory).
- Fix: ruff enforces `T20` (no `print` in server code) and no longer silences
  `S110`/`S112` (`except: pass`).
- Fix: e2e backend-health spec probes `/api/health` (was `/health`, 404).
- Fix: DashboardPage reads runtime/docker/tree health from `/api/status`
  (matches the new minimal `/api/health` contract).
- Fix: Biome config migrated to CLI schema 2.4.16 (`biome ci` runs again).
- Add: `POST /api/shutdown` orderly exit, `GET /api/v1/diagnostics`,
  `GET /api/skills`, `GET /api/llm/discover`, `GET /api/llm/models`,
  `GET /api/llm/onboarding` on the webapp backend.
- Add: MCP `sakana_shutdown` self-termination tool; tool annotations
  (`READ_ONLY`/`MUTATING`) and dialogic `{success, message, data}` returns.
- Add: `tests/` smoke suite (manifest validity, MCPB entry import, health
  contract) + Windows CI workflow (ruff, format, pytest, tsc, biome).
- Add: `.env.example`, `.gitattributes`, `.cursorrules`/`.windsurfrules`,
  `.claude-plugin` session hook, `llms.txt`/`llms-full.txt`, `glama.json`,
  `docs/ONBOARDING.md`, `renovate.json`, `.pre-commit-config.yaml`.
