from __future__ import annotations

import pandas as pd

from src.analytics import (
    fastest_growing_counties,
    party_breakdown,
    party_share_change,
    top_counties,
    total_registered,
    validate_dataframe,
)
from src.logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsAgent:
    """Analytics Agent.

    Responsibility: run analytical computations and return structured results.
    """

    def run(self, df: pd.DataFrame) -> dict[str, object]:
        logger.info("AnalyticsAgent started with %s rows", len(df))
        validate_dataframe(df, ["year", "month", "county", "party", "registered"])

        results: dict[str, object] = {
            "totals": total_registered(df),
            "party_breakdown": party_breakdown(df),
            "growth": fastest_growing_counties(df, n=10),
            "top_counties": top_counties(df, n=10),
            "party_share_change": party_share_change(df),
        }
        logger.info("AnalyticsAgent completed calculations")
        return results
