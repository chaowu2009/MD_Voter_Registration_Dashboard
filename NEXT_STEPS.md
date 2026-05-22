# NEXT_STEPS

## Future Improvements
- Add canonical county-name mapping to unify variants like "BALTIMORE CO." and "Baltimore".
- Add year/month extraction from PDF metadata or filenames instead of relying on defaults.
- Add structured import logs with run IDs for traceability.

## Known Limitations
- Current parser is table-layout dependent and may fail on scanned-image PDFs.
- Wide-layout mapping depends on known column positions; unseen layouts may require new aliases.

## Dashboard Ideas
- Add a dedicated Data Quality page showing issue counts by type and source file.
- Add filter controls for year/month/source_url on Overview and Growth Analysis.

## Automation Ideas
- Add scheduled import job to fetch and process new monthly reports automatically.
- Add CI workflow to run tests and lint checks on every commit.
- Add anomaly alerts when statewide totals shift beyond configurable thresholds.
