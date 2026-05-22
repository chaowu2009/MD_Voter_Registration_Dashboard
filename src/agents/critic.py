from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from src.logging_config import get_logger

logger = get_logger(__name__)


class CriticAgent:
    """Critic Agent.

    Responsibility: review code quality signals and append findings to AGENT_NOTES.
    """

    def __init__(self, notes_path: str = "AGENT_NOTES.md") -> None:
        self.notes_path = Path(notes_path)

    def _python_files(self) -> list[Path]:
        return [
            path
            for path in Path("src").rglob("*.py")
            if "__pycache__" not in path.parts
        ]

    def _function_length_findings(self, file_path: Path) -> list[str]:
        findings: list[str] = []
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception as exc:
            return [f"Could not parse {file_path}: {exc}"]

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and hasattr(node, "end_lineno"):
                start = node.lineno
                end = node.end_lineno or node.lineno
                length = end - start + 1
                if length > 30:
                    findings.append(f"Function longer than 30 lines: {file_path}:{node.name} ({length} lines)")
        return findings

    def _error_handling_findings(self, source: str, file_path: Path) -> list[str]:
        findings: list[str] = []
        if "try:" not in source and ("requests." in source or "read_csv" in source):
            findings.append(f"Potential missing error handling in {file_path}")
        return findings

    def _duplicate_line_findings(self, file_paths: list[Path]) -> list[str]:
        line_to_files: dict[str, set[str]] = {}
        findings: list[str] = []

        for file_path in file_paths:
            lines = file_path.read_text(encoding="utf-8").splitlines()
            for line in lines:
                norm = line.strip()
                if len(norm) < 40:
                    continue
                line_to_files.setdefault(norm, set()).add(str(file_path))

        for line, files in line_to_files.items():
            if len(files) > 1 and "import" not in line:
                findings.append(f"Possible duplicate logic across files {sorted(files)}: {line[:80]}")
                if len(findings) >= 5:
                    break

        return findings

    def run(self, mode: str, context: dict[str, Any] | None = None) -> list[str]:
        logger.info("CriticAgent started in mode=%s", mode)
        context = context or {}
        findings: list[str] = []

        files = self._python_files()
        for file_path in files:
            source = file_path.read_text(encoding="utf-8")
            findings.extend(self._function_length_findings(file_path))
            findings.extend(self._error_handling_findings(source, file_path))

        findings.extend(self._duplicate_line_findings(files))

        if mode == "failure":
            qa_issues = context.get("qa_issues", [])
            findings.append(f"Workflow halted due to QA failures: {qa_issues}")

        self.notes_path.parent.mkdir(parents=True, exist_ok=True)
        with self.notes_path.open("a", encoding="utf-8") as handle:
            handle.write("\n## Entry 2026-05-21 - Stage 4 critic review\n")
            handle.write(f"- Mode: {mode}\n")
            for item in findings[:15]:
                handle.write(f"- Finding: {item}\n")

        logger.info("CriticAgent completed with %s findings", len(findings))
        return findings
