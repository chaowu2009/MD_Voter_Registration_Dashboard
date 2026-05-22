# Maryland Voter Registration Dashboard - Agentic Prompt Workflow

This repository currently contains a staged prompt system for building and evolving a Streamlit dashboard project with agentic AI workflows.

## What Has Been Completed

The following prompt files were created and finalized:

- Prompt_Step_1.md
- Prompt_Step_2.md
- Prompt_Step_3.md
- Prompt_Step_4.md
- Prompt_Step_5.md

These prompts are designed to be executed in order, with each stage building on the previous one.

## Stage 1 Implementation Status

Stage 1 has now been executed in this repository.

Created project files:
- streamlit_app.py
- src/__init__.py
- src/analytics.py
- data/sample.csv
- tests/test_analytics.py
- requirements.txt

Synthetic data assumptions used for MVP:
- Data schema: year, month, county, party, registered
- Coverage: all 24 Maryland jurisdictions (23 counties + Baltimore City)
- Time range: monthly snapshots for Jan-Jun 2025
- Party buckets: Democratic, Republican, Unaffiliated, Other
- Counts are synthetic but monotonic over months to support trend/growth charts

## Stage Overview

1. Stage 1 (Prompt_Step_1.md): Build a simple working MVP dashboard.
2. Stage 2 (Prompt_Step_2.md): Add official data import (scraping + PDF parsing + ETL).
3. Stage 3 (Prompt_Step_3.md): Add self-improvement loops (logging, reflection, retries).
4. Stage 4 (Prompt_Step_4.md): Add a multi-agent workflow with orchestration and QA gating.
5. Stage 5 (Prompt_Step_5.md): Add autonomous evolution with benchmarks and optimization loops.

## Finalization Updates Applied

The prompt set was reviewed and refined for consistency and practical execution:

- Unified verification rule: never claim tests passed without real pytest output.
- Added missing scraping dependency in Stage 2: beautifulsoup4.
- Added offline fallback validation path for Stage 2 scraping checks.
- Made AGENT_NOTES format more structured in Stage 3 for later parsing.
- Fixed Stage 4 orchestration flow (QA pass/fail branches) and corrected required file count.
- Added machine-parseable failure line format in Stage 5 for failure tracking.

## Current Repository State

This repo currently contains prompt specifications only.

Application code (such as streamlit_app.py, src/, tests/, and data/) will be generated when executing Stage 1 and subsequent stages.

## How To Use

1. Start with Prompt_Step_1.md and complete all its success criteria.
2. Move to Prompt_Step_2.md only after Stage 1 is verified.
3. Continue sequentially through Prompt_Step_5.md.
4. At each stage, do not proceed until the stage-specific checklist is satisfied.

## Notes

- Stages 1-3 provide the highest immediate engineering value.
- Stages 4-5 are advanced and should be tackled after a stable baseline is working.
