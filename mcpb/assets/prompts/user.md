# sakana-mcp — User Guide

Server: sakana-mcp v0.1.0
Description: Autonomous scientific research assistant powered by Sakana AI Scientist v2.
Transport: stdio (default) or HTTP (set MCP_TRANSPORT=http).

---

## Installation

### Prerequisites

Python 3.11+ with uv package manager. Git for cloning the AI Scientist v2 vendor. Docker Desktop for research_execute. Ollama (optional) for local LLM chat. GEMINI_API_KEY from Google AI Studio.

### Setup Steps

git clone https://github.com/sandraschi/sakana-mcp.git
cd sakana-mcp
uv venv
uv sync

For full AI Scientist integration: mkdir -p vendor && git clone https://github.com/SakanaAI/AI-Scientist-v2.git vendor/ai-scientist-v2 && cd vendor/ai-scientist-v2 && pip install -e . && cd ../..

Set environment: set GEMINI_API_KEY=your_key and set S2_API_KEY=your_key. Start with: uv run python -m sakana_mcp

### Claude Desktop Configuration

In claude_desktop_config.json, set the MCP server with command "uv", args ["run", "--directory", "C:/path/to/sakana-mcp", "python", "-m", "sakana_mcp"], and env with GEMINI_API_KEY, S2_API_KEY, and AI_SCIENTIST_V2_PATH.

---

## Step-by-Step Tutorials

### Tutorial 1: Generate Research Hypotheses (Ideation)

Goal: Generate 5 machine learning research hypotheses using research_ideate.

Background: Ideation is the first step in the autonomous research loop. Describe a research focus and the AI Scientist generates concrete, testable hypotheses.

Tool Call:
research_ideate(codebase_hint="Investigate how attention sparsity affects model robustness to input noise.", model="gemini-2.5-flash", max_num_generations=5, num_reflections=3)

Return Value:
{
  "success": true,
  "result": {
    "hypotheses": [
      {"id": "H1", "title": "Sparse attention improves noise robustness", "hypothesis": "Models with sparse attention patterns will show higher accuracy under Gaussian input noise compared to dense attention baselines."},
      {"id": "H2", "title": "Layer-specific dropout for adversarial robustness", "hypothesis": "Applying higher dropout rates in early layers improves robustness to adversarial perturbations."}
    ],
    "count": 5,
    "mode": "ai_scientist_v2"
  }
}

What happened: The AI Scientist v2 ideation module generated 5 hypotheses about attention mechanisms and robustness. Results saved to research_vault/ideation_last.json.

### Tutorial 2: Ideation with Fallback Mode

Goal: Generate hypotheses when AI Scientist v2 is not installed.

Tool Call: research_ideate(codebase_hint="Optimize transformer inference speed")

Return: success true with 5 generic hypotheses, mode "fallback", ideation_error set to import error.

### Tutorial 3: Execute Hypotheses in Docker

Goal: Run the experiment on hypothesis H1. Requires Docker Desktop running.

Tool Call: research_execute(idea_idx=0, num_workers=4, max_debug_depth=3)

Return:
{
  "success": true, "return_code": 0, "mode": "docker_only",
  "logs": {"stdout": ".../execute_last_stdout.log", "stderr": ".../execute_last_stderr.log"},
  "message": "Experiment execution completed in Docker."
}

What happened: BTFS config generated, docker compose run executed, stdout and stderr captured.

### Tutorial 4: Monitor Experiment Health

Goal: Check tree-search experiment health after running.

Tool Call: research_status()

Return:
{
  "success": true, "status": "running_or_completed",
  "tree_health": {"good_nodes": 85, "buggy_nodes": 12, "ratio_good_to_buggy": 7.08},
  "stages": [
    {"stage": "stage_1", "total_nodes": 20, "good_nodes": 18, "buggy_nodes": 2, "best_metric": 0.94},
    {"stage": "stage_2", "total_nodes": 45, "good_nodes": 40, "buggy_nodes": 5, "best_metric": 0.91}
  ]
}

### Tutorial 5: VLM Manuscript Review

Goal: Review a research paper PDF for figure-caption consistency.

Tool Call: research_review(pdf_path="C:/manuscripts/paper.pdf", model="gpt-4o-2024-11-20")

Return: success true, model "gpt-4o-2024-11-20", 8 figures reviewed, review saved to vault.

