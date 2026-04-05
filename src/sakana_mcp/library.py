from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ResearchTask:
    task_id: str
    title: str
    domain: str
    difficulty: str
    summary: str
    success_criteria: list[str]
    starter_prompt: str


SAMPLE_TASKS: list[ResearchTask] = [
    ResearchTask(
        task_id="ml_ablation_robustness",
        title="Ablation-driven robustness analysis",
        domain="machine-learning",
        difficulty="intermediate",
        summary="Identify which model components most influence robustness under shift/noise.",
        success_criteria=[
            "At least 3 ablation variants evaluated",
            "One robustness metric reported",
            "Clear hypothesis-to-result mapping in writeup",
        ],
        starter_prompt=(
            "Study robustness under distribution shift for a baseline model. "
            "Focus on component ablations that can be run within a few hours."
        ),
    ),
    ResearchTask(
        task_id="data_curriculum_generalization",
        title="Curriculum for generalization gains",
        domain="machine-learning",
        difficulty="advanced",
        summary="Test whether synthetic curriculum stages improve cross-dataset generalization.",
        success_criteria=[
            "Curriculum schedule explicitly defined",
            "Compared against no-curriculum baseline",
            "Generalization delta reported across at least 2 datasets",
        ],
        starter_prompt=(
            "Design a staged easy-to-hard curriculum and evaluate whether it improves "
            "generalization relative to direct training."
        ),
    ),
    ResearchTask(
        task_id="llm_debug_loop_efficiency",
        title="Debug-loop efficiency profiling",
        domain="agent-systems",
        difficulty="intermediate",
        summary="Measure whether deeper debug loops increase success rates or just cost.",
        success_criteria=[
            "Evaluate at multiple max_debug_depth values",
            "Track success, runtime, and failure categories",
            "Recommend an operating point with rationale",
        ],
        starter_prompt=(
            "Benchmark different debug depths in agentic tree search and quantify trade-offs."
        ),
    ),
    ResearchTask(
        task_id="vision_caption_consistency",
        title="Figure-caption-reference consistency audit",
        domain="scientific-writing",
        difficulty="beginner",
        summary="Use VLM review to find mismatches between figures, captions, and text references.",
        success_criteria=[
            "At least 10 figures reviewed or full paper coverage",
            "Mismatch categories summarized",
            "Actionable revision checklist produced",
        ],
        starter_prompt=(
            "Run comprehensive figure-caption-reference review and produce fix-ready findings."
        ),
    ),
]


def task_to_dict(task: ResearchTask) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "title": task.title,
        "domain": task.domain,
        "difficulty": task.difficulty,
        "summary": task.summary,
        "success_criteria": task.success_criteria,
        "starter_prompt": task.starter_prompt,
    }


def load_custom_tasks(root: Path) -> list[dict[str, Any]]:
    lib_dir = root / "research_library" / "tasks"
    if not lib_dir.exists():
        return []
    tasks: list[dict[str, Any]] = []
    for item in sorted(lib_dir.glob("*.json")):
        try:
            tasks.append(json.loads(item.read_text(encoding="utf-8")))
        except Exception:
            continue
    return tasks

