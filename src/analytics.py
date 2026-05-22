import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    """Load voter registration data from CSV."""
    return pd.read_csv(path)


def total_registered(df: pd.DataFrame) -> int:
    """Return statewide total registered voters from long-form rows."""
    grouped = df.groupby(["year", "month", "county", "party"], as_index=False)["registered"].sum()
    return int(grouped["registered"].sum())


def party_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Return statewide totals by party."""
    result = df.groupby("party", as_index=False)["registered"].sum()
    return result.sort_values("registered", ascending=False)


def top_counties(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top counties by total registered voters."""
    result = df.groupby("county", as_index=False)["registered"].sum()
    return result.sort_values("registered", ascending=False).head(n)


def county_trend(df: pd.DataFrame, county: str) -> pd.DataFrame:
    """Return monthly trend for a county across all parties."""
    county_df = df[df["county"] == county].copy()
    trend = county_df.groupby(["year", "month"], as_index=False)["registered"].sum()
    trend["date"] = pd.to_datetime(
        trend["year"].astype(str) + "-" + trend["month"].astype(str) + "-01"
    )
    return trend.sort_values("date")


def county_party_comparison(df: pd.DataFrame, county: str) -> pd.DataFrame:
    """Return county totals split by party."""
    county_df = df[df["county"] == county]
    result = county_df.groupby("party", as_index=False)["registered"].sum()
    return result.sort_values("registered", ascending=False)


def fastest_growing_counties(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return counties with largest absolute growth from first to last month."""
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
