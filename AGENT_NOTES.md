# AGENT_NOTES

## Entry Template
- Date:
- Task:
- What failed?
- Why did it fail? (root cause)
- What fix worked?
- What assumptions were made?
- What risks remain?

## Entry 2026-05-21 - Stage 3 implementation
- Date: 2026-05-21
- Task: Implement Step 3 self-improvement loop requirements (logging, validation, retry, cache, tests)
- What failed?
  - Live PDF parsing initially produced duplicate-column concat errors.
  - Early normalization could not map real SBE wide tables to long-form Stage 1 schema.
- Why did it fail? (root cause)
  - Root cause 1: parser accepted repeated/blank headers from PDF tables without enforcing uniqueness.
  - Root cause 2: normalizer expected long-form columns and did not support wide party-column layout from SBE reports.
- What fix worked?
  - Added unique header generation in parser and a wide-layout normalization path.
  - Added centralized logging and descriptive validation errors to surface schema mismatches quickly.
  - Added retry with exponential backoff and parse cache to improve robustness.
- What assumptions were made?
  - Assumed monthly report tables include county and party totals in a consistent enough wide pattern for alias mapping.
  - Assumed cached parsed CSV per PDF stem is acceptable for this stage.
- What risks remain?
  - Some PDFs may still use layouts that require additional heuristics or OCR.
  - County-name normalization (for punctuation/abbreviations) may need stricter canonical mapping later.
