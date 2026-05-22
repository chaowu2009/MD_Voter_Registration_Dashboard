from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.logging_config import get_logger
from src.pdf_parser import parse_pdf_tables

logger = get_logger(__name__)

EXPECTED_COLUMNS = ["year", "month", "county", "party", "registered"]

COLUMN_ALIASES = {
    "county": "county",
    "6": "county",
    "county_name": "county",
    "jurisdiction": "county",
    "party": "party",
    "party_name": "party",
    "affiliation": "party",
    "registered": "registered",
    "registrations": "registered",
    "voters": "registered",
    "total": "registered",
    "year": "year",
    "month": "month",
}

KNOWN_COUNTY_TOKENS = {
    "ALLEGANY",
    "ANNE ARUNDEL",
    "BALTIMORE CITY",
    "BALTIMORE",
    "CALVERT",
    "CAROLINE",
    "CARROLL",
    "CECIL",
    "CHARLES",
    "DORCHESTER",
    "FREDERICK",
    "GARRETT",
    "HARFORD",
    "HOWARD",
    "KENT",
    "MONTGOMERY",
    "PR. GEORGE",
    "QUEEN ANNE",
    "ST. MARY",
    "SOMERSET",
    "TALBOT",
    "WASHINGTON",
    "WICOMICO",
    "WORCESTER",
    "TOTAL",
}

WIDE_PARTY_COLUMN_MAP = {
    "Democratic": "total_active_registration",
    "Republican": "none_8",
    "Green": "none_9",
    "Working Class": "none_10",
    "Unaffiliated": "none_11",
    "Other": "none_12",
}


def _normalize_column_name(name: str) -> str:
    normalized = str(name).strip().lower()
    normalized = normalized.replace("%", "pct")
    normalized = "_".join(normalized.split())
    return COLUMN_ALIASES.get(normalized, normalized)


