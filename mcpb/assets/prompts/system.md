# sakana-mcp — MCP Server Capabilities

**Server:** sakana-mcp v0.1.0
**Description:** FastMCP wrapper around Sakana AI Scientist v2 for autonomous scientific research loops. Supports hypothesis ideation, containerized experiment execution, tree-search health monitoring, VLM-based manuscript review, research task discovery, and workflow planning across six MCP tools with a complementary REST API surface.

---

## Architecture Overview

sakana-mcp is an orchestration layer between an MCP client (Claude Desktop, Cursor, etc.) and the Sakana AI Scientist v2 open-source codebase. The server manages a local research vault directory that stores all generated artifacts: hypotheses, experiment configurations, execution logs, review results, and a JSONL warehouse manifest for audit traceability.

### Vault Directory Structure

The research vault defaults to `./research_vault/` relative to the server's working directory and is configurable via `RESEARCH_VAULT_PATH`. The full layout is:

```
research_vault/
  default_workshop.md            # Auto-generated workshop description
  default_workshop.json          # AI Scientist ideation output (hypotheses)
  ideation_last.json             # Most recent ideation result snapshot
  execute_last_request.json      # Payload of the last research_execute call
  execute_last_stdout.log        # Full stdout from Docker container
  execute_last_stderr.log        # Full stderr from Docker container
  runs/
    bfts_config.runtime.yaml     # Generated BTFS configuration with runtime overrides
    workspace/                   # Container workspace directory
    logs/                        # Stage progress logs from tree search
      stage_1/notes/stage_progress.json
      stage_2/notes/stage_progress.json
    data/                        # Experiment data output
  warehouse/
    manifests/                   # Per-date JSONL event log (YYYY-MM-DD.jsonl)
    runs/                        # Reserved for run archives
    reviews/                     # Reserved for review output storage
    manuscripts/                 # Reserved for manuscript storage
    datasets/                    # Reserved for dataset storage
    exports/                     # Reserved for export artifacts
```

The vault is created automatically on first use of any tool. Subdirectories are created lazily as needed.

### AI Scientist v2 Vendor Integration

The AI Scientist v2 vendor directory defaults to `./vendor/ai-scientist-v2/` and is expected to contain a clone of the SakanaAI/AI-Scientist-v2 repository. When present and importable, the server uses these specific modules:

- `ai_scientist.perform_ideation_temp_free.generate_temp_free_idea()` — generates hypotheses from a workshop description using an LLM client. Takes the workshop text, model client, and generation parameters, returns a structured list of idea dicts.
- `ai_scientist.perform_vlm_review.perform_imgs_cap_ref_review()` — runs VLM-based figure-caption-reference consistency review on a PDF. Extracts figures, sends them with captions and text references to the VLM, returns structured findings.
- `ai_scientist.llm.create_client()` — factory function for creating an LLM client from a model string. Supports models from OpenAI, Google, Anthropic, Ollama, and others.
- `ai_scientist.vlm.create_client()` — factory function for creating a VLM client supporting multimodal inputs.

When the vendor is absent, `research_ideate` falls back gracefully to 5 built-in hardcoded hypotheses. `research_review` will fail with a clear error pointing to the missing vendor.

### BTFS Runtime Configuration

The `research_execute` tool generates a Breadth-First Tree Search (BTFS) configuration file by reading the base `bfts_config.yaml` from the vendor directory and overlaying runtime-specific values:

- `desc_file`: Path to the ideas JSON file, mounted inside the container at `/workspace/research_vault/`.
- `workspace_dir`, `log_dir`, `data_dir`: Subdirectories under `runs/` in the vault.
- `agent.num_workers`: Parallel tree-search branches.
- `agent.search.max_debug_depth`: Debug retry attempts for buggy branches.

The generated `runs/bfts_config.runtime.yaml` is the sole runtime configuration. The full experiment is launched via `docker compose run scientist-executor` with a Python command that imports and calls `perform_experiments_bfts()`.

### Warehouse Manifest System

Every operation that produces artifacts writes a JSONL entry to the warehouse manifest, keyed by UTC date. This enables full audit traceability of all research activities:

