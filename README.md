[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.1.0-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

## sakana-mcp

MCP server that wraps Sakana AI Scientist v2 so Cursor can act as a research director for autonomous scientific loops.

## Documentation Map

- `README.md` (this file): entrypoint and quick start
- `docs/README.md`: full docs index
- `docs/architecture/README.md`: system architecture and component boundaries
- `docs/researcher/README.md`: researcher-facing workflow (ideate -> execute -> status -> review)
- `docs/operations/README.md`: Docker, safety model, runbooks, and troubleshooting
- `research_library/README.md`: sample research task catalog
- `prompts/README.md`: reusable prompt templates
- `skills/FASTMCP_3_1_SKILL.md`: FastMCP 3.1.0 operator skill card

## Core Guarantees

- Tool-based orchestration: MCP tools map to ideation, execution, review, and status loops
- Sandbox-first execution: experiment code runs in Docker to reduce host contamination risk
- Deep-memory export: run artifacts are persisted in `research_vault` for downstream RAG indexing

## Tool Surface

- `research_ideate`: generate 5 hypotheses using AI-Scientist v2 ideation if available
- `research_execute`: run experiment manager in Docker with `num_workers` and `max_debug_depth`
- `research_status`: summarize buggy/non-buggy tree nodes from run artifacts
- `research_review`: run VLM figure/caption/reference review on a produced PDF
- `research_library`: browse built-in + custom sample research missions
- `research_workflow_plan`: generate guided agentic step plan for a selected task

## Research Warehousing

All major events are appended to warehouse manifests under:

- `research_vault/warehouse/manifests/*.jsonl`

Warehouse directories are auto-created under `research_vault/warehouse`:

- `runs`, `reviews`, `manuscripts`, `datasets`, `manifests`, `exports`

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


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.
