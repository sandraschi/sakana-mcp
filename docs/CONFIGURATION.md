# Configuration — sakana-mcp

All configuration is via environment (see `.env.example`); no config files.

| Variable | Required | Default | Used by |
|---|---|---|---|
| `GEMINI_API_KEY` | for live mode | — | AI Scientist ideation + VLM review clients |
| `S2_API_KEY` | no (literature paths only) | — (blank warns in compose) | Semantic Scholar lookups |
| `RESEARCH_VAULT_PATH` | no | `./research_vault` | vault root (runs, logs, manifests, reviews) |
| `AI_SCIENTIST_V2_PATH` | no | `./vendor/ai-scientist-v2` | vendored AI Scientist checkout (gitignored) |
| `WEB_PORT` | no | backend port | set by the fleet launcher at start |

Ports (registry: `mcp-central-docs/operations/WEBAPP_PORTS.md`): backend
FastAPI `:10863`, frontend Vite `:10862`, health path `/api/health`.

Absent keys/vendor do not crash anything: ideation falls back to deterministic
hypotheses and the dashboard shows FALLBACK [MOCK] MODE.
