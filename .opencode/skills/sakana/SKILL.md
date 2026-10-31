---
name: sakana
description: Operate the sakana-mcp research control plane (ideate, execute, status, review)
---

# Sakana skill

Coordinate autonomous research loops through the sakana-mcp MCP server.

## Tool catalog (all on the `sakana-mcp` server)

- `sakana_help` — catalog + canonical loop order. Call first when unsure.
- `research_library` / `research_workflow_plan` — pick a task, get the step plan.
- `research_ideate` — 5 hypotheses (live `ai_scientist_v2` mode or declared fallback).
- `research_execute` — Docker-only experiment run; read the returned log paths.
- `research_status` — tree health (good/buggy nodes, stages).
- `research_review` — VLM critique of a manuscript PDF.
- `sakana_shutdown` — graceful stop (needs `confirm: true`).

## Workflows

1. **New research thread**: library → workflow_plan → ideate → execute → status
   (poll) → review.
2. **Resume a run**: status first (stages + tree health tell you where it stopped).
3. **Triage a failure**: execute's `stderr_log` path, then status for buggy nodes.

## Rules

- Never pass `allow_host_execution: true` unless the user explicitly asks;
  execution stays in the `scientist-executor` container.
- Dashboard: backend `:10863` (`/api/health` <1s), frontend `:10862`.
- All tools answer `{"success", "message", ...}` — surface `message` to the user.
