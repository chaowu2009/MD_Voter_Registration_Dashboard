from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import pdfplumber

logger = logging.getLogger(__name__)


def _clean_columns(columns: list[str]) -> list[str]:
    cleaned = []
    seen: dict[str, int] = {}
    for col in columns:
        value = str(col or "").strip().lower()
        value = value.replace("%", "pct")
        value = "_".join(value.split())
        if not value:
            value = "column"
        count = seen.get(value, 0)
        seen[value] = count + 1
        if count > 0:
            value = f"{value}_{count + 1}"
        cleaned.append(value)
    return cleaned


def parse_pdf_tables(pdf_path: str) -> pd.DataFrame:
    """Parse all table rows from a PDF into one DataFrame.

    This parser is intentionally permissive because report layouts may vary.
    """
    file_path = Path(pdf_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    frames: list[pd.DataFrame] = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            for table in tables:
                if not table or len(table) < 2:
                    continue

                header = _clean_columns([str(value) for value in table[0]])
                body = table[1:]
                candidate = pd.DataFrame(body, columns=header)
                candidate = candidate.dropna(how="all")
                if candidate.empty:
                    continue

                candidate["source_page"] = page_number
                frames.append(candidate)

    if not frames:
        raise ValueError(f"No parseable tables found in PDF: {pdf_path}")

    combined = pd.concat(frames, ignore_index=True)
    logger.info("Parsed %s rows and %s columns from %s", len(combined), len(combined.columns), pdf_path)
    return combined
