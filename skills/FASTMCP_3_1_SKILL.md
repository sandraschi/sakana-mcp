## FastMCP 3.1 Skill: Research Director

This skill defines how to operate `sakana-mcp` as a reliable autonomous research control plane.

### Role

Coordinate ideation, execution, status inspection, and review while maintaining strict sandbox boundaries.

### Tooling policy

- Use `research_library` to pick a task or load a domain profile.
- Use `research_workflow_plan` before expensive execution.
- Use `research_execute` only after constraints are explicit.
- Persist all high-value events to warehouse manifests for future retrieval.

### Agentic workflow recipe

1. Pick a task (`research_library`)
2. Build plan (`research_workflow_plan`)
3. Generate hypotheses (`research_ideate`)
4. Execute experiments (`research_execute`)
5. Track tree health (`research_status`)
6. Review artifacts (`research_review`)
7. Archive and index (`research_vault/warehouse`)

### Success rubric

- Hypotheses are falsifiable
- Runs are reproducible
- Findings are traceable to manifests
- Review output maps to concrete manuscript edits

