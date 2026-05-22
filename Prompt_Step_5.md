# Stage 5 — Autonomous Evolution System

## Builds on
Stages 1–4 must be complete. The multi-agent orchestrator runs end-to-end, QA gates are enforced, and `AGENT_WORKFLOW.md` is up to date.

## Goal
Learn:
- Recursive self-improvement
- Benchmark-driven optimization
- Evolving workflows

---

## Prompt

You are an autonomous AI software engineering agent.

Enhance the Maryland voter registration dashboard into a self-improving analytics platform. The system must now measure its own performance, detect weak points, and recommend targeted improvements — based on evidence, not guesswork.

The core loop for this stage:

```
Generate → Execute → Evaluate → Improve → Retest
```

This loop must be explicit and traceable. Every improvement must start with a measurement, not an assumption.

New capabilities to implement:

**1. Performance Benchmarking**
- Add `src/profiler.py`
- Measure execution time for each analytics function using Python's `time` module
- Measure Streamlit page load time (approximate: time from data load to chart render)
- Log all benchmarks to `data/benchmarks.csv` with timestamp, function name, duration
- **Rule: Do not optimize anything until you have a baseline benchmark number**

**2. Slow Query Detection**
- In `src/profiler.py`, flag any function that takes longer than 1 second
- Emit a warning log entry with the function name and duration
- The system must surface slow functions — not silently ignore them

**3. Failure Pattern Detection**
- In `AGENT_NOTES.md`, track every parsing failure with: URL, error type, date
- Use one machine-parseable line per failure (for example: `FAILURE | date=YYYY-MM-DD | source=<url-or-id> | error=<type>`)
- Add `src/failure_tracker.py` to read `AGENT_NOTES.md` and identify failures that have occurred more than twice
- Repeated failures must trigger a warning in the dashboard: "This data source has failed N times"

**4. Improvement Report**
- Create `IMPROVEMENT_REPORT.md`
- After each optimization cycle, append an entry with:
  - What was measured (benchmark before)
  - What was changed
  - What improved (benchmark after)
  - What did not improve
  - What to try next

**5. Caching Optimization**
- Identify which analytics functions are called repeatedly with the same input
- Add `@st.cache_data` or `functools.lru_cache` where appropriate
- Benchmark before and after — record results in `IMPROVEMENT_REPORT.md`

**6. Data Completeness Checks**
- Add `src/data_quality.py`
- Check: are all 24 Maryland counties present?
- Check: are all expected parties represented?
- Check: are there any time gaps in monthly data?
- Display a data quality summary in the dashboard sidebar

**7. Anomaly Detection**
- Flag counties where registration dropped by more than 10% in a single month
- Flag any month where statewide totals decreased year-over-year
- Display anomalies as warnings in the Growth Analysis page

Agentic behavior rules:
- Improve only based on measurable evidence — benchmark numbers, failure counts, or test failures
- Do not self-modify randomly or speculatively
- Every change must be justified in `IMPROVEMENT_REPORT.md` with before/after data
- Preserve readability — reject any optimization that makes code significantly harder to understand
- Rerun all tests after every change — show actual `pytest` output
- Never claim tests passed unless you have run pytest and shown the actual output

---

## Success Criteria

Before considering this step complete, verify every item:

- [ ] `data/benchmarks.csv` exists and contains at least one full benchmark run
- [ ] At least one function has been optimized — `IMPROVEMENT_REPORT.md` shows before/after times
- [ ] `failure_tracker.py` correctly identifies a repeated failure (write a test with mock data)
- [ ] Data quality summary appears in the dashboard sidebar
- [ ] At least one anomaly is detectable with the synthetic or real data
- [ ] `IMPROVEMENT_REPORT.md` has at least one completed entry with before/after metrics
- [ ] `pytest` passes — show actual output
- [ ] No optimization was made without a prior benchmark — verify in `IMPROVEMENT_REPORT.md`

---

## What You Learn

| Concept | Where it appears |
|---|---|
| Benchmark-driven development | Measure first, then optimize |
| Recursive improvement | Generate → Execute → Evaluate → Improve → Retest |
| Failure pattern recognition | `failure_tracker.py` finding repeated errors |
| Evidence-based decision making | No change without a metric |
| Self-documentation | `IMPROVEMENT_REPORT.md` as the agent's audit trail |

---

## Recommended Focus Order

The ChatGPT recommendation applies here too:

> Spend most of your time on **Stages 1, 2, and 3**.
> Those are where most real-world engineering value exists today.

Stage 4 (multi-agent) and Stage 5 (autonomous evolution) are advanced patterns.
Master the first three before building here.
