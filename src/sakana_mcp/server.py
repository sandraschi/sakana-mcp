from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from fastmcp import FastMCP
from fastmcp.context import Context
import yaml
from sakana_mcp.library import SAMPLE_TASKS, load_custom_tasks, task_to_dict
from sakana_mcp.warehouse import append_manifest, ensure_warehouse


def _env_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _research_vault_path() -> Path:
    # Local-first default; caller can override via env var.
    return Path(os.getenv("RESEARCH_VAULT_PATH", "./research_vault")).resolve()


def _vendor_root() -> Path:
    return Path(os.getenv("AI_SCIENTIST_V2_PATH", "./vendor/ai-scientist-v2")).resolve()


def _extract_hypotheses(ideas: list[dict[str, Any]], limit: int = 5) -> list[dict[str, str]]:
    hypotheses: list[dict[str, str]] = []
    for idx, idea in enumerate(ideas[:limit], start=1):
        hypotheses.append(
            {
                "id": f"H{idx}",
                "title": str(idea.get("Title", idea.get("Name", f"Idea {idx}"))),
                "hypothesis": str(
                    idea.get("Short Hypothesis", idea.get("Abstract", "No hypothesis text provided."))
                ),
            }
        )
    return hypotheses


def _fallback_hypotheses() -> list[dict[str, str]]:
    return [
        {
            "id": "H1",
            "title": "Improve baseline by targeted ablations",
            "hypothesis": "Focused ablations will identify high-leverage components and yield a "
            "measurable improvement on a representative benchmark.",
        },
        {
            "id": "H2",
            "title": "Reduce compute via adaptive pruning",
            "hypothesis": "Adaptive pruning of low-promise branches during tree search will reduce "
            "compute while preserving solution quality.",
        },
        {
            "id": "H3",
            "title": "Increase robustness with adversarial debug loops",
            "hypothesis": "Injecting adversarial debugging prompts will reduce failure modes and "
            "improve reproducibility of experiments.",
        },
        {
            "id": "H4",
            "title": "Better generalization through synthetic curriculum",
            "hypothesis": "A synthetic curriculum staged from easy to hard tasks will improve "
            "generalization versus single-stage training/evaluation.",
        },
        {
            "id": "H5",
            "title": "Higher-quality manuscripts with structured peer review",
            "hypothesis": "A structured peer-review JSON schema feeding back into drafting will "
            "improve clarity and reduce logical gaps in LaTeX manuscripts.",
        },
    ]


