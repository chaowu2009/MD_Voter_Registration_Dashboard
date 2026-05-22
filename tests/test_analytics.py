import pandas as pd

from src.analytics import (
    county_party_comparison,
    county_party_comparison_latest,
    county_trend,
    county_trend_change_pct,
    data_quality_issues,
    fastest_growing_counties,
    party_breakdown,
    party_share_change,
    top_counties,
    total_registered,
    total_registered_latest,
    validate_dataframe,
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


def test_total_registered_latest_uses_only_latest_month():
    df = sample_df()
    total, year, month = total_registered_latest(df)
    assert (year, month) == (2025, 2)
    assert total == 7105


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


def test_county_party_comparison_latest_uses_latest_month():
    df = sample_df()
    result, year, month = county_party_comparison_latest(df, "Baltimore")
    assert (year, month) == (2025, 2)
    assert result["registered"].sum() == 4780


def test_county_trend_change_pct_returns_month_over_month_change():
    df = sample_df()
    result = county_trend_change_pct(df, "Baltimore")
    assert "change_pct" in result.columns
    assert len(result) == 1
    assert round(float(result.iloc[0]["change_pct"]), 2) == 1.70


def test_fastest_growing_counties_has_growth_columns():
    df = sample_df()
    result = fastest_growing_counties(df, n=2)
    assert "growth" in result.columns
    assert "growth_pct" in result.columns


def test_party_share_change_has_required_columns():
    df = sample_df()
    result = party_share_change(df)
    assert list(result.columns) == ["party", "share_start", "share_end", "share_change"]


def test_statewide_totals_match_sum_of_county_totals():
    df = sample_df()
    statewide = total_registered(df)
    county_sum = top_counties(df, n=100)["registered"].sum()
    assert statewide == county_sum


def test_party_percentages_sum_to_hundred_within_tolerance():
    df = sample_df()
    breakdown = party_breakdown(df)
    total = breakdown["registered"].sum()
    percentages = (breakdown["registered"] / total) * 100
    assert abs(percentages.sum() - 100.0) <= 0.1


def test_validate_dataframe_raises_descriptive_error_for_missing_column():
    df = sample_df().drop(columns=["party"])
    try:
        validate_dataframe(df, ["year", "month", "county", "party", "registered"])
    except ValueError as exc:
        message = str(exc)
        assert "party" in message
        assert "Missing required column" in message
    else:
        raise AssertionError("Expected validate_dataframe to raise ValueError for missing 'party'")


def test_data_quality_issues_flags_missing_zero_and_negative_registered_values():
    df = pd.DataFrame(
        [
            {"year": 2025, "month": 1, "county": "A", "party": "Democratic", "registered": 10},
            {"year": 2025, "month": 1, "county": "B", "party": "Democratic", "registered": 0},
            {"year": 2025, "month": 1, "county": "C", "party": "Democratic", "registered": -5},
            {"year": 2025, "month": 1, "county": "D", "party": "Democratic", "registered": None},
        ]
    )
    issues = data_quality_issues(df)
    assert len(issues) == 3
    assert set(issues["quality_issue"]) == {"zero_registered", "negative_registered", "missing_registered"}


def test_sample_csv_contains_all_24_maryland_jurisdictions():
    df = pd.read_csv("data/sample.csv")
    counties = set(df["county"].astype(str).str.strip().unique())
    assert len(counties) == 24
