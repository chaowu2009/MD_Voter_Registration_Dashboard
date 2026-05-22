# AGENT_WORKFLOW

## Planner Agent
- Responsibility: Break high-level goals into ordered tasks for specialized agents.
- Input: `goal: str`
- Output: `list[dict]` where each item includes task, assigned agent, and expected input.
- Failure handling: Returns a minimal fallback plan and logs warning if no goal is provided.

## Data Agent
- Responsibility: Acquire report data (live/fixture), parse and normalize to dashboard schema.
- Input: `report_selection: "latest" | list[str]`
- Output: `pandas.DataFrame` with Stage 1 schema columns (`year, month, county, party, registered`).
- Failure handling: If import fails, logs error and falls back to existing dashboard data.

## Analytics Agent
- Responsibility: Compute totals, party breakdown, growth metrics, and top counties.
- Input: `pandas.DataFrame`
- Output: `dict` with keys: `totals`, `party_breakdown`, `growth`, `top_counties`, `party_share_change`.
- Failure handling: Raises descriptive validation errors for missing required columns.

## Visualization Agent
- Responsibility: Build Plotly figures from analytics outputs.
- Input: `dict` from Analytics Agent.
- Output: `dict[str, Figure]` keyed by chart names.
- Failure handling: Logs failures and returns empty dictionary if chart build fails.

## QA Agent
- Responsibility: Run `pytest` and validate analytics consistency/anomaly checks.
- Input: DataFrame from Data Agent and analytics dict from Analytics Agent.
- Output: `{"passed": bool, "issues": list[str], "pytest_output": str}`
- Failure handling: Captures test failures and consistency errors in `issues`; sets `passed=False`.

## Critic Agent
- Responsibility: Review code quality, append findings to AGENT_NOTES.
- Input: `mode: "success" | "failure"`, optional context data (e.g. QA issues).
- Output: `list[str]` findings.
- Failure handling: Writes parse/error-handling findings even when workflow halts.

## Orchestration Rule
- Execution order: Planner -> Data -> Analytics -> QA -> Visualization -> Critic.
- QA Gate:
  - If QA passes: run Visualization, then Critic in success mode.
  - If QA fails: skip Visualization, run Critic in failure mode, then halt workflow.
