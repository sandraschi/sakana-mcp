"""Webapp backend contract: liveness probe shape + endpoint availability.

Health is a hard latency contract (fleet launcher probes with a 2s timeout):
this test fails if /api/health ever becomes a slow diagnostics call again.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "webapp" / "backend"))

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_is_instant_liveness_probe() -> None:
    started = time.perf_counter()
    resp = client.get("/api/health")
    elapsed = time.perf_counter() - started
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert elapsed < 2.0, f"/api/health took {elapsed:.2f}s (launcher timeout is 2s)"


def test_status_has_runtime_and_docker() -> None:
    resp = client.get("/api/status")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["ok"] is True
    assert "runtime" in payload
    assert "tree_health" in payload
    assert "docker" in payload


def test_discovery_endpoints_present() -> None:
    for path in ("/api/skills", "/api/llm/discover", "/api/llm/models", "/api/llm/onboarding"):
        resp = client.get(path)
        assert resp.status_code == 200, path
        assert resp.json()["ok"] is True, path


def test_diagnostics_lists_tools() -> None:
    resp = client.get("/api/v1/diagnostics")
    assert resp.status_code == 200
    assert "research_ideate" in resp.json()["mcp_tools"]


def test_shutdown_requires_confirm() -> None:
    resp = client.post("/api/shutdown")
    assert resp.status_code == 200
    assert resp.json()["ok"] is False
