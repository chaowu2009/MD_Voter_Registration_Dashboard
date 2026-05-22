# Stage 2 — Add Official Data Import

## Builds on
Stage 1 must be complete. The MVP dashboard is working, tests pass, and `sample.csv` is in use.

## Goal
Learn:
- Web scraping
- ETL (Extract, Transform, Load)
- PDF parsing
- Defensive coding

---

## Prompt

You are an autonomous AI software engineering agent.

Enhance the existing Streamlit Maryland voter registration dashboard built in Stage 1.

New goal:
Automatically import official Maryland State Board of Elections voter registration reports.

Official source:
https://elections.maryland.gov/voter_registration/stats.html

New requirements:
1. Scrape report links from the official page
2. Download selected PDF reports
3. Save PDFs locally in `data/raw/`
4. Extract voter registration tables using `pdfplumber`
5. Normalize extracted data into pandas DataFrames
6. Append cleaned data into local storage (CSV in `data/processed/`)

New source files to create:
```
src/
  sbe_scraper.py     # scrapes report links from the official page
  pdf_parser.py      # extracts tables from downloaded PDFs
  data_loader.py     # loads and normalizes data; falls back to sample.csv if parsing fails
```

New dashboard section — "Data Import" page:
- Show available reports from the official source
- Allow selecting one or more reports to download
- Trigger PDF download and parsing
- Display parsing success or failure per report
- Show a preview of successfully parsed data

Agentic workflow:
1. Implement one small feature at a time — scraper first, then parser, then loader
2. Test parsing on one PDF first before handling multiple
3. Validate extracted data manually — print column names and first 5 rows
4. Add logging and error handling to every step
5. Refactor duplicated parsing logic only after it works

Rules:
- Do NOT assume all PDF layouts are identical — handle layout variations gracefully
- Fail gracefully — a failed parse must log the reason and continue, not crash the app
- Preserve original PDF URLs in the stored data for traceability
- Save raw PDFs in `data/raw/` for debugging purposes
- Use `data/sample.csv` as fallback if all parsing fails
- Add `pdfplumber`, `requests`, and `beautifulsoup4` to `requirements.txt`
- Never claim tests passed unless you have run pytest and shown the actual output

Update `README.md` with:
- Import workflow description
- Troubleshooting steps for common PDF parsing failures
- Known parsing limitations

---

## Success Criteria

Before considering this step complete, verify every item:

- [ ] `sbe_scraper.py` successfully retrieves at least one real report link from the official page
- [ ] If the official page is unreachable, scraper is validated with a saved HTML fixture and reports that fallback clearly
- [ ] At least one PDF is downloaded to `data/raw/`
- [ ] `pdf_parser.py` extracts a valid table from that PDF (show actual column names and row count)
- [ ] Parsed data matches the schema established in Stage 1 (same column names)
- [ ] "Data Import" page renders in the dashboard without crashing
- [ ] App falls back to `sample.csv` gracefully if parsing fails
- [ ] `pytest` still passes — no regressions from Stage 1

---

## What You Learn

| Concept | Where it appears |
|---|---|
| Web scraping | `sbe_scraper.py` fetching report links |
| ETL pipeline | Download → Parse → Normalize → Store |
| Defensive coding | Graceful failure, fallback to sample data |
| Logging | Every parse step emits a log entry |
| Schema consistency | Parser output must match Stage 1 schema |