### Tutorial 6: Browse Research Tasks

Tool Call: research_library() returns 4 tasks across 3 domains.
Filter with: research_library(domain="machine-learning")

### Tutorial 7: Generate Workflow Plan

Tool Call: research_workflow_plan(task_id="llm_debug_loop_efficiency")
Returns 4-step plan: ideate, execute, status, review.

### Tutorial 8: End-to-End Research Lifecycle

Step 1: research_ideate(codebase_hint="Curriculum learning for low-data regimes") generates 5 hypotheses.
Step 2: research_execute(idea_idx=0, num_workers=4) launches Docker experiment.
Step 3: research_status() monitors progress with good/buggy ratio.
Step 4: research_review(pdf_path="C:/vault/runs/manuscript.pdf") runs VLM review.
Step 5: research_workflow_plan(task_id="data_curriculum_generalization") plans next cycle.

### Tutorial 9: Custom Task Integration

Create research_library/tasks/my_rl_task.json with standard schema, then call research_library() to see 5 tasks.

### Tutorial 10: HTTP Transport Mode

Start with set MCP_TRANSPORT=http. Test: curl http://localhost:8000/health, curl http://localhost:8000/api/llm/providers.

### Tutorial 11: Docker Execution Failure Recovery

When docker-compose.yml is missing, research_execute returns success false with recovery_options pointing to the solution.

### Tutorial 12: Custom Workshop Ideation

Create my_workshop.md with Title, Keywords, TL;DR, Abstract. Call research_ideate(workshop_file="my_workshop.md") for domain-specific hypotheses.

---

## REST API Reference

GET /health returns {"status": "healthy", "server": "sakana-mcp"}.
GET /api/llm/providers discovers Ollama models on localhost:11434.
POST /api/llm/chat proxies to Ollama, accepts {"model": "...", "prompt": "..."}, returns {"response": "..."}.

---

## Troubleshooting Guide: Common Problems and Solutions

Problem 1: AI Scientist vendor not found after cloning. Solution: Run pip install -e . in the vendor directory. Verify AI_SCIENTIST_V2_PATH is correct.

Problem 2: Docker container exits immediately. Solution: Check execute_last_stderr.log. Common causes: missing API keys, missing Python deps, paths wrong in BTFS config.

Problem 3: Ideation results off-topic. Solution: Provide more specific codebase_hint with concrete technical terms.

Problem 4: research_status always idle. Solution: Verify RESEARCH_VAULT_PATH. Check runs/logs/ exists inside vault.

Problem 5: Custom tasks not loading. Solution: Verify JSON files in research_library/tasks/. Check format matches schema exactly.

Problem 6: Workflow plan empty. Solution: Ensure task_id is valid from research_library() output.

Problem 7: Review finds 0 figures. Solution: PDF may be scanned without embedded figures.

Problem 8: Docker OOM. Solution: Increase memory limits in docker-compose.yml. Reduce num_workers.

Problem 9: Vault disk usage high. Solution: Delete old stage logs and completed run artifacts.

Problem 10: API key errors. Solution: Verify key is set and has access to requested model.

Problem 11: Workshop parsing fails. Solution: Ensure all required markdown sections are present.

Problem 12: Concurrent executions conflict. Solution: Use separate vault paths for parallel research sessions.

Problem 13: HTTP transport refuses connection. Solution: Verify MCP_TRANSPORT=http is set. Check port 8000 availability.

Problem 14: Custom task leads to poor hypotheses. Solution: Make starter_prompt more specific with concrete technical details.

Problem 15: Warehouse manifest files grow large. Solution: Implement log rotation for old manifest dates.

---

## Detailed Workflow Reference

### Complete Research Session Walkthrough

This 7-step walkthrough demonstrates a complete research session from start to finish. The scenario investigates how sparse attention affects model robustness.

Session Start: The agent calls research_library() to discover 4 built-in tasks and selects ml_ablation_robustness.

Step 1 Ideation: research_ideate(codebase_hint="Investigate how attention sparsity affects model robustness.") The AI Scientist generates 5 hypotheses.

Step 2 Workflow Plan: research_workflow_plan(task_id="ml_ablation_robustness", num_workers=4) returns 4 steps.

Step 3 Execution: research_execute(idea_idx=0, num_workers=4, max_debug_depth=3) launches Docker with 4 workers.

