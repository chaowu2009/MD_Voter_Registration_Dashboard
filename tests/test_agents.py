import pandas as pd

from src.agents.orchestrator import run_workflow
from src.agents.qa_agent import QAAgent


def test_qa_agent_detects_bad_data_without_pytest_run():
    df = pd.DataFrame(
        [
            {"year": 2025, "month": 1, "county": "A", "party": "Democratic", "registered": 100},
            {"year": 2025, "month": 1, "county": "A", "party": "Republican", "registered": 0},
        ]
    )
    analytics_results = {
        "totals": 100,
        "party_breakdown": pd.DataFrame(
            [
                {"party": "Democratic", "registered": 100},
                {"party": "Republican", "registered": 0},
            ]
        ),
        "growth": pd.DataFrame([{"county": "A", "growth": -300, "growth_pct": -150.0}]),
        "top_counties": pd.DataFrame([{"county": "A", "registered": 100}]),
    }

    result = QAAgent().run(df, analytics_results, run_pytest=False)
    assert result["passed"] is False
    assert any("zero or negative" in issue for issue in result["issues"])
    assert any("below -100%" in issue for issue in result["issues"])


def test_orchestrator_skips_visualization_when_qa_fails(monkeypatch):
    def fake_data_run(self, report_selection="latest"):
        return pd.DataFrame(
            [
                {"year": 2025, "month": 1, "county": "A", "party": "Democratic", "registered": 10},
                {"year": 2025, "month": 1, "county": "A", "party": "Republican", "registered": 5},
            ]
        )

    def fake_qa_run(self, df, analytics_results, run_pytest=True):
        return {"passed": False, "issues": ["forced failure"], "pytest_output": ""}

    viz_called = {"value": False}

    def fake_viz_run(self, analytics_results):
        viz_called["value"] = True
        return {"party_breakdown": object()}

    def fake_critic_run(self, mode, context=None):
        return [f"critic mode={mode}"]

    monkeypatch.setattr("src.agents.data_agent.DataAgent.run", fake_data_run)
    monkeypatch.setattr("src.agents.qa_agent.QAAgent.run", fake_qa_run)
    monkeypatch.setattr("src.agents.viz_agent.VisualizationAgent.run", fake_viz_run)
    monkeypatch.setattr("src.agents.critic.CriticAgent.run", fake_critic_run)

    result = run_workflow(goal="qa failure gate test")
    assert result["status"] == "halted_by_qa"
    assert result["qa"]["passed"] is False
    assert viz_called["value"] is False
    assert result["visualizations"] == {}
