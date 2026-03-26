## Researcher Guide

This guide is for running autonomous research loops through MCP tools.

## Loop Overview

1. Ideate hypotheses
2. Execute experiments
3. Monitor tree health
4. Review generated manuscript visuals

## Step 1: Ideation

Call `research_ideate` with optional fields:
- `codebase_hint`
- `workshop_file`
- `model`
- `max_num_generations`
- `num_reflections`

Expected output:
- 5 hypotheses
- ideation mode (`ai_scientist_v2` or `fallback`)
- ideation artifact persisted to `research_vault/ideation_last.json`

## Step 2: Execute

Call `research_execute` with:
- `ideas_file` (optional, defaults to vault output)
- `idea_idx`
- `num_workers`
- `max_debug_depth`

Execution model:
- Docker-only by default
- runtime config written to `research_vault/runs/bfts_config.runtime.yaml`
- stdout/stderr persisted in `research_vault`

## Step 3: Status

Call `research_status` to inspect:
- per-stage `good_nodes` and `buggy_nodes`
- global tree health ratio
- current run activity state

## Step 4: Review

Call `research_review` with:
- `pdf_path`
- optional `model`

Output:
- figure/caption/reference review JSON in `research_vault/<paper>.review_img_cap_ref.json`

## Artifact Indexing for RAG

Recommended indexing targets:
- `research_vault/*.json`
- `research_vault/runs/logs/**/notes/*.json`
- `research_vault/*.log`