```jsonl
{"ts_utc": "20260619T103000Z", "event_type": "ideation", "payload": {"mode": "ai_scientist_v2", "count": 5, "codebase_hint": "attention sparsity"}}
{"ts_utc": "20260619T104500Z", "event_type": "execution", "payload": {"ok": true, "return_code": 0, "num_workers": 4, "max_debug_depth": 3}}
{"ts_utc": "20260619T110000Z", "event_type": "review", "payload": {"pdf_path": "paper.pdf", "figures_reviewed": 12, "model": "gpt-4o-2024-11-20"}}
```

### REST API Surface

Three custom endpoints are available alongside the MCP tools:

1. **GET /health** — Returns `{"status": "healthy", "server": "sakana-mcp"}`. No authentication required.
2. **GET /api/llm/providers** — Discovers Ollama model at localhost:11434 with a 5-second timeout. Returns `{"providers": [{"name": "ollama", "models": [...]}]}` or an empty list if Ollama is unreachable.
3. **POST /api/llm/chat** — Proxies a prompt to Ollama's `/api/generate` endpoint. Accepts JSON body `{"model": "...", "prompt": "..."}`, returns `{"response": "..."}`. 120-second timeout. Returns HTTP 500 with error details on failure.

---

## Tool Reference

### 1. research_ideate

**Purpose:** Generate 5 research hypotheses using Progressive Agentic Tree Search. Invokes the AI Scientist v2 ideation module when vendored, or falls back to 5 built-in hardcoded hypotheses. The result is saved to `research_vault/ideation_last.json` and appended to the warehouse manifest.

**How it works:**
1. Creates or validates the workshop description file. If `workshop_file` is omitted, a default workshop is written using `codebase_hint` (or a generic fallback).
2. If the AI Scientist vendor is found at `AI_SCIENTIST_V2_PATH`, it imports `create_client` and `generate_temp_free_idea`, creates a client for the specified `model`, and calls the ideation loop with `max_num_generations` generation passes and `num_reflections` reflection rounds per idea.
3. Extracts the top 5 hypotheses with fields: `id` (H1-H5), `title`, `hypothesis`.
4. If the vendor is absent or import fails, returns 5 built-in fallback hypotheses with `ideation_error` set.
5. Saves the result to the vault and writes a manifest entry.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `codebase_hint` | `str \| None` | No | `None` | Optional hint about the research focus area. Used as TL;DR and Abstract in the auto-generated workshop file. |
| `workshop_file` | `str \| None` | No | `None` | Path to a Markdown workshop description file. Must contain sections: `# Title`, `# Keywords`, `# TL;DR`, `# Abstract`. |
| `model` | `str` | No | `"gemini-2.5-flash"` | Model identifier for the AI Scientist LLM client. Supports OpenAI, Google, Anthropic, Ollama models. |
| `max_num_generations` | `int` | No | `5` | Number of idea candidates to generate (1-20). |
| `num_reflections` | `int` | No | `3` | Reflection rounds per idea (1-10). Higher values refine hypotheses but increase token cost. |

**Return Format:**
```json
{
  "success": true,
  "result": {
    "hypotheses": [
      {"id": "H1", "title": "Sparse attention improves noise robustness", "hypothesis": "Models with sparse attention patterns will show higher accuracy under Gaussian input noise compared to dense attention baselines."},
      {"id": "H2", "title": "Layer-specific dropout for adversarial robustness", "hypothesis": "Applying higher dropout rates in early layers will improve robustness to adversarial perturbations without sacrificing clean accuracy."}
    ],
    "count": 5,
    "codebase_hint": "Study attention sparsity and model robustness",
    "mode": "ai_scientist_v2"
  },
  "research_vault": "/Users/user/project/research_vault",
  "ai_scientist_v2_path": "/Users/user/project/vendor/ai-scientist-v2",
  "warehouse_manifest": "/Users/user/project/research_vault/warehouse/manifests/2026-06-19.jsonl",
  "ideation_error": null,
  "recommendations": [
    "Set AI_SCIENTIST_V2_PATH if vendor path differs from default.",
    "Enable Docker compose sandbox for experiment execution."
  ],
  "related_operations": ["research_execute", "research_status", "research_review"]
}
```