Step 4 Monitoring: research_status() shows 3 stages, 120 nodes, 108 good, 12 buggy, ratio 9:1.

Step 5 Manuscript: The AI Scientist generates a LaTeX PDF in the vault.

Step 6 Review: research_review(pdf_path=".../manuscript.pdf") reviews 12 figures, finds 3 mismatches.

Step 7 Next Cycle: research_workflow_plan(task_id="data_curriculum_generalization") for the next research focus.

### Multi-Worker Configuration

For complex hypotheses, use research_execute(idea_idx=2, num_workers=8, max_debug_depth=5). This launches 8 parallel branches with 5 automatic bug-fix retries each.

### Custom Workshop Specification

Create a workshop markdown with sections: Title, Keywords, TL;DR, Abstract. Provide specific technical details. Call research_ideate(workshop_file="my_workshop.md", model="gpt-4o", max_num_generations=7, num_reflections=5).

---

## Environment Variable Configuration Guide

RESEARCH_VAULT_PATH defaults to ./research_vault/. Controls all artifact storage. Use absolute paths for reliability.

AI_SCIENTIST_V2_PATH defaults to ./vendor/ai-scientist-v2/. Must contain importable ai_scientist/ package.

GEMINI_API_KEY required for Gemini models. Validate by running test ideation.

S2_API_KEY reserved for future Semantic Scholar integration. Not currently consumed.

---

## Performance Optimization Guide

Ideation Speed: Gemini 2.5 Flash generates 5 hypotheses in 30-60s. GPT-4o in 45-90s. Local Ollama in 2-5 minutes. Reduce num_reflections for speed.

Execution Performance: Match num_workers to CPU cores. Rule of thumb: num_workers = core_count - 2. Each worker uses ~1GB RAM.

Disk Management: Experiment logs can reach hundreds of MB. Monitor vault size. Delete old stage logs. Rotate manifest files.

Network Usage: Each ideation with 5 generations sends 50-100KB request, receives 20-50KB response. For 100 sessions/month, expect 10-50MB data transfer.

---

## FAQ

1. Do I need Docker? Only for research_execute. All other tools work standalone.
2. What models are supported? Any model supported by AI Scientist client: GPT-4o, Gemini, Claude, Ollama.
3. Where are experiments stored? In the research vault directory (default ./research_vault/).
4. Can I run without Docker? No, execution always uses docker compose run.
5. How to add custom tasks? Create JSON files in research_library/tasks/ following the standard schema.
6. What does warehouse manifest track? Every ideation, execution, and review operation.
7. Does it support HTTP? Yes, set MCP_TRANSPORT=http.
8. What API keys are needed? GEMINI_API_KEY for ideation. S2_API_KEY reserved.
9. How many hypotheses per ideation? Up to 20, controlled by max_num_generations.
10. Good vs buggy nodes? Good completed without errors. Buggy encountered failures during execution.

---

## Docker Compose Template

Create docker-compose.yml in repo root:
```yaml
version: "3.8"
services:
  scientist-executor:
    build:
      context: ./vendor/ai-scientist-v2
      dockerfile: Dockerfile
    volumes:
      - ./research_vault:/workspace/research_vault
      - ./vendor/ai-scientist-v2:/workspace/vendor/ai-scientist-v2
    working_dir: /workspace/vendor/ai-scientist-v2
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    deploy:
      resources:
        limits:
          memory: 8G
```

---

## Custom Task JSON Schema

```json
{
  "task_id": "unique_lowercase_id",
  "title": "Human-Readable Title",
  "domain": "domain-category",
  "difficulty": "beginner|intermediate|advanced",
  "summary": "One or two sentences describing the task.",
  "success_criteria": ["Specific outcome 1", "Specific outcome 2"],
  "starter_prompt": "Detailed prompt for ideation step."
}
```

## Common Tool Call Patterns

Pattern 1 Basic Discovery: research_library() then research_workflow_plan() then research_ideate(). Works without Docker or vendor.

Pattern 2 Full Research Cycle needs Docker and vendor: research_ideate() then research_execute() then research_status() then research_review().

Pattern 3 Custom Tasks: Create JSON file, call research_library() to verify, call research_workflow_plan(), then execute.

Pattern 4 Multi-Hypothesis: research_ideate(max_num_generations=10) then research_execute(idea_idx=0) then research_execute(idea_idx=1). Compare results.

