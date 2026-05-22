from __future__ import annotations

import subprocess
import sys
from typing import Any

import pandas as pd

from src.logging_config import get_logger

logger = get_logger(__name__)


class QAAgent:
    """QA Agent.

    Responsibility: run automated tests and validate analytics consistency.
    """

    def run(
        self,
        df: pd.DataFrame,
        analytics_results: dict[str, Any],
        run_pytest: bool = True,
    ) -> dict[str, Any]:
        logger.info("QAAgent started")
        issues: list[str] = []
        pytest_output = ""

        totals = float(analytics_results["totals"])
        party_total = float(analytics_results["party_breakdown"]["registered"].sum())
        county_total = float(df.groupby("county", as_index=False)["registered"].sum()["registered"].sum())

        if abs(totals - party_total) > 1e-6:
            issues.append("Totals mismatch between analytics totals and party breakdown sum")

        if abs(totals - county_total) > 1e-6:
            issues.append("Totals mismatch between analytics totals and county totals sum")

        party_df = analytics_results["party_breakdown"].copy()
        if totals > 0:
            pct_sum = ((party_df["registered"] / totals) * 100).sum()
            if abs(float(pct_sum) - 100.0) > 0.1:
                issues.append("Party percentages do not sum to 100% within tolerance")

        if (df["registered"] <= 0).any():
            issues.append("Detected county rows with zero or negative registrations")

        growth_df = analytics_results["growth"]
        if "growth_pct" in growth_df.columns and (growth_df["growth_pct"] < -100).any():
            issues.append("Detected impossible county growth rates below -100%")

        if run_pytest:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                capture_output=True,
                text=True,
                check=False,
            )
            pytest_output = (proc.stdout + "\n" + proc.stderr).strip()
            if proc.returncode != 0:
                issues.append("pytest command reported failures")

        passed = len(issues) == 0
        logger.info("QAAgent finished: passed=%s, issue_count=%s", passed, len(issues))
        return {"passed": passed, "issues": issues, "pytest_output": pytest_output}
