from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger("sakana-webapp")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _research_vault_path() -> Path:
    return Path(os.getenv("RESEARCH_VAULT_PATH", _repo_root() / "research_vault")).resolve()


def _vendor_root() -> Path:
    return Path(os.getenv("AI_SCIENTIST_V2_PATH", _repo_root() / "vendor" / "ai-scientist-v2")).resolve()


def _safe_read_text(path: Path, max_bytes: int = 2_000_000) -> str:
    data = path.read_bytes()
    if len(data) > max_bytes:
        data = data[:max_bytes]
    return data.decode("utf-8", errors="replace")


def _safe_load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _prepare_bfts_config(
    *, vendor_root: Path, vault: Path, ideas_json_name: str, num_workers: int, max_debug_depth: int
) -> Path:
    base_cfg_path = vendor_root / "bfts_config.yaml"
    if not base_cfg_path.exists():
        raise FileNotFoundError(f"Missing {base_cfg_path}")

    cfg = yaml.safe_load(base_cfg_path.read_text(encoding="utf-8")) or {}

    run_dir = (vault / "runs").resolve()
    (run_dir / "workspace").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "data").mkdir(parents=True, exist_ok=True)

    cfg["desc_file"] = f"/workspace/research_vault/{ideas_json_name}"
    cfg["workspace_dir"] = "/workspace/research_vault/runs/workspace"
    cfg["log_dir"] = "/workspace/research_vault/runs/logs"
    cfg["data_dir"] = "/workspace/research_vault/runs/data"

    cfg.setdefault("agent", {})
    cfg["agent"]["num_workers"] = int(num_workers)
    cfg["agent"].setdefault("search", {})
    cfg["agent"]["search"]["max_debug_depth"] = int(max_debug_depth)

    out_path = run_dir / "bfts_config.runtime.yaml"
    out_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return out_path


def _summarize_stage_progress(vault: Path) -> list[dict[str, Any]]:
    logs_root = vault / "runs" / "logs"
    if not logs_root.exists():
        return []

    # stage_*\\notes\\stage_progress.json
    files = sorted(logs_root.glob("stage_*\\notes\\stage_progress.json"))
    summaries: list[dict[str, Any]] = []
    for file_path in files:
        try:
            payload = _safe_load_json(file_path)
        except Exception:
            logger.warning("sakana webapp: skipping unreadable stage progress file %s", file_path)
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