## CI/CD Pipeline Integration

For automated research pipelines, use HTTP mode. Each step is a separate CI job: research_library, research_ideate, research_execute, research_status, research_review. The research vault persists between jobs for continuous research operations.

## Model Compatibility Reference

OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo, o1-mini, o1-preview
Google: gemini-2.5-flash, gemini-2.5-pro, gemini-1.5-flash
Anthropic: claude-sonnet-4-20250514, claude-opus-4-20250514
Ollama: gemma3:1b, gemma3:12b, llama3.2, qwen2.5, mistral, mixtral

Each model requires the corresponding API key. Ollama requires a running instance on localhost:11434.

## REST API Endpoint Reference

The sakana-mcp server exposes three custom REST endpoints alongside the standard MCP protocol. These endpoints are accessible in both stdio and HTTP transport modes.

GET /health returns a simple health check response with status healthy and server name sakana-mcp. This is useful for Docker health checks, load balancer probes, and monitoring systems. The endpoint has no parameters, no authentication, and responds within milliseconds.

GET /api/llm/providers probes the local Ollama instance at localhost:11434 with a 5-second timeout. On success it returns available models under providers.0.models. On failure it returns an empty providers array. This is used by the web dashboard to discover available local LLM models for chat features.

POST /api/llm/chat accepts a JSON body with model and prompt fields. The default model is gemma3:1b. The server proxies the request to Ollama's /api/generate endpoint with a 120-second timeout. On success it returns the generated response text. On failure it returns HTTP 500 with the error message. This enables browser-based chat with local LLMs without requiring direct API access.

## Extended Troubleshooting For Power Users

Problem: research_execute fails with exit code 137. This is a Docker OOM (out of memory) kill. The container process was terminated by the kernel because it exceeded the available memory. Solution: Increase Docker memory limits in docker-compose.yml under deploy.resources.limits.memory. Alternatively, reduce the num_workers parameter to lower memory consumption.

Problem: research_ideate takes more than 5 minutes. The AI Scientist ideation module is making API calls to the LLM provider. Slow responses are typically due to network latency, model queue times, or rate limiting. Solutions: Switch to a faster model like gemini-2.5-flash instead of gpt-4o. Reduce num_reflections from 3 to 1. Check your API provider's status page for outages.

Problem: The warehouse manifest shows duplicate entries. Each tool call writes one manifest entry. If a tool is called multiple times with the same parameters, each call produces a separate entry. Duplication is expected and by design for audit purposes. Remove duplicates by filtering on ts_utc in downstream analysis.

Problem: research_library shows different tasks in different environments. Custom tasks are loaded from the filesystem at research_library/tasks/. If the directory does not exist or contains different JSON files, the available tasks will differ. Verify the task files exist and are valid JSON. Missing files result in empty custom task lists.

Problem: research_workflow_plan returns a task with missing fields. The task was loaded but its structure may be incomplete. Built-in tasks always have all fields. Custom tasks may be missing required fields if the JSON file is incomplete. Verify the JSON file has all required keys: task_id, title, domain, difficulty, summary, success_criteria, starter_prompt.

## Complete Research Lifecycle Reference

The sakana-mcp research lifecycle follows this sequence: discovery, planning, ideation, execution, monitoring, review, and iteration. Each phase produces artifacts that feed into the next phase.

Discovery phase: Call research_library to list available tasks. The result includes task metadata, difficulty ratings, and success criteria. Use the domain filter to narrow down relevant tasks. Select a task that matches your research goals.

Planning phase: Call research_workflow_plan with the selected task_id. The plan provides a structured sequence of tool calls with parameter templates. Customize the parameters as needed for your specific research question.

Ideation phase: Call research_ideate with a codebase_hint or workshop_file. The AI Scientist generates hypotheses using tree search. Review the hypotheses and select the most promising ones for execution. The hypotheses are saved to the vault for reference.

Execution phase: Call research_execute with the selected hypothesis index. The Docker container runs experiments with the configured tree search parameters. Monitor progress with research_status.

Monitoring phase: Call research_status periodically during execution. Track the good-to-buggy ratio to assess experiment health. A ratio above 5 indicates healthy progress. Below 2 requires investigation.

Review phase: After execution produces a manuscript, call research_review with the PDF path. The VLM analyzes each figure for caption and text reference consistency. Review findings are saved as JSON for revision.