def _default_ideas_path(vault: Path) -> Path:
    return vault / "default_workshop.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _prepare_bfts_config(
    *, vendor_root: Path, vault: Path, ideas_json: Path, num_workers: int, max_debug_depth: int
) -> Path:
    base_cfg_path = vendor_root / "bfts_config.yaml"
    with base_cfg_path.open("r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle) or {}

    run_dir = (vault / "runs").resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    work_dir = (run_dir / "workspace").resolve()
    log_dir = (run_dir / "logs").resolve()
    data_dir = (run_dir / "data").resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    cfg["desc_file"] = f"/workspace/research_vault/{ideas_json.name}"
    cfg["workspace_dir"] = "/workspace/research_vault/runs/workspace"
    cfg["log_dir"] = "/workspace/research_vault/runs/logs"
    cfg["data_dir"] = "/workspace/research_vault/runs/data"
    cfg.setdefault("agent", {})
    cfg["agent"]["num_workers"] = int(num_workers)
    cfg["agent"].setdefault("search", {})
    cfg["agent"]["search"]["max_debug_depth"] = int(max_debug_depth)

    run_cfg_path = run_dir / "bfts_config.runtime.yaml"
    with run_cfg_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(cfg, handle, sort_keys=False)
    return run_cfg_path


def _safe_load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _summarize_stage_progress(vault: Path) -> list[dict[str, Any]]:
    notes_files = sorted((vault / "runs" / "logs").glob("stage_*\\notes\\stage_progress.json"))
    summaries: list[dict[str, Any]] = []
    for file_path in notes_files:
        payload = _safe_load_json(file_path)
        if payload is None:
            continue
        summaries.append(
            {
                "stage": payload.get("stage"),
                "total_nodes": payload.get("total_nodes", 0),
                "good_nodes": payload.get("good_nodes", 0),
                "buggy_nodes": payload.get("buggy_nodes", 0),
                "best_metric": payload.get("best_metric"),
                "path": str(file_path),
            }
        )
    return summaries


mcp = FastMCP(
    "sakana-mcp",
    version="0.1.0",
    description="Sakana AI Scientist v2 wrapper for autonomous scientific research loops.",
)


@mcp.tool()
async def research_ideate(
    ctx: Context,
    *,
    codebase_hint: str | None = None,
    workshop_file: str | None = None,
    model: str = "gemini-2.5-flash",
    max_num_generations: int = 5,
    num_reflections: int = 3,
) -> dict[str, Any]:
    """RESEARCH_IDEATE — Generate 5 research hypotheses via Progressive Agentic Tree Search.

    PORTMANTEAU PATTERN RATIONALE:
    This server exposes a small, high-signal tool surface aligned with the Sakana v2 loop.
    Ideation is kept as a dedicated tool because it is frequently invoked and should remain
    stable while internal tree-search implementations evolve.

    Args:
        ctx: FastMCP context for logging and progress reporting.
        codebase_hint: Optional hint about the current repo / focus area.
        workshop_file: Optional markdown file path used by AI Scientist ideation.
        model: Model string passed to AI Scientist ideation client.
        max_num_generations: Number of ideas to generate.
        num_reflections: Number of reflection rounds per idea.

    Returns:
        Dict containing 5 hypotheses and export paths for the research vault.
    """
    vault = _research_vault_path()
    vault.mkdir(parents=True, exist_ok=True)
    vendor = _vendor_root()
    hypotheses: list[dict[str, str]] = []
    ideation_mode = "fallback"
    ideation_error: str | None = None

    ctx.info(
        "research_ideate invoked",
        extra={
            "codebase_hint_present": bool(codebase_hint),
            "research_vault": str(vault),
            "vendor_root": str(vendor),
        },
    )

    await ctx.report_progress(1, 3, "Preparing ideation context")

    # Prefer the real AI Scientist-v2 ideation module when vendored and importable.
    if vendor.exists():
        try:
            if str(vendor) not in sys.path:
                sys.path.insert(0, str(vendor))

            from ai_scientist.llm import create_client  # type: ignore
            from ai_scientist.perform_ideation_temp_free import (  # type: ignore
                generate_temp_free_idea,
            )

            if workshop_file:
                workshop_path = Path(workshop_file).resolve()
            else:
                workshop_path = vault / "default_workshop.md"
                if not workshop_path.exists():
                    workshop_path.write_text(
                        "\n".join(
                            [
                                "# Title",
                                "Autonomous Research in Machine Learning Systems",
                                "",
                                "# Keywords",
                                "agentic tree search, experiment manager, reproducibility, ablation",
                                "",
                                "# TL;DR",
                                codebase_hint or "Generate robust, testable ML research hypotheses.",
                                "",
                                "# Abstract",
                                codebase_hint
                                or "Investigate autonomous scientific pipelines with emphasis on"
                                " reproducibility, controlled experimentation, and efficient search.",
                            ]
                        ),
                        encoding="utf-8",
                    )

            idea_json_path = vault / f"{workshop_path.stem}.json"
            workshop_description = workshop_path.read_text(encoding="utf-8")

            await ctx.report_progress(2, 3, "Running AI Scientist ideation")
            client, client_model = create_client(model)
            ideas = generate_temp_free_idea(
                idea_fname=str(idea_json_path),
                client=client,
                model=client_model,
                workshop_description=workshop_description,
                max_num_generations=max_num_generations,
                num_reflections=num_reflections,
            )
            hypotheses = _extract_hypotheses(ideas, limit=5)
            ideation_mode = "ai_scientist_v2"
        except Exception as exc:
            ideation_error = str(exc)
            hypotheses = _fallback_hypotheses()
            ideation_mode = "fallback"
    else:
        hypotheses = _fallback_hypotheses()
        ideation_mode = "fallback"

    await ctx.report_progress(3, 3, "Finalizing hypotheses")

    ideation_record = {
        "mode": ideation_mode,
        "codebase_hint": codebase_hint,
        "hypotheses": hypotheses,
    }
    if ideation_error:
        ideation_record["error"] = ideation_error

    (vault / "ideation_last.json").write_text(json.dumps(ideation_record, indent=2), encoding="utf-8")
    manifest = append_manifest(
        vault,
        "ideation",
        {"mode": ideation_mode, "count": len(hypotheses), "codebase_hint": codebase_hint},
    )

    return {
        "success": True,
        "result": {
            "hypotheses": hypotheses,
            "count": len(hypotheses),
            "codebase_hint": codebase_hint,
            "mode": ideation_mode,
        },
        "research_vault": str(vault),
        "ai_scientist_v2_path": str(vendor),
        "warehouse_manifest": str(manifest),
        "ideation_error": ideation_error,
        "recommendations": [
            "Set AI_SCIENTIST_V2_PATH if vendor path differs from ./vendor/ai-scientist-v2.",
            "Enable Docker compose sandbox so future `research_execute` runs are container-only.",
        ],
        "related_operations": ["research_execute", "research_status", "research_review"],
    }


@mcp.tool()
async def research_execute(
    ctx: Context,
    *,
    ideas_file: str | None = None,
    idea_idx: int = 0,
    num_workers: int = 3,
    max_debug_depth: int = 3,
    allow_host_execution: bool = False,
) -> dict[str, Any]:
    """RESEARCH_EXECUTE — Launch AI Scientist experiment manager in Docker sandbox.

    Args:
        ctx: FastMCP context.
        ideas_file: Path to generated ideas JSON. Defaults to research_vault default.
        idea_idx: Index of the idea entry to execute.
        num_workers: Parallel branches for tree search.
        max_debug_depth: Max debug retries for buggy branches.
        allow_host_execution: Safety valve; host execution is blocked unless explicitly enabled.
    """
    vault = _research_vault_path()
    vault.mkdir(parents=True, exist_ok=True)
    vendor = _vendor_root()
    compose_path = Path("./docker-compose.yml").resolve()

    if not compose_path.exists():
        return {
            "success": False,
            "error": "docker-compose.yml not found in repository root",
            "recovery_options": [
                "Add docker-compose.yml with `scientist-executor` service.",
                "Run this tool from the sakana-mcp repo root.",
            ],
        }

    if not vendor.exists():
        return {
            "success": False,
            "error": "ai-scientist-v2 vendor directory missing",
            "recovery_options": [
                "Clone AI Scientist v2 into ./vendor/ai-scientist-v2.",
                "Set AI_SCIENTIST_V2_PATH to the correct location.",
            ],
        }

    if not allow_host_execution:
        ctx.info("research_execute enforcing Docker-only mode")

    selected_ideas = Path(ideas_file).resolve() if ideas_file else _default_ideas_path(vault)
    if not selected_ideas.exists():
        return {
            "success": False,
            "error": f"Ideas file not found: {selected_ideas}",
            "recovery_options": ["Run research_ideate first or provide `ideas_file`."],
        }

    await ctx.report_progress(1, 4, "Preparing run configuration")
    run_payload = {
        "ideas_file": str(selected_ideas),
        "idea_idx": idea_idx,
        "num_workers": num_workers,
        "max_debug_depth": max_debug_depth,
    }
    (vault / "execute_last_request.json").write_text(json.dumps(run_payload, indent=2), encoding="utf-8")
    container_ideas_path = vault / selected_ideas.name
    if container_ideas_path.resolve() != selected_ideas.resolve():
        container_ideas_path.write_text(selected_ideas.read_text(encoding="utf-8"), encoding="utf-8")

    runtime_cfg = _prepare_bfts_config(
        vendor_root=vendor,
        vault=vault,
        ideas_json=container_ideas_path,
        num_workers=num_workers,
        max_debug_depth=max_debug_depth,
    )

    run_cmd = [
        "docker",
        "compose",
        "-f",
        str(compose_path),
        "run",
        "--rm",
        "scientist-executor",
        "python",
        "-c",
        (
            "import os; "
            "from ai_scientist.treesearch.perform_experiments_bfts_with_agentmanager import "
            "perform_experiments_bfts; "
            f"os.chdir('/workspace/vendor/ai-scientist-v2'); "
            f"perform_experiments_bfts('/workspace/research_vault/runs/{runtime_cfg.name}')"
        ),
    ]

    await ctx.report_progress(2, 4, "Launching Dockerized execution")
    completed = subprocess.run(run_cmd, capture_output=True, text=True, check=False)

    await ctx.report_progress(3, 4, "Collecting execution logs")
    stdout_path = vault / "execute_last_stdout.log"
    stderr_path = vault / "execute_last_stderr.log"
    stdout_path.write_text(completed.stdout or "", encoding="utf-8")
    stderr_path.write_text(completed.stderr or "", encoding="utf-8")
    manifest = append_manifest(
        vault,
        "execution",
        {
            "ok": completed.returncode == 0,
            "return_code": completed.returncode,
            "num_workers": num_workers,
            "max_debug_depth": max_debug_depth,
            "ideas_file": str(selected_ideas),
        },
    )

    await ctx.report_progress(4, 4, "Execution finished")
    return {
        "success": completed.returncode == 0,
        "return_code": completed.returncode,
        "mode": "docker_only",
        "result": {
            "ideas_file": str(selected_ideas),
            "idea_idx": idea_idx,
            "num_workers": num_workers,
            "max_debug_depth": max_debug_depth,
        },
        "logs": {
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
        },
        "warehouse_manifest": str(manifest),
        "message": (
            "Experiment execution completed in Docker."
            if completed.returncode == 0
            else "Experiment execution failed. Check stderr log."
        ),
    }


@mcp.tool()
async def research_status(ctx: Context) -> dict[str, Any]:
    """RESEARCH_STATUS — Monitor tree health from latest run artifacts."""
    vault = _research_vault_path()
    await ctx.report_progress(1, 2, "Scanning run artifacts")
    stage_summaries = _summarize_stage_progress(vault)
    total_buggy = sum(int(item.get("buggy_nodes", 0)) for item in stage_summaries)
    total_good = sum(int(item.get("good_nodes", 0)) for item in stage_summaries)
    status = "idle"
    if stage_summaries:
        status = "running_or_completed"
    await ctx.report_progress(2, 2, "Status prepared")
    return {
        "success": True,
        "status": status,
        "tree_health": {
            "good_nodes": total_good,
            "buggy_nodes": total_buggy,
            "ratio_good_to_buggy": (total_good / total_buggy) if total_buggy > 0 else None,
        },
        "stages": stage_summaries,
        "research_vault": str(vault),
    }


@mcp.tool()
async def research_review(
    ctx: Context, *, pdf_path: str, model: str = "gpt-4o-2024-11-20"
) -> dict[str, Any]:
    """RESEARCH_REVIEW — Run VLM feedback loop over manuscript figures/captions."""
    vault = _research_vault_path()
    vault.mkdir(parents=True, exist_ok=True)
    vendor = _vendor_root()
    review_pdf = Path(pdf_path).resolve()
    if not review_pdf.exists():
        return {
            "success": False,
            "error": f"PDF not found: {review_pdf}",
            "recovery_options": ["Provide a valid manuscript PDF path."],
        }

    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))

    await ctx.report_progress(1, 3, "Initializing VLM client")
    from ai_scientist.perform_vlm_review import perform_imgs_cap_ref_review  # type: ignore
    from ai_scientist.vlm import create_client  # type: ignore

    client, client_model = create_client(model)
    await ctx.report_progress(2, 3, "Running figure-caption-reference review")
    review_payload = perform_imgs_cap_ref_review(client, client_model, str(review_pdf))

    out_path = vault / f"{review_pdf.stem}.review_img_cap_ref.json"
    out_path.write_text(json.dumps(review_payload, indent=2), encoding="utf-8")
    manifest = append_manifest(
        vault,
        "review",
        {"pdf_path": str(review_pdf), "figures_reviewed": len(review_payload), "model": client_model},
    )
    await ctx.report_progress(3, 3, "Review artifacts saved")
    return {
        "success": True,
        "model": client_model,
        "pdf_path": str(review_pdf),
        "review_path": str(out_path),
        "warehouse_manifest": str(manifest),
        "figures_reviewed": len(review_payload),
    }


