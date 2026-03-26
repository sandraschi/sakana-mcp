## Architecture

## Purpose

`sakana-mcp` exposes a controlled MCP interface over AI-Scientist v2 so research automation is orchestrated by tools, not ad hoc shell runs.

## Components

- `src/sakana_mcp/server.py`
  - MCP server entrypoint
  - tool registration (`research_ideate`, `research_execute`, `research_status`, `research_review`)
- `vendor/ai-scientist-v2`
  - upstream Sakana AI-Scientist v2 code
  - provides ideation, tree search, experiment manager, manuscript review modules
- `docker-compose.yml`
  - `sakana-mcp` service (MCP server container)
  - `scientist-executor` service (GPU-enabled execution sandbox)
- `research_vault/` (runtime output)
  - ideas JSON, runtime BFTS config, stage summaries, execution stdout/stderr, review JSON

## Execution Flow

1. `research_ideate`
   - loads workshop context
   - runs AI-Scientist ideation module when importable
   - emits top 5 hypotheses and stores ideation artifact JSON
2. `research_execute`
   - materializes runtime BFTS config
   - maps MCP args into `agent.num_workers` and `agent.search.max_debug_depth`
   - launches experiment manager inside `scientist-executor` container
3. `research_status`
   - scans stage progress notes under `research_vault/runs/logs`
   - reports buggy vs non-buggy node counts
4. `research_review`
   - runs VLM-based figure/caption/reference consistency review
   - writes JSON report to `research_vault`

## Data Boundaries

- Trusted host side:
  - MCP control plane (`server.py`)
  - artifact persistence (`research_vault`)
- Untrusted/high-entropy zone:
  - model-authored experiment execution in containerized sandbox