Iteration phase: Use the findings to inform the next cycle. Call research_ideate again with refined codebase_hint based on previous results. The vault preserves all artifacts for longitudinal analysis.

## Research Vault Maintenance

The research vault stores all generated artifacts. Over time it accumulates logs, configs, and review outputs. Monitor disk usage regularly. Old stage logs in runs/logs/ can be safely deleted after review. The warehouse manifest files are append-only and can be archived to cold storage. The vault directory structure is designed for easy partial cleanup without affecting other experiments.

## MCP Protocol Integration Notes

sakana-mcp implements the FastMCP protocol which extends the standard MCP protocol with features like Context injection, progress reporting, and custom REST routes. Tools are registered in the order they are defined in the source code. Each tool may have a Context parameter that is automatically injected by the framework. The Context object provides logging, progress tracking, and sampling capabilities. Custom routes are registered using the @mcp.custom_route() decorator and are available in both transport modes.

## Extended Reference: Tool-by-Tool Parameter Guide

research_ideate accepts five parameters with specific constraints. The codebase_hint must be a string under 10000 characters. The workshop_file must be a valid path to an existing markdown file. The model parameter must match a model supported by the AI Scientist client. The max_num_generations parameter accepts integer values from 1 to 20 with a default of 5. The num_reflections parameter accepts integer values from 1 to 10 with a default of 3. Each parameter affects the quality, speed, and cost of the ideation process.

research_execute accepts five parameters with specific constraints. The ideas_file defaults to research_vault/default_workshop.json. The idea_idx is a zero-based index starting at 0. The num_workers parameter accepts values from 1 to 16 with a default of 3. The max_debug_depth parameter accepts values from 1 to 10 with a default of 3. The allow_host_execution boolean defaults to false and is currently informational. The execution runs entirely inside Docker regardless of this flag.

research_status accepts no parameters. It reads stage progress JSON files from the vault's runs/logs/ directory matching the pattern stage_*/notes/stage_progress.json. The tool is read-only and makes no modifications to the vault. It can be called safely at any time, even during an active execution.

research_review accepts two parameters. The pdf_path must be an absolute path to an existing PDF file on the local filesystem. The model parameter defaults to gpt-4o-2024-11-20 and must support multimodal inputs. The review requires the AI Scientist vendor to be installed with VLM client dependencies.

research_library accepts one optional parameter. The domain filter is case-insensitive and matches against the domain field of each task. When omitted, all tasks are returned. The tool is read-only and can be called at any time.

research_workflow_plan accepts two parameters. The task_id must match an existing task exactly including case. Use research_library to discover valid task IDs. The num_workers parameter defaults to 3 and is passed through to the execution step of the generated plan.

## Vault File Reference

The research vault creates these files on first use. The default_workshop.md is created by research_ideate when no workshop_file is provided. The default_workshop.json contains the AI Scientist ideation output with hypotheses array. The ideation_last.json is a snapshot of the most recent ideation result. The execute_last_stdout.log and execute_last_stderr.log capture Docker container output. The warehouse directory contains dated manifest JSONL files for audit purposes. The runs directory contains BTFS configs, workspace directories, and stage progress logs.

## Container Environment Reference

The Docker container used by research_execute has these mounted paths. The research vault is mounted at /workspace/research_vault. The AI Scientist vendor is mounted at /workspace/vendor/ai-scientist-v2. The working directory is /workspace/vendor/ai-scientist-v2. The BTFS runtime config is passed as an argument to perform_experiments_bfts. The container runs with the --rm flag for automatic cleanup after execution. Environment variables for API keys are passed through from the host.

## Web Dashboard Integration

The REST API endpoints at /health, /api/llm/providers, and /api/llm/chat are designed for web dashboard integration. The health endpoint provides a quick liveness check. The providers endpoint enables the dashboard to discover available LLM models. The chat endpoint enables browser-based interaction with local Ollama models without requiring direct API access from the browser.

## Research Scope Configuration

The research vault is the single source of truth for all research artifacts. Its location is configurable via RESEARCH_VAULT_PATH. For multi-repo research, create separate vaults per repository. For collaborative research, point the vault to a shared network drive. The vault can be version-controlled with git or DVC for reproducibility. The warehouse manifest provides an immutable audit trail of all research operations.

## Config Reference: All Environment Variables

