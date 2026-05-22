# Stage 1 — Simple Working MVP

## Goal
Learn the core agentic loop:

> **Build → Run → Fix → Improve**

Use this prompt first. Every later stage builds on the output of this one.

---

## Prompt

You are an autonomous AI software engineering agent.

Build a simple Streamlit dashboard for Maryland voter registration analysis.

Data source:
https://elections.maryland.gov/voter_registration/stats.html

For this first version:
- Do NOT scrape PDFs
- Use a manually downloaded CSV or generate a synthetic sample CSV
- Focus on creating a working dashboard first
- If no real CSV is available, generate synthetic data using Maryland's 24 real county names with realistic party and registration columns — document this assumption clearly

Requirements:
1. Use Streamlit
2. Use pandas
3. Use Plotly charts
4. Keep the project simple and readable
5. Use minimal dependencies
6. Include pytest tests for analytics functions

Features:

1. Overview page
   - Statewide total voters
   - Party breakdown chart
   - Top counties table

2. County Trends page
   - County selector
   - Voter trend chart
   - Party comparison chart

3. Growth Analysis page
   - Fastest growing counties
   - Party share change

Project structure:
```
streamlit_app.py
src/
  __init__.py
  analytics.py
data/
  sample.csv
tests/
  test_analytics.py
requirements.txt
README.md
```

Agentic Workflow:
1. Build the simplest working version first
2. Run the app (`streamlit run streamlit_app.py`)
3. Run tests (`pytest`)
4. Fix any errors — explain each fix when it occurs
5. Refactor only after functionality works
6. Document assumptions and limitations in README.md

Rules:
- Do not over-engineer
- Prefer simple functions
- Keep code modular
- Use clear variable names
- Never claim tests passed unless you have run pytest and shown the actual output
- Explain fixes when errors occur
- All UI values must come from `src/analytics.py` — no inline calculations in `streamlit_app.py`
- If a command fails, report the exact error and your next fix attempt

After the MVP works:
- Suggest future improvements
- Suggest how PDF scraping could be added in Stage 2

---

## Success Criteria

Before considering this step complete, verify every item:

- [ ] `streamlit run streamlit_app.py` starts without error
- [ ] All 3 pages render (Overview, County Trends, Growth Analysis)
- [ ] Charts display data from `sample.csv`
- [ ] `pytest` runs and shows actual pass/fail output (not assumed)
- [ ] `requirements.txt` lists all dependencies
- [ ] `README.md` documents any assumptions about the CSV schema

---

## What You Learn

| Concept | Where it appears |
|---|---|
| Agentic build loop | Build → Run → Fix → Improve cycle |
| Task decomposition | Breaking dashboard into 3 focused pages |
| Separation of concerns | Analytics in `src/`, UI in `streamlit_app.py` |
| Test-first discipline | Writing pytest before claiming things work |
| Assumption documentation | README captures schema decisions |
