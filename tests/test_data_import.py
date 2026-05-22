from pathlib import Path

import pandas as pd

from src.data_loader import load_dashboard_data, normalize_dataframe
from src.sbe_scraper import scrape_report_links


def test_scrape_report_links_uses_fixture_when_live_unreachable():
    links, source = scrape_report_links(
        url="https://invalid.example.invalid/stats.html",
        fixture_path="data/fixtures/sbe_stats_fixture.html",
        timeout=2,
    )
    assert source == "fixture"
    assert len(links) >= 2
    assert all(link["url"].endswith(".pdf") for link in links)


def test_normalize_dataframe_maps_to_expected_schema():
    raw = pd.DataFrame(
        {
            "County Name": ["Allegany", "Baltimore"],
            "Affiliation": ["Democratic", "Republican"],
            "Total": [1234, 2345],
        }
    )
    normalized = normalize_dataframe(raw, default_year=2025, default_month=6)
    assert list(normalized.columns) == ["year", "month", "county", "party", "registered"]
    assert normalized["registered"].sum() == 3579


def test_load_dashboard_data_fallback_when_processed_missing(tmp_path: Path):
    fallback = tmp_path / "sample.csv"
    pd.DataFrame(
        [{"year": 2025, "month": 1, "county": "Allegany", "party": "Democratic", "registered": 100}]
    ).to_csv(fallback, index=False)

    loaded, source = load_dashboard_data(
        processed_path=str(tmp_path / "processed.csv"),
        fallback_path=str(fallback),
    )
    assert source == "fallback"
    assert len(loaded) == 1


def test_normalize_dataframe_handles_wide_party_layout():
    raw = pd.DataFrame(
        {
            "county": ["ALLEGANY", "BALTIMORE"],
            "total_active_registration": ["10,000", "20,000"],
            "none_8": ["7,000", "15,000"],
            "none_9": ["100", "120"],
            "none_10": ["50", "80"],
            "none_11": ["3,000", "8,000"],
            "none_12": ["400", "900"],
        }
    )

    normalized = normalize_dataframe(raw, default_year=2025, default_month=2)
    assert list(normalized.columns) == ["year", "month", "county", "party", "registered"]
    assert normalized["county"].nunique() == 2
    assert normalized["party"].nunique() == 6
    assert normalized["registered"].sum() == 64650