**Mode values:**
- `"ai_scientist_v2"`: The vendor module was successfully imported and used for generation.
- `"fallback"`: Vendor missing or import failed. Hardcoded generic hypotheses returned.

**Error states:**
- Vendor not found: `ideation_error` contains the import exception message.
- Workshop file not found: auto-creates a default workshop.
- Model authentication fails: caught and falls back gracefully.

---

### 2. research_execute

**Purpose:** Launch the AI Scientist experiment manager inside a Docker sandbox. Prepares the BTFS runtime configuration, copies ideas into the vault, and launches `docker compose run scientist-executor` with a Python command that calls `perform_experiments_bfts()`.

**How it works:**
1. Validates that `docker-compose.yml` exists in the repo root directory.
2. Validates that the AI Scientist vendor directory is present and importable.
3. Resolves the ideas file path (defaults to `research_vault/default_workshop.json` from ideation).
4. Copies the ideas file into the vault for container filesystem access.
5. Generates the BTFS runtime config by loading `bfts_config.yaml` from vendor, applying `num_workers`, `max_debug_depth`, and path overrides.
6. Runs `docker compose run --rm scientist-executor python -c "import os; from ai_scientist.treesearch.perform_experiments_bfts_with_agentmanager import perform_experiments_bfts; os.chdir('/workspace/vendor/ai-scientist-v2'); perform_experiments_bfts('/workspace/research_vault/runs/{config_name}')"`.
7. Captures stdout and stderr to `execute_last_stdout.log` and `execute_last_stderr.log`.
8. Logs result to warehouse manifest with exit code and configuration details.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ideas_file` | `str \| None` | No | `None` | Path to ideas JSON file. Defaults to `research_vault/default_workshop.json`. |
| `idea_idx` | `int` | No | `0` | Zero-based index of the idea to execute from the ideas file. |
| `num_workers` | `int` | No | `3` | Parallel tree-search branches (1-16). Higher values increase parallelism. |
| `max_debug_depth` | `int` | No | `3` | Max debug retry depth for buggy branches (1-10). |
| `allow_host_execution` | `bool` | No | `false` | Safety valve. Currently informational — execution always uses Docker. |

**Return Format:**
```json
{
  "success": true,
  "return_code": 0,
  "mode": "docker_only",
  "result": {
    "ideas_file": "/Users/user/project/research_vault/default_workshop.json",
    "idea_idx": 0,
    "num_workers": 4,
    "max_debug_depth": 3
  },
  "logs": {
    "stdout": "/Users/user/project/research_vault/execute_last_stdout.log",
    "stderr": "/Users/user/project/research_vault/execute_last_stderr.log"
  },
  "warehouse_manifest": "/Users/user/project/research_vault/warehouse/manifests/2026-06-19.jsonl",
  "message": "Experiment execution completed in Docker."
}
```

**Error states:**
- `docker-compose.yml` missing: returns recovery options to add the file or run from repo root.
- Vendor directory missing: prompts to clone AI Scientist v2.
- Ideas file not found: suggests running `research_ideate` first.
- Docker daemon not running: subprocess returns non-zero exit code.

---

### 3. research_status

**Purpose:** Monitor tree-search experiment health by scanning vault stage progress logs. Aggregates good and buggy node counts across all found stages.

**How it works:**
1. Scans `research_vault/runs/logs/` for files matching `stage_*/notes/stage_progress.json`.
2. For each file, reads `stage`, `total_nodes`, `good_nodes`, `buggy_nodes`, `best_metric`.
3. Computes aggregate totals and the good-to-buggy ratio.

**Parameters:** None.

**Return Format:**
```json
{
  "success": true,
  "status": "running_or_completed",
  "tree_health": {
    "good_nodes": 85,
    "buggy_nodes": 12,
    "ratio_good_to_buggy": 7.08
  },
  "stages": [
    {"stage": "stage_1", "total_nodes": 20, "good_nodes": 18, "buggy_nodes": 2, "best_metric": 0.94, "path": "/vault/runs/logs/stage_1/notes/stage_progress.json"},
    {"stage": "stage_2", "total_nodes": 45, "good_nodes": 40, "buggy_nodes": 5, "best_metric": 0.91, "path": "/vault/runs/logs/stage_2/notes/stage_progress.json"}
  ],
  "research_vault": "/Users/user/project/research_vault"
}
```

**Status values:**
- `"idle"`: No stage progress files found.
- `"running_or_completed"`: At least one stage file found.

---

### 4. research_review

**Purpose:** Run a VLM feedback loop over manuscript figures and captions. Extracts figures from a PDF, analyzes each figure-caption-reference triplet, and returns structured revision directives.

**How it works:**
1. Validates the PDF exists at the given path.
2. Imports `perform_imgs_cap_ref_review` and `vlm.create_client` from the AI Scientist vendor.
3. Creates a VLM client for the specified `model`.
4. Calls the review function, which extracts figures via PDF parsing, sends each figure with caption and text references to the VLM.
5. Saves the review output to `vault/{pdf_stem}.review_img_cap_ref.json`.
6. Logs to warehouse manifest.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `pdf_path` | `str` | Yes | — | Absolute path to the manuscript PDF. |
| `model` | `str` | No | `"gpt-4o-2024-11-20"` | VLM model string. Must support multimodal input. |

**Return Format:**
```json
{
  "success": true,
  "model": "gpt-4o-2024-11-20",
  "pdf_path": "/Users/user/manuscript.pdf",
  "review_path": "/Users/user/research_vault/manuscript.review_img_cap_ref.json",
  "figures_reviewed": 12
}
```

---

### 5. research_library

**Purpose:** List built-in and custom research tasks. Built-in tasks are `ResearchTask` dataclass instances. Custom tasks load from `research_library/tasks/*.json`.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `domain` | `str \| None` | No | `None` | Case-insensitive domain filter. |

**Return Format:**
```json
{
  "success": true,
  "count": 4,
  "tasks": [
    {"task_id": "ml_ablation_robustness", "title": "Ablation-driven robustness analysis", "domain": "machine-learning", "difficulty": "intermediate", "summary": "Identify which model components most influence robustness.", "success_criteria": ["At least 3 ablation variants", "One robustness metric", "Clear hypothesis-to-result mapping"], "starter_prompt": "Study robustness under distribution shift..."}
  ],
  "domains": ["agent-systems", "machine-learning", "scientific-writing"]
}
```

**Built-in tasks:**
- `ml_ablation_robustness` — Ablation robustness (intermediate, ML)
- `data_curriculum_generalization` — Curriculum generalization (advanced, ML)
- `llm_debug_loop_efficiency` — Debug profiling (intermediate, agent-systems)
- `vision_caption_consistency` — Figure-caption audit (beginner, scientific-writing)

---

### 6. research_workflow_plan

**Purpose:** Generate a multi-step agentic workflow plan for a given task.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `task_id` | `str` | Yes | — | Task identifier (case-sensitive). |
| `num_workers` | `int` | No | `3` | Workers for the execution step. |

**Return Format:**
```json
{
  "success": true,
  "task": {"task_id": "ml_ablation_robustness", "title": "Ablation-driven robustness analysis"},
  "workflow_plan": [
    {"step": 1, "tool": "research_ideate", "args": {"codebase_hint": "...", "max_num_generations": 5}, "goal": "Generate candidate hypotheses."},
    {"step": 2, "tool": "research_execute", "args": {"num_workers": 3, "max_debug_depth": 3}, "goal": "Run experiment in Docker."},
    {"step": 3, "tool": "research_status", "args": {}, "goal": "Monitor tree health."},
    {"step": 4, "tool": "research_review", "args": {"pdf_path": "<path-to-paper.pdf>"}, "goal": "VLM review."}
  ]
}
```

---

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `RESEARCH_VAULT_PATH` | `./research_vault` | No | Research artifact storage directory |
| `AI_SCIENTIST_V2_PATH` | `./vendor/ai-scientist-v2` | No | AI Scientist vendor path |
| `GEMINI_API_KEY` | — | For Gemini | Gemini API key for ideation/review |
| `S2_API_KEY` | — | No | Semantic Scholar API key (reserved) |

## Integration Points

- **Ollama:** Auto-discovered at localhost:11434. Provides local LLM models for chat and optional ideation.
- **AI Scientist v2:** Core dependency for ideation, review, LLM/VLM client factories.
- **Docker:** Required for experiment execution via `docker compose`.
- **Semantic Scholar API:** Accepted but not consumed (reserved).

## Complete Parameter and Return Type Reference

Every tool in sakana-mcp follows a consistent structured return pattern. The `success` field is always a boolean. On failure, the response includes `error` (string) and `recovery_options` (list of strings) for agent-visible recovery guidance. On success, domain-specific fields are populated.

### research_ideate Detailed Parameter Breakdown

The `codebase_hint` parameter accepts any natural language string describing a research focus area. It populates the TL;DR and Abstract sections of the auto-generated workshop file when no workshop_file is provided. The `workshop_file` parameter, when provided, must be a valid path to an existing Markdown file on disk. The file should contain four sections: a `# Title` line, a `# Keywords` line with comma-separated values, a `# TL;DR` line with a one-sentence summary, and a `# Abstract` section with one or more paragraphs describing the research direction. The `model` parameter is passed verbatim to the AI Scientist `create_client` function. Supported model strings include `"gpt-4o"`, `"gpt-4o-mini"`, `"gpt-4-turbo"`, `"gemini-2.5-flash"`, `"gemini-2.5-pro"`, `"claude-sonnet-4-20250514"`, `"claude-opus-4-20250514"`, and `"gemma3:1b"` (for local Ollama). The `max_num_generations` parameter controls how many idea candidates are generated in the first pass. Higher values produce more diverse candidates but consume proportionally more tokens. The `num_reflections` parameter controls iterative refinement: each reflection round sends the current hypothesis back to the LLM for self-critique and improvement. More rounds yield more polished hypotheses but increase API costs linearly.

### research_execute Detailed Parameter Breakdown

The `ideas_file` parameter defaults to `research_vault/default_workshop.json` which is the standard output path of `research_ideate`. If the file does not exist, the tool returns a helpful error asking the caller to run ideation first. The `idea_idx` parameter is a zero-based index into the `ideas` array within the JSON file. The first idea (index 0) corresponds to hypothesis H1 from the ideation output. The `num_workers` parameter sets the breadth of the tree search. Each worker explores a separate branch of the hypothesis space in parallel. More workers increase resource consumption (CPU, memory) but can find solutions faster. Values above 8 require significant computational resources. The `max_debug_depth` parameter controls how many times the experiment manager retries a buggy branch before marking it as failed. Each retry attempts to automatically fix the issue (e.g., by modifying code or adjusting parameters). Higher depths increase the chance of recovering from transient failures but consume more experiment time. The `allow_host_execution` parameter is a design-level safety control. Currently, all execution happens inside Docker regardless of this flag, but future versions may respect it to enable host-side experimentation for debugging purposes. The error response for missing `docker-compose.yml` includes a recovery_options array with specific actions: adding the Compose file, running from the repo root, or creating the file manually with the correct service definition.

### research_status Return Fields

The `status` field takes one of two values: `"idle"` when no stage progress files are found in the vault, or `"running_or_completed"` when at least one stage file is present. The tool cannot distinguish between a running experiment and a completed one because it uses only the presence of stage files as its signal. The `tree_health` object contains three fields: `good_nodes` (integer count of experiment branches that completed without errors), `buggy_nodes` (integer count of branches that encountered failures), and `ratio_good_to_buggy` (float or null). The ratio is null when there are zero buggy nodes, which prevents division-by-zero errors. The `stages` array contains one entry per found stage progress file. Each entry includes `stage` (string, e.g. `"stage_1"`), `total_nodes` (integer), `good_nodes` (integer), `buggy_nodes` (integer), `best_metric` (float or null representing the best performance metric found in that stage), and `path` (string, full filesystem path to the JSON file for manual inspection).

### research_review Return Fields

The `model` field reports the actual model string used, which may differ from the input if the AI Scientist client resolves aliases. The `pdf_path` is the resolved absolute path to the manuscript PDF. The `review_path` is the path where the review JSON was saved in the vault. The `figures_reviewed` field is an integer count of how many figures were successfully extracted and analyzed from the PDF. A value of 0 may indicate the PDF has no embedded figures, uses a non-standard encoding, or is a scanned document rather than a digitally-born PDF. The saved review JSON contains per-figure entries with findings about caption accuracy, text reference alignment, and suggested revisions.

### research_library Return Fields

The `count` field reports the total number of tasks matching the optional domain filter. When no filter is applied, this includes both built-in and custom tasks. The `tasks` array contains task objects with fields: `task_id` (unique string identifier), `title` (human-readable name), `domain` (categorization string such as `"machine-learning"`, `"agent-systems"`, or `"scientific-writing"`), `difficulty` (one of `"beginner"`, `"intermediate"`, `"advanced"`), `summary` (one-sentence description), `success_criteria` (array of strings defining measurable completion conditions), and `starter_prompt` (a detailed prompt suitable for passing to `research_ideate` as a codebase hint). The `domains` field lists all unique domain values present in the current task set, including domains from custom tasks.

### research_workflow_plan Return Fields

The `task` object is the full task definition matching the requested `task_id`. The `workflow_plan` array contains step objects. Each step has: `step` (integer, 1-based sequence number), `tool` (string, the MCP tool name to call), `args` (object, the parameters to pass to the tool, with placeholder values where paths are unknown), and `goal` (string, explaining what this step achieves in natural language). The plan always follows the same four-phase structure: ideation first (to generate hypotheses), execution second (to test them in Docker), status monitoring third (to assess results), and review fourth (to evaluate the manuscript).

## REST API Detailed Reference

The `/health` endpoint is a lightweight GET endpoint that returns a JSON object with two fields: `status` (always `"healthy"`) and `server` (always `"sakana-mcp"`). It has no parameters, no authentication, and a negligible response time. The `/api/llm/providers` endpoint probes `http://localhost:11434/api/tags` with a 5-second timeout. On success, it returns available Ollama models as a JSON array under `providers[0].models`. On failure (connection refused, timeout, or non-JSON response), it returns an empty `providers` array. The `/api/llm/chat` endpoint accepts a POST with JSON body `{"model": "...", "prompt": "..."}`. The default model is `"gemma3:1b"`. The response is `{"response": "..."}` containing the generated text. On failure, returns HTTP 500 with `{"error": "..."}` containing the exception message. The timeout is 120 seconds, suitable for long generations.

## Security and Privacy - Extended Considerations

### Credential Handling

API keys for Gemini, OpenAI, and other LLM providers are read exclusively from environment variables. They are never written to disk in the research vault, never included in return values, and never logged. The `main()` function reads `GEMINI_API_KEY` at startup but does not validate it — validation happens lazily when the AI Scientist client is first used. If the key is missing or invalid, the client will throw an authentication error which is caught by the tool and returned gracefully. The `S2_API_KEY` for Semantic Scholar is currently unused but reserved for future paper search features.

### Filesystem Isolation

The research vault is the only directory the server writes to. All hypotheses, logs, configurations, review artifacts, and warehouse manifests are contained within this tree. The vault is configurable via `RESEARCH_VAULT_PATH` and defaults to a subdirectory of the current working directory. When running inside Docker, only the vault and the AI Scientist vendor directory are mounted into the container. The container has no access to other host directories.

### Network Security

The server makes outbound HTTPS connections to configured LLM API endpoints (OpenAI, Google AI, Anthropic) based on the model string provided to tools. It also connects to localhost:11434 for Ollama requests. No other network connections are made. The REST API endpoints (`/health`, `/api/llm/*`) are unauthenticated — they are intended for local development use only. Production deployments should put the server behind a reverse proxy with authentication.

## Integration Points - Extended

### Docker Compose Requirements

The `research_execute` tool requires a `docker-compose.yml` file in the repo root directory. This file must define a `scientist-executor` service that:
- Builds from or uses an image containing the AI Scientist v2 codebase
- Mounts the research vault at `/workspace/research_vault`
- Mounts the AI Scientist vendor at `/workspace/vendor/ai-scientist-v2`
- Uses the `python` command to execute the experiment manager
- Sets working directory to `/workspace/vendor/ai-scientist-v2`

### Ollama Requirements

The local LLM chat endpoint (`/api/llm/chat`) requires Ollama to be running on localhost:11434. Models must be pulled before use. The Ollama connection is optional — if unreachable, the endpoint returns empty provider lists or HTTP 500 errors. The research ideation tool does not require Ollama; it uses the configured model string which may point to any supported provider.

### Semantic Scholar Integration

The Semantic Scholar API base URL and key are read from `S2_API_KEY` environment variable. This integration is reserved for future paper search and retrieval features. Currently, the key is accepted but not consumed by any tool. When implemented, it will enable paper citation graph traversal, full-text search across the academic literature, and automated related-work section generation.

## Warehouse Manifest Format

Each manifest file is a JSONL (JSON Lines) file named by UTC date, e.g. `2026-06-19.jsonl`. Each line is a JSON object with three fields:
- `ts_utc`: ISO-8601 timestamp in compact format, e.g. `"20260619T103000Z"`
- `event_type`: One of `"ideation"`, `"execution"`, `"review"`
- `payload`: A JSON object with event-specific fields (hypothesis count, return code, figure count, etc.)

Manifest files are append-only. They are never rotated or pruned. Over time, the manifest directory will grow linearly with research activity.

## Dual Transport Support

The server supports both stdio and HTTP/SSE transport. In stdio mode (default), the server reads and writes JSON-RPC messages on stdin/stdout. This is the standard MCP transport used by Claude Desktop, Cursor, and other MCP clients. In HTTP mode (`MCP_TRANSPORT=http`), the server binds to `http://localhost:8000` and provides SSE (Server-Sent Events) transport. The SSE endpoint is at `GET /sse` and the message posting endpoint is at `POST /messages?session_id=<id>`. The custom REST endpoints (`/health`, `/api/llm/*`) are available in both modes.

## Fallback Behavior

When the AI Scientist v2 vendor directory is missing or the Python import fails, `research_ideate` enters fallback mode. The fallback hypotheses are generic stubs covering five common ML research themes: ablation studies, adaptive pruning, adversarial debugging, curriculum learning, and structured peer review. These hypotheses are hardcoded in the server source code and do not require any external dependencies. The `mode` field in the response is set to `"fallback"` and the `ideation_error` field contains the original exception message for debugging.

## Error Recovery Guidance

Every tool returns structured error information to guide automated recovery. Error responses include:
- `success: false` — clear signal that the operation did not complete
- `error` — human-readable error message describing what went wrong
- `recovery_options` — array of specific, actionable steps the caller can take to resolve the issue

This pattern enables autonomous agents to self-correct without human intervention. For example, if `research_execute` cannot find the ideas file, the recovery options direct the agent to run `research_ideate` first. If the vendor directory is missing, the options suggest cloning the repository or setting the correct path.

## Performance Considerations

Ideation performance depends primarily on the LLM provider and model choice. Gemini 2.5 Flash typically generates 5 hypotheses with 3 reflections in 30-60 seconds. GPT-4o is comparable. Local models via Ollama are significantly slower (2-5 minutes). Execution performance depends on Docker resource allocation, the complexity of the experiment code, and the number of worker branches. Each worker adds approximately linear time to the total execution. Debug depth adds time only when branches encounter errors that trigger retries.

## Version Compatibility

The server is designed for AI Scientist v2 (the `SakanaAI/AI-Scientist-v2` repository). Older v1 versions are not supported. The expected import paths are `ai_scientist.perform_ideation_temp_free` and `ai_scientist.perform_vlm_review`. If the vendor repository changes its module structure, imports will fail and the server will fall back gracefully.

## Security & Privacy

- **Docker-only execution:** The `research_execute` tool always uses `docker compose run`. Host execution is never performed.
- **No credential logging:** API keys are read from environment variables only and never appear in logs, vault artifacts, or return values.
- **Local-first:** All artifacts stay on the local filesystem vault. No data is sent to external services except configured LLM APIs and local Ollama.
- **Container isolation:** The Docker container mounts only the vault and vendor directories. It has no access to the host filesystem or network beyond those mounts.
- **Auto-cleanup:** `--rm` flag ensures containers are removed after execution.
