# Troubleshooting — sakana-mcp

## Start failures

- **`FAIL: Backend not healthy after 20s`** — the launcher probes `/api/health`
  with a 2s timeout. If health is slow, something heavy got added to the probe
  path (2026-10-31 incident: health ran full Docker diagnostics, ~6s). Health
  must stay `{"ok": true}` and instant; diagnostics belong on `/api/status`.
- **Port held after kill** — `netstat -ano -p TCP | findstr 10863`, then
  `Stop-Process -Id <pid> -Force`. Session-0 holders are NSSM services: restart
  via services.msc, never taskkill.
- **`uv sync` locked exe** — a running server locks `.venv` entry points; stop
  the backend first, the existing venv keeps working meanwhile.

## Runtime

- **Dashboard shows FALLBACK [MOCK] MODE** — expected without `GEMINI_API_KEY`
  and `vendor/ai-scientist-v2`. Follow the hero Go Live Checklist.
- **Chat gets 404 from the dashboard** — the widget proxies `/api/llm/chat`
  through vite; if the backend predates that route, restart it (`POST
  /api/shutdown?confirm=true` or bounce the backend window).
- **Ollama 502s** — start Ollama (`:11434`) or set the widget model to a
  pulled model; `/api/llm/discover` reports what is reachable.
- **e2e `Backend health` fails** — it asserts `/api/health` (not `/health`).

## Packaging

- **`mcpb pack` says bunx missing** — use `just mcpb-pack` (shim fixes PATH);
  never pack with a hand-rolled command.
- **Bundle won't start on a real install** — check `mcpb/manifest.json` for
  non-spec `${...}` (only `${__dirname}` etc. are expanded); the repo audit
  (`audit-mcpb-bundles.ps1`) rejects them.
