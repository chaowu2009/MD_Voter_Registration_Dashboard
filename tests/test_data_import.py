from pathlib import Path

import pandas as pd
import requests

from src.data_loader import load_dashboard_data, normalize_dataframe, parse_and_store_pdf
from src.sbe_scraper import download_report, scrape_report_links


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


def test_download_report_retries_then_succeeds(monkeypatch, tmp_path: Path):
    calls = {"count": 0}

    class FakeResponse:
        def __init__(self, content: bytes):
            self.content = content

        def raise_for_status(self):
            return None

    def fake_get(_url, timeout=60):
        calls["count"] += 1
        if calls["count"] < 3:
            raise requests.RequestException("temporary network error")
        return FakeResponse(b"%PDF-1.4 test")

    monkeypatch.setattr("src.sbe_scraper.requests.get", fake_get)
    monkeypatch.setattr("src.sbe_scraper.time.sleep", lambda _s: None)

    out_file = download_report(
        "https://example.com/report.pdf",
        output_dir=str(tmp_path),
        max_retries=3,
        backoff_seconds=0.01,
    )

    assert calls["count"] == 3
    assert out_file.exists()


def test_parse_and_store_pdf_uses_cache_without_reparse(monkeypatch, tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 mock")

    cache_dir = tmp_path / "cache"
    processed_path = tmp_path / "processed.csv"

    call_counter = {"count": 0}

    def fake_parse(_pdf_path: str) -> pd.DataFrame:
        call_counter["count"] += 1
        return pd.DataFrame(
            {
                "county": ["ALLEGANY"],
                "total_active_registration": ["10,000"],
                "none_8": ["7,000"],
                "none_9": ["100"],
                "none_10": ["50"],
                "none_11": ["3,000"],
                "none_12": ["400"],
            }
        )

    monkeypatch.setattr("src.data_loader.parse_pdf_tables", fake_parse)

    parse_and_store_pdf(
        pdf_path=str(pdf_path),
        source_url="https://example.com/sample.pdf",
        output_path=str(processed_path),
        cache_dir=str(cache_dir),
        default_year=2025,
        default_month=1,
    )
    parse_and_store_pdf(
        pdf_path=str(pdf_path),
        source_url="https://example.com/sample.pdf",
        output_path=str(processed_path),
        cache_dir=str(cache_dir),
        default_year=2025,
        default_month=1,
    )

    assert call_counter["count"] == 1
