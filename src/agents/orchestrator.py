from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.agents.analytics_agent import AnalyticsAgent
from src.agents.critic import CriticAgent
from src.agents.data_agent import DataAgent
from src.agents.planner import PlannerAgent
from src.agents.qa_agent import QAAgent
from src.agents.viz_agent import VisualizationAgent
from src.logging_config import get_logger

logger = get_logger(__name__)


def run_workflow(goal: str = "Run multi-agent voter analytics workflow") -> dict[str, Any]:
    planner = PlannerAgent()
    data_agent = DataAgent()
    analytics_agent = AnalyticsAgent()
    qa_agent = QAAgent()
    visualization_agent = VisualizationAgent()
    critic_agent = CriticAgent()

    logger.info("Orchestrator starting")

    plan = planner.run(goal)
    logger.info("Orchestrator plan contains %s tasks", len(plan))

    data_df = data_agent.run(report_selection="latest")
    analytics_results = analytics_agent.run(data_df)
    qa_result = qa_agent.run(data_df, analytics_results, run_pytest=True)

    visualizations: dict[str, Any] = {}
    if qa_result["passed"]:
        visualizations = visualization_agent.run(analytics_results)
        critic_findings = critic_agent.run(mode="success", context={"qa": qa_result})
        status = "completed"
    else:
        critic_findings = critic_agent.run(mode="failure", context={"qa_issues": qa_result["issues"]})
        status = "halted_by_qa"

    logger.info("Orchestrator finished with status=%s", status)
    return {
        "status": status,
        "plan": plan,
        "qa": qa_result,
        "analytics": analytics_results,
        "visualizations": visualizations,
        "critic_findings": critic_findings,
    }


if __name__ == "__main__":
    result = run_workflow()
    print("Orchestrator status:", result["status"])
    print("QA passed:", result["qa"]["passed"])
    print("QA issues:", result["qa"]["issues"])
    print("Visualization keys:", list(result["visualizations"].keys()))
