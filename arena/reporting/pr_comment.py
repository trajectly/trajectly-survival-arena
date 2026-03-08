"""Generate PR comment markdown and labels from Trajectly report JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from arena.reporting.death_report import render_failure_comment
from arena.reporting.graduation_report import render_graduation_comment


def _sanitize_label(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return normalized[:50] or "unknown"


def _build_labels(latest_report: dict[str, Any]) -> list[str]:
    regressions = int(latest_report.get("regressions", 0))
    if regressions <= 0:
        return ["evolution:graduated"]

    reports = latest_report.get("reports") or []
    if not isinstance(reports, list):
        reports = []
    first_code = "unknown"
    for row in reports:
        if not isinstance(row, dict):
            continue
        primary = row.get("trt_primary_violation") or {}
        if not isinstance(primary, dict):
            continue
        code = str(primary.get("code", "")).strip()
        if code:
            first_code = code
            break
    return ["evolution:dead", f"cause:{_sanitize_label(first_code)}"]


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Report payload must be an object: {path}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Merge or Die PR comment markdown")
    parser.add_argument("--report-path", default=".trajectly/reports/latest.json")
    parser.add_argument("--output-markdown", default="trajectly_pr_comment.md")
    parser.add_argument("--output-meta", default="arena_pr_meta.json")
    parser.add_argument("--actor", default="")
    args = parser.parse_args()

    report_path = Path(args.report_path).resolve()
    output_markdown = Path(args.output_markdown).resolve()
    output_meta = Path(args.output_meta).resolve()

    if report_path.exists():
        latest_report = _load_json(report_path)
        regressions = int(latest_report.get("regressions", 0))
        if regressions > 0:
            body = render_failure_comment(latest_report)
            status = "FAIL"
        else:
            body = render_graduation_comment(latest_report, actor=args.actor or None)
            status = "PASS"
        labels = _build_labels(latest_report)
    else:
        body = (
            "### Merge or Die Verdict: FAIL\n\n"
            "No Trajectly report was generated. This usually means the run failed before reporting.\n"
        )
        status = "FAIL"
        labels = ["evolution:dead", "cause:report-missing"]

    marker = "<!-- merge-or-die-report -->"
    output_markdown.write_text(f"{marker}\n{body}\n", encoding="utf-8")

    meta = {"status": status, "labels": labels}
    output_meta.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
