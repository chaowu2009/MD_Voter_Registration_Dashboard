# Stage 3 — Add Self-Improvement Loops

## Builds on
Stages 1 and 2 must be complete. The dashboard loads real data from PDFs, falls back to sample CSV, and all existing tests pass.

## Goal
Learn:
- Autonomous debugging
- Reflection
- Retry systems

---

## Prompt

You are an autonomous AI software engineering agent.

Enhance the Maryland voter registration dashboard with agentic self-improvement workflows.

You are now responsible not just for building features, but for analyzing your own failures, fixing root causes, and documenting what you learned.

Add the following development workflow to every future implementation task:

```
1. Build
2. Run
3. Test
4. Analyze failures
5. Fix root cause (not symptoms)
6. Retry
7. Reflect
8. Improve code quality
```

New files to create:

`AGENT_NOTES.md`
After every major implementation, append an entry with:
- What failed
- Why it failed (root cause)
- What fix worked
- What assumptions were made
- What risks remain
- Use a consistent section template per entry so this file can be parsed later in Stage 5

`NEXT_STEPS.md`
Maintain a running list of:
- Future improvements
- Known limitations
- Dashboard enhancement ideas
- Automation opportunities

New technical requirements:
1. Add centralized logging using Python's `logging` module — all modules must use the same logger
2. Improve error messages — every exception must name the specific field, file, or operation that failed
3. Add `validate_dataframe(df, required_columns)` in `src/analytics.py` — raises a descriptive error if any required column is missing
4. Add data quality checks — flag rows where registration counts are zero, negative, or missing
5. Add retry logic in `src/sbe_scraper.py` — retry failed downloads up to 3 times with exponential backoff
6. Add caching for parsed PDF data — do not re-parse a PDF that has already been successfully parsed

New testing requirements — add to `tests/test_analytics.py`:
- Validate that statewide totals match the sum of county totals
- Validate that party percentages sum to 100% (within 0.1% tolerance)
- Validate that all county names match Maryland's 24 known counties
- Validate that missing values are handled without crashing

Agentic rules:
- Never rewrite large sections of code unnecessarily
- Prefer the minimal fix that resolves the root cause
- Always analyze the root cause before making a change
- Always rerun all tests after any fix
- Explain why each failure occurred before fixing it
- Never claim tests passed unless you have run pytest and shown the actual output

Mandatory reflection after each task:
Answer all 5 questions before marking the task complete:
1. What failed?
2. Why did it fail? (root cause, not symptom)
3. What fix worked?
4. What technical debt remains?
5. What should be improved later?

Write your answers into `AGENT_NOTES.md`.

---

## Success Criteria

Before considering this step complete, verify every item:

- [ ] `AGENT_NOTES.md` exists and contains at least one completed reflection entry
- [ ] `NEXT_STEPS.md` exists with at least 5 future items
- [ ] All modules import and use the centralized logger
- [ ] `validate_dataframe()` raises a descriptive error when a column is missing (tested)
- [ ] Retry logic in scraper is tested with a simulated failure
- [ ] All 5 reflection questions are answered for at least one task completed in this stage
- [ ] `pytest` passes with new tests added — show actual output

---

## What You Learn

| Concept | Where it appears |
|---|---|
| Autonomous debugging | Analyze failures before fixing |
| Reflection loops | 5-question debrief after every task |
| Retry systems | Exponential backoff in scraper |
| Root cause analysis | Fix cause, not symptom |
| Self-documentation | `AGENT_NOTES.md` as agent memory |