@mcp.tool()
async def research_library(ctx: Context, *, domain: str | None = None) -> dict[str, Any]:
    """RESEARCH_LIBRARY — List sample and custom research tasks."""
    _ = ctx
    root = _repo_root()
    builtins = [task_to_dict(t) for t in SAMPLE_TASKS]
    custom = load_custom_tasks(root)
    merged = builtins + custom
    if domain:
        merged = [item for item in merged if str(item.get("domain", "")).lower() == domain.lower()]
    return {
        "success": True,
        "count": len(merged),
        "tasks": merged,
        "domains": sorted({str(item.get("domain", "unknown")) for item in merged}),
    }


@mcp.tool()
async def research_workflow_plan(ctx: Context, *, task_id: str, num_workers: int = 3) -> dict[str, Any]:
    """RESEARCH_WORKFLOW_PLAN — Build a guided agentic workflow plan for a task."""
    _ = ctx
    builtins = [task_to_dict(t) for t in SAMPLE_TASKS]
    all_tasks = builtins + load_custom_tasks(_repo_root())
    selected = next((item for item in all_tasks if item.get("task_id") == task_id), None)
    if not selected:
        return {
            "success": False,
            "error": f"Unknown task_id: {task_id}",
            "recovery_options": ["Call research_library() to inspect available task_ids."],
        }

    plan = [
        {
            "step": 1,
            "tool": "research_ideate",
            "args": {"codebase_hint": selected.get("starter_prompt"), "max_num_generations": 5},
            "goal": "Generate candidate hypotheses aligned with the selected task.",
        },
        {
            "step": 2,
            "tool": "research_execute",
            "args": {"num_workers": num_workers, "max_debug_depth": 3},
            "goal": "Run experiment manager in Docker sandbox.",
        },
        {
            "step": 3,
            "tool": "research_status",
            "args": {},
            "goal": "Track buggy/non-buggy tree evolution and stage progression.",
        },
        {
            "step": 4,
            "tool": "research_review",
            "args": {"pdf_path": "<path-to-paper.pdf>"},
            "goal": "Review figure-caption-text alignment and capture revision directives.",
        },
    ]
    return {
        "success": True,
        "task": selected,
        "workflow_plan": plan,
    }


def main() -> None:
    # Keep env vars wired early; enforcement can be tightened as tools are implemented.
    # (GEMINI_API_KEY and S2_API_KEY are required for later stages, not ideation stub.)
    _ = os.getenv("GEMINI_API_KEY")
    _ = os.getenv("S2_API_KEY")
    ensure_warehouse(_research_vault_path())

    mcp.run()


if __name__ == "__main__":
    main()

