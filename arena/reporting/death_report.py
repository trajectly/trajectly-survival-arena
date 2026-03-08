"""Death report rendering for failing Trajectly runs."""

from __future__ import annotations

from typing import Any


def _friendly_cause(code: str) -> str:
    mapping = {
        "REFINEMENT_BASELINE_CALL_MISSING": "Baseline-required behavior disappeared",
        "CONTRACT_SEQUENCE_REQUIRE_BEFORE_VIOLATED": "Operation order regression",
        "CONTRACT_ARGS_REGEX_VIOLATION": "Argument format violation",
        "DATA_LEAK_SECRET_PATTERN": "Secret leakage detected",
        "NETWORK_DOMAIN_DENIED": "Network policy violation",
    }
    return mapping.get(code, "Trajectory contract regression")


def _scenario_name(spec: str) -> str:
    lowered = spec.lower()
    if "procurement" in lowered:
        return "Budget Dragon"
    if "support" in lowered:
        return "Ticket Apocalypse"
    if "secret" in lowered:
        return "Secret Karaoke"
    if "shell" in lowered:
        return "Shell Roulette"
    if "calendar" in lowered:
        return "Calendar Thunderdome"
    return spec


def render_death_block(row: dict[str, Any]) -> str:
    """Render one compact death report block."""
    spec = str(row.get("spec", "unknown"))
    scenario = _scenario_name(spec)
    witness = row.get("trt_witness_index", "n/a")
    primary = row.get("trt_primary_violation") or {}
    if not isinstance(primary, dict):
        primary = {}
    code = str(primary.get("code", "UNKNOWN"))
    expected = primary.get("expected")
    observed = primary.get("observed")
    repro = str(row.get("repro_command", "python -m trajectly repro"))
    shrink_stats = row.get("trt_shrink_stats") or {}
    if not isinstance(shrink_stats, dict):
        shrink_stats = {}
    original_len = shrink_stats.get("original_len", "n/a")
    reduced_len = shrink_stats.get("reduced_len", "n/a")

    lines: list[str] = []
    lines.append(f"## ☠️ Agent Death Report - {scenario}")
    lines.append(f"- Cause of death: {_friendly_cause(code)}")
    lines.append(f"- Witness index: `{witness}`")
    lines.append(f"- Violated rule: `{code}`")
    lines.append(f"- Minimal failing trace summary: expected `{expected}` vs observed `{observed}`")
    lines.append(f"- Repro: `{repro}`")
    lines.append(f"- Shrink: `original_len={original_len}, reduced_len={reduced_len}`")
    lines.append("- Suggested next step: run repro, inspect witness event, then patch tool order/args.")
    lines.append("")
    return "\n".join(lines)


def render_failure_comment(latest_report: dict[str, Any]) -> str:
    """Render markdown for a failing report payload."""
    reports = latest_report.get("reports") or []
    if not isinstance(reports, list):
        reports = []

    lines: list[str] = []
    lines.append("### Merge or Die Verdict: FAIL")
    lines.append("")
    lines.append("Your agent died in CI. Final text can still look fine while behavior regresses.")
    lines.append("")
    for row in reports:
        if not isinstance(row, dict):
            continue
        if str(row.get("trt_status", "PASS")).upper() == "FAIL":
            lines.append(render_death_block(row).rstrip())
    if lines[-1] != "":
        lines.append("")
    lines.append("Try locally:")
    lines.append("- `python -m trajectly report`")
    lines.append("- `python -m trajectly repro`")
    lines.append("- `python -m trajectly shrink`")
    lines.append("")
    return "\n".join(lines)

