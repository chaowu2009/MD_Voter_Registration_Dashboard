import pandas as pd

from src.analytics import (
    county_party_comparison,
    county_trend,
    fastest_growing_counties,
    party_breakdown,
    party_share_change,
    top_counties,
    total_registered,
)


def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"year": 2025, "month": 1, "county": "Allegany", "party": "Democratic", "registered": 1000},
            {"year": 2025, "month": 1, "county": "Allegany", "party": "Republican", "registered": 900},
            {"year": 2025, "month": 1, "county": "Allegany", "party": "Unaffiliated", "registered": 400},
            {"year": 2025, "month": 2, "county": "Allegany", "party": "Democratic", "registered": 1010},
            {"year": 2025, "month": 2, "county": "Allegany", "party": "Republican", "registered": 905},
            {"year": 2025, "month": 2, "county": "Allegany", "party": "Unaffiliated", "registered": 410},
            {"year": 2025, "month": 1, "county": "Baltimore", "party": "Democratic", "registered": 2200},
            {"year": 2025, "month": 1, "county": "Baltimore", "party": "Republican", "registered": 1800},
            {"year": 2025, "month": 1, "county": "Baltimore", "party": "Unaffiliated", "registered": 700},
            {"year": 2025, "month": 2, "county": "Baltimore", "party": "Democratic", "registered": 2240},
            {"year": 2025, "month": 2, "county": "Baltimore", "party": "Republican", "registered": 1810},
            {"year": 2025, "month": 2, "county": "Baltimore", "party": "Unaffiliated", "registered": 730},
        ]
    )


def test_total_registered():
    df = sample_df()
    assert total_registered(df) == 14105


def test_party_breakdown_has_expected_columns():
    df = sample_df()
    result = party_breakdown(df)
    assert list(result.columns) == ["party", "registered"]
    assert result["registered"].sum() == 14105


def test_top_counties_sorted_desc():
    df = sample_df()
    result = top_counties(df, n=2)
    assert len(result) == 2
    assert result.iloc[0]["registered"] >= result.iloc[1]["registered"]


def test_county_trend_returns_dates():
    df = sample_df()
    result = county_trend(df, "Allegany")
    assert "date" in result.columns
    assert len(result) == 2


def test_county_party_comparison_single_county():
    df = sample_df()
    result = county_party_comparison(df, "Baltimore")
    assert set(result["party"]) == {"Democratic", "Republican", "Unaffiliated"}


def test_fastest_growing_counties_has_growth_columns():
    df = sample_df()
    result = fastest_growing_counties(df, n=2)
    assert "growth" in result.columns
    assert "growth_pct" in result.columns


def test_party_share_change_has_required_columns():
    df = sample_df()
    result = party_share_change(df)
    assert list(result.columns) == ["party", "share_start", "share_end", "share_change"]
