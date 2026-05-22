import pandas as pd

from src.logging_config import get_logger


logger = get_logger(__name__)


def validate_dataframe(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Validate that required columns exist and raise a descriptive error if not."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        missing_columns = ", ".join(missing)
        available_columns = ", ".join([str(col) for col in df.columns])
        raise ValueError(
            "Missing required column(s) "
            f"[{missing_columns}] in dataframe for analytics operation. "
            f"Available columns: [{available_columns}]"
        )


def data_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Return rows with missing, zero, or negative registration counts."""
    validate_dataframe(df, ["registered"])

    issues = df.copy()
    issues["registered_numeric"] = pd.to_numeric(issues["registered"], errors="coerce")

    missing_mask = issues["registered_numeric"].isna()
    zero_mask = issues["registered_numeric"] == 0
    negative_mask = issues["registered_numeric"] < 0

    flagged = issues[missing_mask | zero_mask | negative_mask].copy()
    if flagged.empty:
        logger.info("No data quality issues found for registration counts")
        return flagged

    flagged["quality_issue"] = ""
    flagged.loc[missing_mask.loc[flagged.index], "quality_issue"] = "missing_registered"
    flagged.loc[zero_mask.loc[flagged.index], "quality_issue"] = "zero_registered"
    flagged.loc[negative_mask.loc[flagged.index], "quality_issue"] = "negative_registered"

    logger.warning("Found %s rows with data quality issues", len(flagged))
    return flagged.drop(columns=["registered_numeric"])


def load_data(path: str) -> pd.DataFrame:
    """Load voter registration data from CSV."""
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise ValueError(f"Failed to load CSV file at path '{path}': {exc}") from exc


def total_registered(df: pd.DataFrame) -> int:
    """Return statewide total registered voters from long-form rows."""
    validate_dataframe(df, ["year", "month", "county", "party", "registered"])
    grouped = df.groupby(["year", "month", "county", "party"], as_index=False)["registered"].sum()
    return int(grouped["registered"].sum())


def party_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Return statewide totals by party."""
    validate_dataframe(df, ["party", "registered"])
    result = df.groupby("party", as_index=False)["registered"].sum()
    return result.sort_values("registered", ascending=False)


def top_counties(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top counties by total registered voters."""
    validate_dataframe(df, ["county", "registered"])
    result = df.groupby("county", as_index=False)["registered"].sum()
    return result.sort_values("registered", ascending=False).head(n)


def county_trend(df: pd.DataFrame, county: str) -> pd.DataFrame:
    """Return monthly trend for a county across all parties."""
    validate_dataframe(df, ["year", "month", "county", "registered"])
    county_df = df[df["county"] == county].copy()
    trend = county_df.groupby(["year", "month"], as_index=False)["registered"].sum()
    trend["date"] = pd.to_datetime(
        trend["year"].astype(str) + "-" + trend["month"].astype(str) + "-01"
    )
    return trend.sort_values("date")


def county_party_comparison(df: pd.DataFrame, county: str) -> pd.DataFrame:
    """Return county totals split by party."""
    validate_dataframe(df, ["county", "party", "registered"])
    county_df = df[df["county"] == county]
    result = county_df.groupby("party", as_index=False)["registered"].sum()
    return result.sort_values("registered", ascending=False)


def fastest_growing_counties(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return counties with largest absolute growth from first to last month."""
    validate_dataframe(df, ["year", "month", "county", "registered"])
    monthly = (
        df.groupby(["year", "month", "county"], as_index=False)["registered"].sum()
        .sort_values(["county", "year", "month"])
    )

    first = monthly.groupby("county", as_index=False).first().rename(columns={"registered": "start_registered"})
    last = monthly.groupby("county", as_index=False).last().rename(columns={"registered": "end_registered"})

    merged = first[["county", "start_registered"]].merge(last[["county", "end_registered"]], on="county")
    merged["growth"] = merged["end_registered"] - merged["start_registered"]
    merged["growth_pct"] = (merged["growth"] / merged["start_registered"]) * 100

    return merged.sort_values("growth", ascending=False).head(n)


def party_share_change(df: pd.DataFrame) -> pd.DataFrame:
    """Return statewide party share change from first to last month."""
    validate_dataframe(df, ["year", "month", "party", "registered"])
    monthly_party = (
        df.groupby(["year", "month", "party"], as_index=False)["registered"].sum()
        .sort_values(["year", "month"])
    )

    first_period = monthly_party[["year", "month"]].drop_duplicates().head(1).iloc[0]
    last_period = monthly_party[["year", "month"]].drop_duplicates().tail(1).iloc[0]

    first_df = monthly_party[
        (monthly_party["year"] == first_period["year"]) &
        (monthly_party["month"] == first_period["month"])
    ].copy()
    last_df = monthly_party[
        (monthly_party["year"] == last_period["year"]) &
        (monthly_party["month"] == last_period["month"])
    ].copy()

    first_total = first_df["registered"].sum()
    last_total = last_df["registered"].sum()

    first_df["share_start"] = (first_df["registered"] / first_total) * 100
    last_df["share_end"] = (last_df["registered"] / last_total) * 100

    result = first_df[["party", "share_start"]].merge(last_df[["party", "share_end"]], on="party", how="outer").fillna(0)
    result["share_change"] = result["share_end"] - result["share_start"]

    return result.sort_values("share_change", ascending=False)
