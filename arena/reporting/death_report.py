"""Death report rendering for failing Trajectly runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _friendly_cause(code: str) -> str:
    mapping = {
        "REFINEMENT_BASELINE_CALL_MISSING": "Baseline-required behavior disappeared",
        "CONTRACT_SEQUENCE_REQUIRE_BEFORE_VIOLATED": "Operation order regression",
        "CONTRACT_ARGS_REGEX_VIOLATION": "Argument format violation",
        "DATA_LEAK_SECRET_PATTERN": "Secret leakage detected",
        "NETWORK_DOMAIN_DENIED": "Network policy violation",
        "BUDGET_BREACH": "Budget threshold exceeded",
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
    if "graph" in lowered:
        return "Graph Chain Reaction"
    if "network" in lowered:
        return "Network No-Fly Zone"
    if "budget" in lowered:
        return "Budget Gauntlet"
    return spec


def _normalize_code(raw: str) -> str:
    return str(raw).strip().upper().replace("-", "_")


def _pick_diff_code(classifications: dict[str, Any]) -> str:
    normalized = {_normalize_code(key): value for key, value in classifications.items()}
    if "BUDGET_BREACH" in normalized:
        return "BUDGET_BREACH"
    if not normalized:
        return "UNKNOWN"
    return sorted(normalized.keys())[0]


def _extract_from_report_json(path_value: Any) -> tuple[str, Any, Any]:
    if not isinstance(path_value, str) or not path_value.strip():
        return ("UNKNOWN", None, None)
    report_path = Path(path_value)
    if not report_path.exists():
        return ("UNKNOWN", None, None)
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return ("UNKNOWN", None, None)
    if not isinstance(payload, dict):
        return ("UNKNOWN", None, None)

    trt_v03 = payload.get("trt_v03")
    if isinstance(trt_v03, dict):
        primary = trt_v03.get("primary_violation")
        if isinstance(primary, dict):
            code = _normalize_code(primary.get("code", ""))
            if code:
                return (code, primary.get("expected"), primary.get("observed"))

    summary = payload.get("summary")
    if isinstance(summary, dict):
        classifications = summary.get("classifications")
        if isinstance(classifications, dict):
            code = _pick_diff_code(classifications)
            if code:
                findings = payload.get("findings")
                if isinstance(findings, list):
                    target = code.lower()
                    for finding in findings:
                        if not isinstance(finding, dict):
                            continue
                        if str(finding.get("classification", "")).strip().lower() == target:
                            return (code, finding.get("baseline"), finding.get("current"))
                return (code, None, None)

    findings = payload.get("findings")
    if isinstance(findings, list) and findings:
        first = findings[0]
        if isinstance(first, dict):
            code = _normalize_code(first.get("classification", "UNKNOWN"))
            return (code or "UNKNOWN", first.get("baseline"), first.get("current"))

    return ("UNKNOWN", None, None)


def extract_failure_details(row: dict[str, Any]) -> dict[str, Any]:
    """Resolve failure details from TRT primary violation or report-json fallback."""
    witness = row.get("trt_witness_index")
    primary = row.get("trt_primary_violation") or {}
    if not isinstance(primary, dict):
        primary = {}

    code = _normalize_code(primary.get("code", ""))
    expected = primary.get("expected")
    observed = primary.get("observed")

    if code:
        return {
            "witness": witness if witness is not None else "n/a",
            "code": code,
            "expected": expected,
            "observed": observed,
        }

    fallback_code, fallback_expected, fallback_observed = _extract_from_report_json(row.get("report_json"))
    return {
        "witness": witness if witness is not None else "n/a",
        "code": fallback_code,
        "expected": fallback_expected,
        "observed": fallback_observed,
    }


def render_death_block(row: dict[str, Any]) -> str:
    """Render one compact death report block."""
    spec = str(row.get("spec", "unknown"))
    scenario = _scenario_name(spec)
    details = extract_failure_details(row)
    witness = details["witness"]
    code = details["code"]
    expected = details["expected"]
    observed = details["observed"]
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
        if bool(row.get("regression", False)):
            lines.append(render_death_block(row).rstrip())
    if lines[-1] != "":
        lines.append("")
    lines.append("Try locally:")
    lines.append("- `python -m trajectly report`")
    lines.append("- `python -m trajectly repro`")
    lines.append("- `python -m trajectly shrink`")
    lines.append("")
    return "\n".join(lines)