def _coerce_int_series(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(text, errors="coerce")


def _detect_county_like_column(df: pd.DataFrame) -> str | None:
    """Detect a column whose values look like county names."""
    best_col = None
    best_score = 0

    for col in df.columns:
        values = df[col].dropna().astype(str).str.strip().str.upper()
        if values.empty:
            continue

        score = 0
        for value in values.head(40):
            if any(token in value for token in KNOWN_COUNTY_TOKENS):
                score += 1

        if score > best_score:
            best_score = score
            best_col = col

    if best_score >= 3:
        return best_col
    return None


def _normalize_wide_party_layout(
    df: pd.DataFrame,
    default_year: int,
    default_month: int,
    source_url: str,
) -> pd.DataFrame | None:
    """Handle SBE wide tables where party counts are spread across columns."""
    if "county" not in df.columns:
        return None

    available = [col for col in WIDE_PARTY_COLUMN_MAP.values() if col in df.columns]
    if len(available) < 3:
        return None

    base_rows = df[df["county"].notna()].copy()
    base_rows["county"] = base_rows["county"].astype(str).str.strip()
    base_rows = base_rows[base_rows["county"].str.len() > 0]

    long_frames: list[pd.DataFrame] = []
    for party, column in WIDE_PARTY_COLUMN_MAP.items():
        if column not in base_rows.columns:
            continue

        part_df = base_rows[["county", column]].copy()
        part_df["registered"] = _coerce_int_series(part_df[column])
        part_df = part_df.drop(columns=[column]).dropna(subset=["registered"])
        part_df["party"] = party
        long_frames.append(part_df)

    if not long_frames:
        return None

    normalized = pd.concat(long_frames, ignore_index=True)
    normalized = normalized.dropna(subset=["county", "party", "registered"])
    normalized["year"] = int(default_year)
    normalized["month"] = int(default_month)
    normalized["registered"] = normalized["registered"].astype(int)

    if source_url:
        normalized["source_url"] = source_url

    columns = EXPECTED_COLUMNS + (["source_url"] if source_url else [])
    return normalized[columns]


def normalize_dataframe(
    df: pd.DataFrame,
    default_year: int = 2025,
    default_month: int = 1,
    source_url: str = "",
) -> pd.DataFrame:
    """Normalize parsed table data to the Stage 1 schema."""
    if df.empty:
        raise ValueError("Parsed data is empty")

    normalized = df.copy()
    normalized.columns = [_normalize_column_name(col) for col in normalized.columns]

    if "county" not in normalized.columns:
        county_like = _detect_county_like_column(normalized)
        if county_like:
            normalized = normalized.rename(columns={county_like: "county"})

    required_core = ["county", "party", "registered"]
    missing = [col for col in required_core if col not in normalized.columns]
    if missing:
        wide_normalized = _normalize_wide_party_layout(
            normalized,
            default_year=default_year,
            default_month=default_month,
            source_url=source_url,
        )
        if wide_normalized is not None:
            return wide_normalized
        raise ValueError(f"Missing required columns after normalization: {missing}")

    if "year" not in normalized.columns:
        normalized["year"] = default_year
    if "month" not in normalized.columns:
        normalized["month"] = default_month

    normalized["registered"] = _coerce_int_series(normalized["registered"])
    normalized = normalized.dropna(subset=["registered", "county", "party"]).copy()

    normalized["year"] = pd.to_numeric(normalized["year"], errors="coerce").fillna(default_year).astype(int)
    normalized["month"] = pd.to_numeric(normalized["month"], errors="coerce").fillna(default_month).astype(int)
    normalized["registered"] = normalized["registered"].astype(int)

    normalized["county"] = normalized["county"].astype(str).str.strip()
    normalized["party"] = normalized["party"].astype(str).str.strip()
    normalized = normalized[normalized["county"].str.upper() != "TOTAL"].copy()

    if source_url:
        normalized["source_url"] = source_url

    columns = EXPECTED_COLUMNS + (["source_url"] if "source_url" in normalized.columns else [])
    return normalized[columns]


def append_processed_data(df: pd.DataFrame, output_path: str = "data/processed/imported_voter_data.csv") -> Path:
    """Append normalized records into processed storage."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        existing = pd.read_csv(destination)
        merged = pd.concat([existing, df], ignore_index=True)
        merged.to_csv(destination, index=False)
    else:
        df.to_csv(destination, index=False)

    logger.info("Stored %s rows to %s", len(df), destination)
    return destination


def parse_and_store_pdf(
    pdf_path: str,
    source_url: str = "",
    output_path: str = "data/processed/imported_voter_data.csv",
    cache_dir: str = "data/cache/parsed_tables",
    default_year: int = 2025,
    default_month: int = 1,
) -> tuple[pd.DataFrame, Path]:
    """Parse a downloaded PDF, normalize it, and append to processed CSV."""
    pdf_file = Path(pdf_path)
    cache_path = Path(cache_dir) / f"{pdf_file.stem}.csv"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():
        logger.info("Using cached parsed table for file '%s' at '%s'", pdf_path, cache_path)
        parsed = pd.read_csv(cache_path)
    else:
        parsed = parse_pdf_tables(pdf_path)
        parsed.to_csv(cache_path, index=False)
        logger.info("Cached parsed table for file '%s' at '%s'", pdf_path, cache_path)

    normalized = normalize_dataframe(
        parsed,
        default_year=default_year,
        default_month=default_month,
        source_url=source_url,
    )
    destination = append_processed_data(normalized, output_path=output_path)
    return normalized, destination


def load_dashboard_data(
    processed_path: str = "data/processed/imported_voter_data.csv",
    fallback_path: str = "data/sample.csv",
) -> tuple[pd.DataFrame, str]:
    """Load imported data if present, otherwise fallback to sample CSV."""
    processed_file = Path(processed_path)
    if processed_file.exists():
        logger.info("Loaded dashboard data from processed file: %s", processed_file)
        return pd.read_csv(processed_file), "processed"

    logger.warning("Processed data missing; using fallback file: %s", fallback_path)
    return pd.read_csv(fallback_path), "fallback"
