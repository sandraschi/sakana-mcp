# Onboarding — sakana-mcp

Get from zero to a first live research loop in ~15 minutes.

## What this is for

`sakana-mcp` wraps **Sakana AI Scientist v2** so an agent (or you, via the
dashboard at `http://127.0.0.1:10862`) can run autonomous research loops:
pick a task → plan → generate hypotheses → execute in a Docker sandbox →
monitor tree health → VLM-review the manuscript. Everything persists under
`research_vault/` for later RAG indexing.

## What it costs / what you need

- **Docker Desktop** (free) — execution is Docker-only by design; model-generated
  experiment code never runs on your host. The `scientist-executor` service can
  use your NVIDIA GPU when present.
- **A Gemini API key** (`GEMINI_API_KEY`, pay-per-use) — for live ideation and
  VLM review. Without it the server runs in **FALLBACK [MOCK] MODE** with
  deterministic sample hypotheses (the dashboard says so explicitly — that badge
  is real state, not a demo).
- **S2 API key** (`S2_API_KEY`, free) — only for literature-heavy workflows.
- **The vendor checkout** (`vendor/ai-scientist-v2`, gitignored) — live ideation
  imports `ai_scientist` from there; missing checkout also means fallback mode.

No wrappee to install, no account besides the keys above.

## Setup

1. Copy `.env.example` to `.env` and fill `GEMINI_API_KEY` (and `S2_API_KEY`).
2. Clone AI Scientist v2 into `vendor/ai-scientist-v2` (or set
   `AI_SCIENTIST_V2_PATH`).
3. `docker compose up --build` (builds `sakana-mcp` + `scientist-executor`).
4. `just serve` (or `webapp/start.ps1`) — backend `:10863`, frontend `:10862`.
5. Open the dashboard, work the **Go Live Checklist** on the hero card: it flips
   each item DONE as Docker/keys/vendor come online, then auto-hides.

## Sanity check

- Backend: `GET http://127.0.0.1:10863/api/health` → `{"ok": true}` in <1s.
- Status: `GET /api/status` → `"runtime": {"mode": "live", ...}` once keys and
  vendor are present (else `"fallback"` — expected, not broken).
- MCP: `research_library()` → 2 builtin tasks; `sakana_help()` → loop order.

## Pitfalls

- `/api/health` slower than ~1s means you are hitting something else on `:10863`
  (the probe is intentionally minimal — see CHANGELOG 2026-10-31).
- `docker compose` warning about blank `S2_API_KEY` is harmless until you run
  literature workflows.
- The MCP stdio server spawns with `cwd=C:\Windows\System32` (Claude Desktop) —
  all repo paths resolve against the repo root, never CWD (BUG-063 pattern).
- Fallback mode is **declared** (`mode: "fallback"`, `[MOCK]` badges) — the day
  the dashboard stops telling you which mode it is in, file a bug.