def _docker_diagnostics() -> dict[str, Any]:
    compose_path = _repo_root() / "docker-compose.yml"
    services = ["sakana-mcp", "scientist-executor"]
    diag: dict[str, Any] = {
        "required_services": services,
        "docker_cli_available": False,
        "docker_daemon_reachable": False,
        "compose_file_exists": compose_path.exists(),
        "service_status": {name: {"present": False, "running": False, "state": "unknown"} for name in services},
    }

    try:
        subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True, timeout=5)
        diag["docker_cli_available"] = True
    except Exception:
        return diag

    try:
        subprocess.run(["docker", "info"], capture_output=True, text=True, check=True, timeout=5)
        diag["docker_daemon_reachable"] = True
    except Exception:
        return diag

    if not compose_path.exists():
        return diag

    try:
        ps = subprocess.run(
            ["docker", "compose", "-f", str(compose_path), "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=8,
        )
        lines = [line.strip() for line in (ps.stdout or "").splitlines() if line.strip()]
        entries: list[dict[str, Any]] = []
        for line in lines:
            try:
                parsed = json.loads(line)
                if isinstance(parsed, dict):
                    entries.append(parsed)
                elif isinstance(parsed, list):
                    entries.extend([item for item in parsed if isinstance(item, dict)])
            except Exception:
                logger.warning("sakana webapp: skipping unparsable compose ps line")
                continue

        by_name = {str(item.get("Service", "")): item for item in entries}
        for name in services:
            entry = by_name.get(name)
            if not entry:
                continue
            state = str(entry.get("State", "unknown")).lower()
            diag["service_status"][name] = {
                "present": True,
                "running": state == "running",
                "state": state,
            }
    except Exception:
        logger.warning("sakana webapp: docker compose ps status probe failed")
        pass

    return diag


def _runtime_mode(vault: Path) -> dict[str, Any]:
    ideation_last = vault / "ideation_last.json"
    if not ideation_last.exists():
        return {"mode": "fallback", "mock": True, "reason": "No ideation artifact found yet"}
    payload = _safe_load_json(ideation_last)
    mode = str(payload.get("mode", "fallback")).lower()
    is_live = mode == "ai_scientist_v2"
    return {
        "mode": "live" if is_live else "fallback",
        "mock": not is_live,
        "reason": "[MOCK] Fallback ideation active" if not is_live else "Live AI-Scientist ideation",
    }


app = FastAPI(title="sakana-mcp webapp backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10862",
        "http://localhost:10862",
        "tauri://localhost",
        "http://tauri.localhost",
        "https://tauri.localhost",
    ],
    # Fleet LAN/Tailscale access: any 192.168.x.x / 10.x.x.x / 100.x.x.x (Tailscale) host.
    allow_origin_regex=r"https?://((192\.168\.\d{1,3}\.\d{1,3})|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(100\.\d{1,3}\.\d{1,3}\.\d{1,3})|(localhost|127\.0\.0\.1))(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IdeateRequest(BaseModel):
    codebase_hint: str | None = None
    workshop_file: str | None = None
    model: str = "gemini-2.5-flash"
    max_num_generations: int = Field(default=5, ge=1, le=50)
    num_reflections: int = Field(default=3, ge=1, le=10)


class ExecuteRequest(BaseModel):
    ideas_file: str | None = None
    idea_idx: int = Field(default=0, ge=0)
    num_workers: int = Field(default=3, ge=1, le=16)
    max_debug_depth: int = Field(default=3, ge=0, le=10)


class ReviewRequest(BaseModel):
    pdf_path: str
    model: str = "gpt-4o-2024-11-20"


SAMPLE_TASKS: list[dict[str, Any]] = [
    {
        "task_id": "ml_ablation_robustness",
        "title": "Ablation-driven robustness analysis",
        "domain": "machine-learning",
        "difficulty": "intermediate",
        "summary": "Identify high-leverage components under shift/noise.",
        "success_criteria": [
            "At least 3 ablation variants evaluated",
            "One robustness metric reported",
            "Hypothesis-to-result mapping in writeup",
        ],
        "starter_prompt": "Focus on robustness and ablation signal density.",
    },
    {
        "task_id": "llm_debug_loop_efficiency",
        "title": "Debug-loop efficiency profiling",
        "domain": "agent-systems",
        "difficulty": "intermediate",
        "summary": "Quantify whether deeper debug loops improve outcomes or only cost.",
        "success_criteria": [
            "Multiple debug-depth settings compared",
            "Runtime and success rates measured",
            "Recommended operating point justified",
        ],
        "starter_prompt": "Benchmark trade-offs of max_debug_depth settings.",
    },
]


def _load_custom_tasks() -> list[dict[str, Any]]:
    lib_dir = _repo_root() / "research_library" / "tasks"
    if not lib_dir.exists():
        return []
    tasks: list[dict[str, Any]] = []
    for item in sorted(lib_dir.glob("*.json")):
        try:
            tasks.append(_safe_load_json(item))
        except Exception:
            logger.warning("sakana webapp: skipping unreadable library task file %s", item)
            continue
    return tasks


@app.get("/api/health")
def health() -> dict[str, Any]:
    # Liveness probe: MUST respond in <500ms. Fleet launcher polls with a
    # 2s per-request timeout, so no docker/file-heavy diagnostics here.
    # Full diagnostics live on /api/status (docker, tree health).
    return {"ok": True}


@app.post("/api/shutdown")
def shutdown(confirm: bool = False) -> dict[str, Any]:
    """Orderly exit: the fleet launcher calls this before restarting the service."""
    if not confirm:
        return {"ok": False, "message": "Shutdown requires confirm=true."}
    import threading

    def _exit() -> None:
        import time

        time.sleep(0.5)
        os._exit(0)

    threading.Thread(target=_exit, daemon=True).start()
    return {"ok": True, "message": "Sakana webapp backend shutting down in ~500 ms."}


@app.get("/api/v1/diagnostics")
def diagnostics() -> dict[str, Any]:
    """CUA-NSIS smoke surface: tool list, versions, and backend health in one call."""
    return {
        "ok": True,
        "server": "sakana-mcp",
        "version": "0.1.0",
        "repo_root": str(_repo_root()),
        "mcp_tools": [
            "sakana_help",
            "research_ideate",
            "research_execute",
            "research_status",
            "research_review",
            "research_library",
            "research_workflow_plan",
            "sakana_shutdown",
        ],
        "rest_routes": [
            "/api/health",
            "/api/status",
            "/api/ideate",
            "/api/execute",
            "/api/review",
            "/api/vault/list",
            "/api/vault/read",
            "/api/library/tasks",
            "/api/workflow/plan",
            "/api/skills",
            "/api/llm/providers",
            "/api/llm/discover",
            "/api/llm/models",
            "/api/llm/chat",
            "/api/llm/chat/stream",
            "/api/llm/onboarding",
            "/api/v1/diagnostics",
            "/api/shutdown",
        ],
        "runtime": _runtime_mode(_research_vault_path()),
        "docker": _docker_diagnostics(),
    }


@app.get("/api/skills")
def skills() -> dict[str, Any]:
    """Skill catalog for skill-first chat clients."""
    return {
        "ok": True,
        "skills": [
            {
                "name": "research-director",
                "description": "Coordinate ideate -> execute -> status -> review with sandbox boundaries.",
                "workflow": [
                    "research_library",
                    "research_workflow_plan",
                    "research_ideate",
                    "research_execute",
                    "research_status",
                    "research_review",
                ],
            }
        ],
    }


@app.get("/api/llm/discover")
def llm_discover() -> dict[str, Any]:
    """Auto-detect local LLM providers (Ollama :11434, LM Studio :1234)."""
    import httpx

    providers: list[dict[str, Any]] = []
    for name, base in (("ollama", "http://127.0.0.1:11434"), ("lmstudio", "http://127.0.0.1:1234")):
        path = "/api/tags" if name == "ollama" else "/v1/models"
        try:
            resp = httpx.get(base + path, timeout=2.0)
            detected = resp.status_code == 200
        except Exception:
            detected = False
        providers.append({"name": name, "base_url": base, "detected": detected, "local": True, "free": True})
    return {"ok": True, "providers": providers}


@app.get("/api/llm/models")
def llm_models(provider: str = "ollama") -> dict[str, Any]:
    """Model list for a provider: live when reachable, curated fallback otherwise."""
    import httpx

    base = "http://127.0.0.1:1234" if provider == "lmstudio" else "http://127.0.0.1:11434"
    path = "/v1/models" if provider == "lmstudio" else "/api/tags"
    try:
        resp = httpx.get(base + path, timeout=3.0)
        resp.raise_for_status()
        payload = resp.json()
        if provider == "lmstudio":
            models = [m.get("id", "") for m in payload.get("data", []) if m.get("id")]
        else:
            models = [m.get("name", "") for m in payload.get("models", []) if m.get("name")]
        return {"ok": True, "provider": provider, "models": models, "live": True}
    except Exception as exc:
        logger.warning("sakana webapp: llm models probe failed for %s: %s", provider, exc)
        return {"ok": True, "provider": provider, "models": ["gemma3:1b"], "live": False}


class ChatRequest(BaseModel):
    provider: str = "ollama"
    model: str = "gemma3:1b"
    prompt: str = ""


@app.post("/api/llm/chat")
def llm_chat(req: ChatRequest) -> dict[str, Any]:
    """Backend chat proxy (non-streaming) — the ONLY path Chat uses. Keys never leave the server."""
    import httpx

    try:
        resp = httpx.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": req.model, "prompt": req.prompt, "stream": False},
            timeout=120.0,
        )
        resp.raise_for_status()
        return {"ok": True, "response": resp.json().get("response", "")}
    except Exception as exc:
        logger.warning("sakana webapp: llm chat proxy failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"LLM backend unreachable: {exc}") from exc


@app.post("/api/llm/chat/stream")
def llm_chat_stream(req: ChatRequest) -> Any:
    """Streaming chat proxy (SSE, OpenAI-style chunks) — the ONLY path Chat uses."""
    import httpx
    from fastapi.responses import StreamingResponse

    def event_source() -> Any:
        try:
            with httpx.stream(
                "POST",
                "http://127.0.0.1:11434/api/generate",
                json={"model": req.model, "prompt": req.prompt, "stream": True},
                timeout=180.0,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except Exception:
                        logger.debug("sakana webapp: skipping malformed SSE chunk line")
                        continue
                    text = chunk.get("response", "")
                    yield f"data: {json.dumps({'text': text, 'done': bool(chunk.get('done', False))})}\n\n"
                    if chunk.get("done", False):
                        break
        except Exception as exc:
            logger.warning("sakana webapp: llm chat stream failed: %s", exc)
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")


@app.get("/api/llm/onboarding")
def llm_onboarding() -> dict[str, Any]:
    """Fresh-install starter facts for the under-hero onboarding cue."""
    return {
        "ok": True,
        "steps": [
            "Set GEMINI_API_KEY for live ideation (else deterministic fallback hypotheses).",
            "Run docker compose up --build for the sandboxed executor.",
            "Pick a task in Library, generate a plan, ideate, execute, monitor status.",
        ],
        "recommended_path": "library -> workflow_plan -> ideate -> execute -> status -> review",
    }


@app.post("/api/ideate")
def ideate(req: IdeateRequest) -> dict[str, Any]:
    vault = _research_vault_path()
    vault.mkdir(parents=True, exist_ok=True)
    vendor = _vendor_root()

    hypotheses: list[dict[str, str]] = []
    mode = "fallback"
    ideation_error: str | None = None

    def fallback() -> list[dict[str, str]]:
        return [
            {"id": "H1", "title": "Baseline ablations", "hypothesis": "Targeted ablations reveal leverage."},
            {"id": "H2", "title": "Adaptive pruning", "hypothesis": "Prune low-promise branches to save compute."},
            {"id": "H3", "title": "Adversarial debugging", "hypothesis": "Adversarial debug reduces failure modes."},
            {"id": "H4", "title": "Synthetic curriculum", "hypothesis": "Curriculum improves generalization."},
            {"id": "H5", "title": "Structured peer review", "hypothesis": "Schema-guided review improves clarity."},
        ]

    if vendor.exists():
        try:
            import sys

            if str(vendor) not in sys.path:
                sys.path.insert(0, str(vendor))
            from ai_scientist.llm import create_client  # type: ignore
            from ai_scientist.perform_ideation_temp_free import generate_temp_free_idea  # type: ignore

            if req.workshop_file:
                workshop_path = Path(req.workshop_file).resolve()
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
                                req.codebase_hint or "Generate robust, testable ML research hypotheses.",
                                "",
                                "# Abstract",
                                req.codebase_hint
                                or "Investigate autonomous scientific pipelines with emphasis on reproducibility.",
                            ]
                        ),
                        encoding="utf-8",
                    )

            idea_json_path = vault / f"{workshop_path.stem}.json"
            workshop_description = workshop_path.read_text(encoding="utf-8")
            client, client_model = create_client(req.model)
            ideas = generate_temp_free_idea(
                idea_fname=str(idea_json_path),
                client=client,
                model=client_model,
                workshop_description=workshop_description,
                max_num_generations=req.max_num_generations,
                num_reflections=req.num_reflections,
            )
            for idx, idea in enumerate(ideas[:5], start=1):
                hypotheses.append(
                    {
                        "id": f"H{idx}",
                        "title": str(idea.get("Title", idea.get("Name", f"Idea {idx}"))),
                        "hypothesis": str(idea.get("Short Hypothesis", idea.get("Abstract", ""))),
                    }
                )
            mode = "ai_scientist_v2"
        except Exception as exc:
            ideation_error = str(exc)
            hypotheses = fallback()
            mode = "fallback"
    else:
        hypotheses = fallback()

    record = {"mode": mode, "codebase_hint": req.codebase_hint, "hypotheses": hypotheses}
    if ideation_error:
        record["error"] = ideation_error
    (vault / "ideation_last.json").write_text(json.dumps(record, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "mode": mode,
        "ideation_error": ideation_error,
        "hypotheses": hypotheses,
        "ideas_json_path": str(
            (vault / (Path(req.workshop_file).stem + ".json"))
            if req.workshop_file
            else (vault / "default_workshop.json")
        ),
        "research_vault": str(vault),
    }


@app.post("/api/execute")
def execute(req: ExecuteRequest) -> dict[str, Any]:
    vault = _research_vault_path()
    vault.mkdir(parents=True, exist_ok=True)
    vendor = _vendor_root()
    repo = _repo_root()

    if not vendor.exists():
        raise HTTPException(status_code=400, detail="ai-scientist-v2 not found")

    ideas_path = Path(req.ideas_file).resolve() if req.ideas_file else (vault / "default_workshop.json")
    if not ideas_path.exists():
        raise HTTPException(status_code=400, detail=f"Ideas file not found: {ideas_path}")

    container_ideas = vault / ideas_path.name
    if container_ideas.resolve() != ideas_path.resolve():
        container_ideas.write_text(ideas_path.read_text(encoding="utf-8"), encoding="utf-8")

    runtime_cfg = _prepare_bfts_config(
        vendor_root=vendor,
        vault=vault,
        ideas_json_name=container_ideas.name,
        num_workers=req.num_workers,
        max_debug_depth=req.max_debug_depth,
    )

    compose_path = repo / "docker-compose.yml"
    if not compose_path.exists():
        raise HTTPException(status_code=400, detail="docker-compose.yml missing in repo root")

    cmd = [
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
            "from ai_scientist.treesearch.perform_experiments_bfts_with_agentmanager import perform_experiments_bfts; "
            "os.chdir('/workspace/vendor/ai-scientist-v2'); "
            f"perform_experiments_bfts('/workspace/research_vault/runs/{runtime_cfg.name}')"
        ),
    ]

    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    (vault / "execute_last_stdout.log").write_text(completed.stdout or "", encoding="utf-8")
    (vault / "execute_last_stderr.log").write_text(completed.stderr or "", encoding="utf-8")
    (vault / "execute_last_request.json").write_text(json.dumps(req.model_dump(), indent=2), encoding="utf-8")

    return {
        "ok": completed.returncode == 0,
        "return_code": completed.returncode,
        "runtime_config": str(runtime_cfg),
        "stdout_log": str(vault / "execute_last_stdout.log"),
        "stderr_log": str(vault / "execute_last_stderr.log"),
        "request": req.model_dump(),
    }


