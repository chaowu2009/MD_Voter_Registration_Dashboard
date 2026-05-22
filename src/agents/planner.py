from __future__ import annotations

from src.logging_config import get_logger

logger = get_logger(__name__)


class PlannerAgent:
    """Planner Agent.

    Responsibility: break a high-level workflow goal into ordered sub-tasks
    and assign each task to the responsible agent.
    """

    def run(self, goal: str) -> list[dict[str, object]]:
        logger.info("PlannerAgent starting with goal: %s", goal)
        plan = [
            {
                "task": "Collect and normalize voter registration data",
                "agent": "DataAgent",
                "input": {"report_selection": "latest"},
            },
            {
                "task": "Compute statewide and county analytics",
                "agent": "AnalyticsAgent",
                "input": {"dataframe": "from DataAgent"},
            },
            {
                "task": "Run test and consistency checks",
                "agent": "QAAgent",
                "input": {"dataframe": "from DataAgent", "analytics": "from AnalyticsAgent"},
            },
            {
                "task": "Build dashboard charts",
                "agent": "VisualizationAgent",
                "input": {"analytics": "from AnalyticsAgent"},
            },
            {
                "task": "Review code quality findings",
                "agent": "CriticAgent",
                "input": {"mode": "success-or-failure"},
            },
        ]
        logger.info("PlannerAgent generated %s tasks", len(plan))
        return plan
