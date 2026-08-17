# sakana-mcp (MCPB Bundle)

MCP server wrapping Sakana AI Scientist v2 for autonomous research loops

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "sakana-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "sakana_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **research_ideate**: research_ideate
- **research_execute**: research_execute
- **research_status**: research_status
- **research_review**: research_review
- **research_library**: research_library
- **research_workflow_plan**: research_workflow_plan

## Requirements

- Python 3.12+
- uv
