# Tools — sakana-mcp

Source of truth for names/shapes is the live server (`sakana_help`, `GET
/api/v1/diagnostics`); `tests/test_manifest.py` fails the build if
`mcpb/manifest.json` or `glama.json` drift from it.

## MCP tools (stdio)

| Tool | Kind | What it does |
|---|---|---|
| `sakana_help` | read-only | catalog + canonical loop order |
| `research_ideate` | mutating (vault write) | 5 hypotheses (live or fallback) |
| `research_execute` | destructive (spawns Docker) | experiment manager in sandbox |
| `research_status` | read-only | tree health + stages |
| `research_review` | read-only (+vault write) | VLM figure/caption review of a PDF |
| `research_library` | read-only | builtin + custom task catalog |
| `research_workflow_plan` | read-only | 4-step guided plan for a task |
| `sakana_shutdown` | destructive | graceful self-termination (confirm) |

Plus 3 prompts: `research_director`, `workflow_director`, `review_critic`
(served from `prompts/*.md`).

## REST (dashboard backend :10863)

Health/status: `GET /api/health`, `GET /api/status`, `GET /api/v1/diagnostics`,
`POST /api/shutdown`. Loop: `POST /api/ideate`, `POST /api/execute`,
`POST /api/review`, `GET /api/workflow/plan`. Vault: `GET /api/vault/list`,
`GET /api/vault/read`. LLM: `GET /api/llm/{providers,discover,models,onboarding}`,
`POST /api/llm/chat`, `POST /api/llm/chat/stream` (SSE).