RESEARCH_VAULT_PATH controls the directory where all research artifacts including hypotheses, logs, configurations, review outputs, and warehouse manifests are stored. The default value is ./research_vault relative to the working directory. The path is resolved to absolute on first use and all subdirectories are created automatically. AI_SCIENTIST_V2_PATH controls the location of the Sakana AI Scientist v2 vendor repository. The default value is ./vendor/ai-scientist-v2. The path must contain the ai_scientist importable package directory. GEMINI_API_KEY provides authentication for Google Gemini models used during ideation and review. The key is passed to the AI Scientist client at runtime. S2_API_KEY is reserved for future Semantic Scholar integration for paper search and citation features. MCP_TRANSPORT controls the transport mode with stdio as default and http as alternative for HTTP SSE transport.

## Full Glossary of Terms

Research Vault: The directory on disk that stores all generated artifacts including hypotheses, execution logs, configurations, review results, and warehouse manifests. The vault is created automatically on first use and persists across server restarts. Warehouse Manifest: A JSONL file that records every research operation with timestamps and summary payloads for audit trail purposes. Each day produces a separate manifest file named by date. BTFS Configuration: Breadth-First Tree Search configuration file that controls how the experiment manager explores hypothesis space. The config is generated by research_execute and passed to the Docker container. Stage Progress File: A JSON file written by the experiment manager for each tree search stage, reporting node counts and metrics. These files are consumed by research_status to report experiment health. Good Nodes: Experiment branches that completed execution without errors. Buggy Nodes: Experiment branches that encountered errors during execution. The ratio of good to buggy nodes indicates experiment health. Progressive Agentic Tree Search: The AI Scientist method for generating hypotheses by iteratively refining candidate ideas through LLM-based evaluation and critique. VLM Review: Vision Language Model review that analyzes manuscript figures alongside their captions and in-text references to identify inconsistencies.

## Return Value Schema Reference

All sakana-mcp tools return a consistent top-level structure with a success boolean. When success is true, tool-specific fields are populated in the response. When success is false, an error string explains the failure and a recovery_options array provides actionable steps for resolution. The recommendations field provides proactive guidance for improving future operations. The related_operations field lists other tools that can be used in conjunction with the current operation. Tool-specific fields vary by tool but always include enough context for automated processing by LLM agents.

## Docker Resource Requirements

The Docker container used by research_execute requires significant resources for complex experiments. The minimum recommended memory is 4GB with 2 CPU cores. The recommended configuration for productive work is 16GB memory with 8 CPU cores. The container mounts two volumes: the research vault and the AI Scientist vendor directory. The container uses the host's network for API access to LLM providers. Docker must be installed and running on the host machine. The Docker daemon must be accessible from the user account running the sakana-mcp server. Container images can consume several GB of disk space for the base image plus dependencies.

## Output File Reference

Each sakana-mcp tool produces specific output files in the research vault. research_ideate produces ideation_last.json with the full ideation result and default_workshop.json if the default workshop was used. research_execute produces execute_last_request.json, execute_last_stdout.log, execute_last_stderr.log, and runs/bfts_config.runtime.yaml. research_status reads runs/logs/stage_*/notes/stage_progress.json files. research_review produces {pdf_stem}.review_img_cap_ref.json in the vault root. All tools append to the warehouse/manifests/{date}.jsonl manifest file. These files persist across server restarts and enable workflow resumption.

## Sequence Diagrams For Common Workflows

The full research cycle follows this sequence: Start with research_library to list available tasks. Then call research_workflow_plan for a structured plan. Execute research_ideate to generate hypotheses. Pass the top hypothesis index to research_execute for Docker-based experimentation. Monitor progress with research_status calls at intervals. After the experiment produces a manuscript, call research_review for VLM analysis. Use the review findings to inform the next research cycle starting with a refined ideation call. This sequence can be fully automated for continuous research pipelines.

The basic discovery workflow is simpler: Call research_library to see all tasks. Call research_workflow_plan to get a structured plan with tool call templates. Execute the plan steps sequentially. This workflow works without Docker or the AI Scientist vendor and is suitable for exploration and planning.

## Data Flow Architecture

Data flows through sakana-mcp in a directed pipeline. The user provides a research direction via codebase_hint or workshop_file. The AI Scientist module generates structured hypothesis objects. These hypotheses are stored in the research vault and can be inspected as JSON. The experiment manager executes hypotheses inside a Docker container, producing logs and stage progress files. The VLM review module analyzes manuscript PDFs and produces structured JSON reports. All artifacts are persisted in the vault for reuse and audit. The warehouse manifest records the complete history of operations for traceability.

