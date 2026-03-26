## Operations Guide

## Why Docker is default

AI-Scientist v2 can execute model-generated code and spawn complex subprocesses. Containerized execution reduces host risk and improves run reproducibility.

## Prerequisites

- Docker Engine + Docker Compose
- NVIDIA runtime configured (for GPU execution path)
- API keys set:
  - `GEMINI_API_KEY`
  - `S2_API_KEY`

## Build and Start

From repo root:

- Build images:
  - `docker compose build`
- Run MCP service container:
  - `docker compose up sakana-mcp`

Or run MCP server on host Python while keeping execution in Docker:
- `python -m sakana_mcp.server`

## Runbook: standard research cycle

1. `research_ideate`
2. `research_execute`
3. `research_status` until desired stage coverage
4. `research_review` on generated manuscript PDF

## Troubleshooting

- `docker-compose.yml not found`
  - ensure command context is repo root
- `ai-scientist-v2 vendor directory missing`
  - clone to `vendor/ai-scientist-v2` or set `AI_SCIENTIST_V2_PATH`
- execution failure
  - inspect:
    - `research_vault/execute_last_stdout.log`
    - `research_vault/execute_last_stderr.log`
- no stage status output
  - verify run generated notes at `research_vault/runs/logs/stage_*/notes/stage_progress.json`

