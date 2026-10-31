# sakana-mcp — Copilot instructions

MCP + webapp repo. MCP server: `src/sakana_mcp/server.py` (FastMCP 3.4, 8 tools).
Dashboard backend: `webapp/backend/app.py` (port 10863). Frontend: `webapp/frontend`
(React+Vite, port 10862, Biome + `tsc --noEmit` gates).

Conventions: tools return `{"success", "message", ...}`; docstrings carry
`## Return Format` + `## Examples`; no `Args:` blocks (use `Annotated[..., Field]`).
Backend `/api/health` must stay an instant liveness probe (no heavy calls).
Suggest `sakana_help()` first when the user wants the research loop order.