## Advice For Research Teams

For teams using sakana-mcp collaboratively, establish a shared research vault on a network drive accessible to all team members. Each team member should use the same RESEARCH_VAULT_PATH pointing to the shared location. Team members can review each others hypotheses and experiment results by reading the vault files. The warehouse manifest provides an automatic changelog of who did what and when. Use the custom tasks feature to define standardized research templates that encode team best practices and preferred evaluation metrics. The workflow plan generated by research_workflow_plan ensures consistent methodology across team members.

For individual researchers, sakana-mcp serves as an always-available research assistant that never sleeps. Start each research session by calling research_status to check the state of any ongoing experiments from previous sessions. The vault persists across sessions, so you can resume interrupted work without losing context. Use research_library to browse available task templates for inspiration when starting new research directions. The workshop file system enables deep dives into specific topics while the codebase_hint system enables quick exploration of new ideas.

## Production Deployment Checklist

Before deploying sakana-mcp in a production environment, verify these requirements. Ensure Docker Desktop or Docker Engine is installed and running. Configure sufficient memory limits for Docker containers (minimum 4GB, recommended 16GB). Set all required environment variables including GEMINI_API_KEY. Verify the AI Scientist vendor directory exists and is importable. Test the full research cycle with a simple hypothesis before running complex experiments. Configure the research vault path to point to a location with sufficient disk space. Set up monitoring for the research vault disk usage. Implement log rotation for warehouse manifest files. Document the research vault location and contents for team reference. Schedule regular backups of the research vault for disaster recovery.

## Common User Questions And Answers

How do I share research results with my team? Share the research vault directory or specific files from it. The warehouse manifest provides a timeline of operations. Hypothesis files are JSON and easily shareable. Review outputs are structured JSON that can be imported into other tools. The vault directory can be placed under version control for team access.

Can I run sakana-mcp on a server without a GPU? Yes. sakana-mcp does not require a GPU. The AI Scientist ideation and review tools use cloud LLM APIs. The experiment execution runs in Docker and only needs CPU and memory. GPU acceleration is not used.

What happens if the server crashes during an experiment? The Docker container continues running independently. After restarting sakana-mcp, call research_status to check the experiment state. The vault contains the latest stage progress files. If the container was killed, the execution will need to be restarted from scratch.

How do I update the AI Scientist vendor? Pull the latest changes from the vendor repository. Run pip install -e . again if needed. Restart the sakana-mcp server. Test with a simple research_ideate call to verify the new vendor version works correctly.

Can I use sakana-mcp with custom Docker images? Yes. Modify the docker-compose.yml to use a custom image that includes your specific dependencies. The scientist-executor service definition can be customized with additional volumes, environment variables, and resource limits as needed for your research workload.

What monitoring recommendations exist for sakana-mcp? Monitor the research vault disk usage as it grows with each experiment. Monitor Docker disk usage for container images. Monitor API key usage and quotas for the LLM providers. Set up alerts for failed research_execute calls. Track warehouse manifest size for log rotation planning. Monitor server memory usage during large experiments.

## Appendix: All Files Created In Research Vault

The research vault directory at the configured RESEARCH_VAULT_PATH contains these files after a full research cycle. The default_workshop.md file is the auto-generated workshop description from research_ideate when no workshop_file is provided. The default_workshop.json file contains the AI Scientist ideation output with the full hypotheses array. The ideation_last.json file provides a quick reference snapshot of the most recent ideation result. The execute_last_request.json file records the parameters passed to the most recent research_execute call. The execute_last_stdout.log and execute_last_stderr.log files capture all output from the Docker execution container for debugging. The runs/bfts_config.runtime.yaml file contains the generated BTFS configuration used by the experiment manager. The runs/logs/ directory contains stage progress JSON files written by the experiment manager during execution. The runs/workspace/ and runs/data/ directories contain temporary files from the execution. The warehouse/manifests/ directory contains dated JSONL files recording all operations. The {pdf_stem}.review_img_cap_ref.json file in the vault root contains the VLM review output. These files persist across server restarts and provide a complete record of all research activities. The complete research lifecycle is fully documentable and reproducible through these files.
