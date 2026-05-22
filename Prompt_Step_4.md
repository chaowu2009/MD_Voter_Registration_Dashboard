# Stage 4 — Add Multi-Agent Workflow

## Builds on
Stages 1, 2, and 3 must be complete. The dashboard is working, self-improvement loops are in place, and `AGENT_NOTES.md` has at least one reflection entry.

## Goal
Learn:
- Planner/executor separation
- Specialized agents
- Agent orchestration

---

## Prompt

You are an autonomous AI software engineering agent.

Refactor the Maryland voter registration dashboard into a multi-agent workflow. Each agent has a single, clearly defined responsibility. Agents communicate by passing structured outputs — not by sharing global state.

Create the following specialized agents:

**1. Planner Agent** (`src/agents/planner.py`)
- Receives a high-level goal as input
- Breaks it into an ordered list of sub-tasks
- Assigns each sub-task to the appropriate agent
- Output: a task plan as a list of dicts: `[{"task": str, "agent": str, "input": dict}]`

**2. Data Agent** (`src/agents/data_agent.py`)
- Handles all scraping and PDF parsing
- Wraps `sbe_scraper.py`, `pdf_parser.py`, `data_loader.py`
- Input: a list of report URLs or "latest"
- Output: a normalized pandas DataFrame matching the Stage 1 schema

**3. Analytics Agent** (`src/agents/analytics_agent.py`)
- Handles all calculations and statistics
- Wraps `src/analytics.py`
- Input: a pandas DataFrame
- Output: a dict of results: `{"totals": ..., "party_breakdown": ..., "growth": ..., "top_counties": ...}`

**4. Visualization Agent** (`src/agents/viz_agent.py`)
- Creates all Plotly charts
- Input: analytics results dict from Analytics Agent
- Output: a dict of Plotly figure objects, keyed by chart name

**5. QA Agent** (`src/agents/qa_agent.py`)
- Runs `pytest` programmatically
- Validates that Analytics Agent outputs are internally consistent (totals match, percentages sum correctly)
- Detects anomalies: counties with zero registrations, impossible growth rates
- Output: `{"passed": bool, "issues": [str]}`
- **No downstream step may proceed if QA Agent returns `passed: False`**

**6. Critic Agent** (`src/agents/critic.py`)
- Reviews completed code for simplification opportunities
- Flags functions longer than 30 lines
- Flags duplicate logic across modules
- Flags missing error handling
- Output: a list of findings written to `AGENT_NOTES.md`

Orchestration:
- Create `src/agents/orchestrator.py`
- The orchestrator calls agents in order: Planner → Data → Analytics → QA → Visualization
- If QA passes: run Visualization, then Critic
- If QA fails: skip Visualization, run Critic in failure-review mode, then halt
- Each agent logs its start, finish, and output summary

Create `AGENT_WORKFLOW.md` documenting:
- Each agent's responsibility
- Its input format
- Its output format
- Its failure behavior

Requirements:
- Keep the architecture simple — no external agent frameworks (no LangChain, no AutoGen)
- Each agent is a plain Python class or module with a `run()` function
- Document agent responsibilities clearly at the top of each file
- The existing Streamlit dashboard must still work — the multi-agent system is an optional workflow layer, not a replacement
- Never claim tests passed unless you have run pytest and shown the actual output

---

## Success Criteria

Before considering this step complete, verify every item:

- [ ] All 7 files exist in `src/agents/` (6 agents + `orchestrator.py`)
- [ ] `orchestrator.py` can run end-to-end without error (show terminal output)
- [ ] QA Agent correctly blocks visualization when given intentionally bad data (write a test for this)
- [ ] `AGENT_WORKFLOW.md` documents all 6 agents with input/output/failure sections
- [ ] Existing Streamlit dashboard still runs unchanged (`streamlit run streamlit_app.py`)
- [ ] `pytest` passes — show actual output

---

## What You Learn

| Concept | Where it appears |
|---|---|
| Separation of responsibilities | Each agent has one job |
| Structured agent communication | Agents pass dicts, not raw state |
| Orchestration | `orchestrator.py` controls execution order |
| QA as a gate | No downstream work if QA fails |
| Critic pattern | Post-hoc review separate from construction |
