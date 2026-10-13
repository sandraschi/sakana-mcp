from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def ensure_warehouse(vault: Path) -> Path:
    warehouse = vault / "warehouse"
    for rel in [
        "runs",
        "reviews",
        "manuscripts",
        "datasets",
        "manifests",
        "exports",
    ]:
        (warehouse / rel).mkdir(parents=True, exist_ok=True)
    return warehouse


def append_manifest(vault: Path, event_type: str, payload: dict[str, Any]) -> Path:
    warehouse = ensure_warehouse(vault)
    date_key = datetime.now(UTC).strftime("%Y-%m-%d")
    manifest_path = warehouse / "manifests" / f"{date_key}.jsonl"
    record = {
        "ts_utc": utc_now_stamp(),
        "event_type": event_type,
        "payload": payload,
    }
    with manifest_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    return manifest_path
