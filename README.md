## sakana-mcp

MCP server that wraps Sakana AI Scientist v2 so Cursor can act as a research director for autonomous scientific loops.

## Documentation Map

- `README.md` (this file): entrypoint and quick start
- `docs/README.md`: full docs index
- `docs/architecture/README.md`: system architecture and component boundaries
- `docs/researcher/README.md`: researcher-facing workflow (ideate -> execute -> status -> review)
- `docs/operations/README.md`: Docker, safety model, runbooks, and troubleshooting

## Core Guarantees

- Tool-based orchestration: MCP tools map to ideation, execution, review, and status loops
- Sandbox-first execution: experiment code runs in Docker to reduce host contamination risk
- Deep-memory export: run artifacts are persisted in `research_vault` for downstream RAG indexing

## Tool Surface

- `research_ideate`: generate 5 hypotheses using AI-Scientist v2 ideation if available
- `research_execute`: run experiment manager in Docker with `num_workers` and `max_debug_depth`
- `research_status`: summarize buggy/non-buggy tree nodes from run artifacts
- `research_review`: run VLM figure/caption/reference review on a produced PDF

## Environment Variables

- `GEMINI_API_KEY`: required for Gemini-backed ideation/review paths
- `S2_API_KEY`: Semantic Scholar key for literature-heavy workflows
- `RESEARCH_VAULT_PATH`: optional; defaults to `./research_vault`
- `AI_SCIENTIST_V2_PATH`: optional; defaults to `./vendor/ai-scientist-v2`

## Quick Start

1. Clone this repo and ensure `vendor/ai-scientist-v2` exists.
2. Set required environment variables.
3. Build Docker images:
   - `docker compose build`
4. Run MCP server locally:
   - `python -m sakana_mcp.server`

## Safety Position

Docker is strongly recommended and treated as the default execution path for experiments because AI-Scientist v2 executes model-generated code.

