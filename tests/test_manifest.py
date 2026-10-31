"""Smoke tests: packaging manifest validity + MCP tool-surface sync.

1V template-conformance guard: the tool list must be identical in
mcpb/manifest.json, glama.json, and the live FastMCP registration.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOOLS = {
    "sakana_help",
    "research_ideate",
    "research_execute",
    "research_status",
    "research_review",
    "research_library",
    "research_workflow_plan",
    "sakana_shutdown",
}


def _live_tool_names() -> set[str]:
    from sakana_mcp.server import mcp

    async def collect() -> list:
        return await mcp.list_tools()

    return {t.name for t in asyncio.run(collect())}


def test_live_tools_match_expected() -> None:
    assert _live_tool_names() == EXPECTED_TOOLS


def test_manifest_uses_spec_variables() -> None:
    manifest = json.loads((REPO_ROOT / "mcpb" / "manifest.json").read_text(encoding="utf-8"))
    blob = json.dumps(manifest)
    assert "${PWD}" not in blob, "manifest must not use ${PWD} (Claude Desktop cannot expand it)"
    assert "${__dirname}" in blob
    assert manifest["server"]["mcp_config"]["args"] == [
        "run",
        "--directory",
        "${__dirname}",
        "python",
        "-m",
        "sakana_mcp",
    ]


def test_manifest_tools_in_sync() -> None:
    manifest = json.loads((REPO_ROOT / "mcpb" / "manifest.json").read_text(encoding="utf-8"))
    assert {t["name"] for t in manifest["tools"]} == EXPECTED_TOOLS


def test_glama_tools_in_sync() -> None:
    glama = json.loads((REPO_ROOT / "glama.json").read_text(encoding="utf-8"))
    assert set(glama["tools"]) == EXPECTED_TOOLS


def test_entry_point_imports() -> None:
    import sakana_mcp.server  # noqa: F401
