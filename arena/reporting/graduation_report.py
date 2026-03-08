"""Graduation comment rendering for successful runs."""

from __future__ import annotations

from typing import Any


def render_graduation_comment(latest_report: dict[str, Any], actor: str | None = None) -> str:
    """Render markdown for all-passing results."""
    reports = latest_report.get("reports") or []
    if not isinstance(reports, list):
        reports = []

    lines: list[str] = []
    lines.append("### Merge or Die Verdict: PASS")
    lines.append("")
    if actor:
        lines.append(f"Agent `@{actor}` evolved successfully.")
    else:
        lines.append("Agent evolved successfully.")
    lines.append("")
    lines.append("Passed scenarios:")
    for row in reports:
        if not isinstance(row, dict):
            continue
        spec = str(row.get("spec", "unknown"))
        status = str(row.get("trt_status", "PASS")).upper()
        lines.append(f"- `{spec}` -> `{status}`")
    lines.append("")
    lines.append("Graduation certificate:")
    lines.append("- Tier: `Survivor`")
    lines.append("- Next objective: beat the weekly cursed challenge")
    lines.append("")
    return "\n".join(lines)

