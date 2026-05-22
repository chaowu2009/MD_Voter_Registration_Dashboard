from __future__ import annotations

import plotly.express as px

from src.logging_config import get_logger

logger = get_logger(__name__)


class VisualizationAgent:
    """Visualization Agent.

    Responsibility: create plotly figures from analytics outputs.
    """

    def run(self, analytics_results: dict[str, object]) -> dict[str, object]:
        logger.info("VisualizationAgent started")

        party_df = analytics_results["party_breakdown"]
        growth_df = analytics_results["growth"]

        party_fig = px.bar(
            party_df,
            x="party",
            y="registered",
            title="Statewide Party Breakdown",
        )
        growth_fig = px.bar(
            growth_df,
            x="county",
            y="growth",
            title="Fastest Growing Counties",
        )

        figures = {
            "party_breakdown": party_fig,
            "growth": growth_fig,
        }
        logger.info("VisualizationAgent created %s figures", len(figures))
        return figures