@app.get("/api/status")
def status() -> dict[str, Any]:
    vault = _research_vault_path()
    stages = _summarize_stage_progress(vault)
    total_buggy = sum(int(s.get("buggy_nodes", 0)) for s in stages)
    total_good = sum(int(s.get("good_nodes", 0)) for s in stages)
    runtime = _runtime_mode(vault)
    return {
        "ok": True,
        "status": "running_or_completed" if stages else "idle",
        "runtime": runtime,
        "repo_root": str(_repo_root()),
        "ai_scientist_v2": str(_vendor_root()),
        "tree_health": {
            "good_nodes": total_good,
            "buggy_nodes": total_buggy,
            "ratio_good_to_buggy": (total_good / total_buggy) if total_buggy else None,
        },
        "docker": _docker_diagnostics(),
        "stages": stages,
        "research_vault": str(vault),
    }


@app.post("/api/review")
def review(req: ReviewRequest) -> dict[str, Any]:
    vault = _research_vault_path()
    vault.mkdir(parents=True, exist_ok=True)
    vendor = _vendor_root()
    pdf = Path(req.pdf_path).resolve()
    if not pdf.exists():
        raise HTTPException(status_code=400, detail=f"PDF not found: {pdf}")
    if not vendor.exists():
        raise HTTPException(status_code=400, detail="ai-scientist-v2 not found")

    import sys

    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))

    from ai_scientist.perform_vlm_review import perform_imgs_cap_ref_review  # type: ignore
    from ai_scientist.vlm import create_client  # type: ignore

    client, client_model = create_client(req.model)
    payload = perform_imgs_cap_ref_review(client, client_model, str(pdf))
    out_path = vault / f"{pdf.stem}.review_img_cap_ref.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "model": client_model,
        "pdf_path": str(pdf),
        "review_path": str(out_path),
        "figures_reviewed": len(payload),
    }


@app.get("/api/vault/list")
def vault_list(rel: str = "") -> dict[str, Any]:
    vault = _research_vault_path()
    target = (vault / rel).resolve()
    if not str(target).startswith(str(vault)):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not found")

    if target.is_file():
        return {"ok": True, "type": "file", "path": str(target), "name": target.name}

    entries = []
    for p in sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        entries.append(
            {
                "name": p.name,
                "type": "file" if p.is_file() else "dir",
                "size": p.stat().st_size if p.is_file() else None,
            }
        )
    return {"ok": True, "type": "dir", "path": str(target), "rel": rel, "entries": entries}


@app.get("/api/vault/read")
def vault_read(rel: str) -> dict[str, Any]:
    vault = _research_vault_path()
    target = (vault / rel).resolve()
    if not str(target).startswith(str(vault)):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True, "path": str(target), "content": _safe_read_text(target)}


@app.get("/api/library/tasks")
def library_tasks(domain: str | None = None) -> dict[str, Any]:
    tasks = SAMPLE_TASKS + _load_custom_tasks()
    if domain:
        tasks = [t for t in tasks if str(t.get("domain", "")).lower() == domain.lower()]
    return {
        "ok": True,
        "count": len(tasks),
        "domains": sorted({str(t.get("domain", "unknown")) for t in tasks}),
        "tasks": tasks,
    }


@app.get("/api/workflow/plan")
def workflow_plan(task_id: str, num_workers: int = 3) -> dict[str, Any]:
    tasks = SAMPLE_TASKS + _load_custom_tasks()
    selected = next((t for t in tasks if t.get("task_id") == task_id), None)
    if not selected:
        raise HTTPException(status_code=404, detail=f"Unknown task_id: {task_id}")
    plan = [
        {
            "step": 1,
            "tool": "research_ideate",
            "args": {"codebase_hint": selected.get("starter_prompt"), "max_num_generations": 5},
            "goal": "Generate hypotheses for the selected task profile",
        },
        {
            "step": 2,
            "tool": "research_execute",
            "args": {"num_workers": num_workers, "max_debug_depth": 3},
            "goal": "Run sandboxed experiment manager",
        },
        {
            "step": 3,
            "tool": "research_status",
            "args": {},
            "goal": "Monitor buggy/non-buggy tree evolution",
        },
        {
            "step": 4,
            "tool": "research_review",
            "args": {"pdf_path": "<path-to-paper.pdf>"},
            "goal": "Run VLM review and package revision directives",
        },
    ]
    return {"ok": True, "task": selected, "plan": plan}
