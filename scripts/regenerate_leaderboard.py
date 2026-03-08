#!/usr/bin/env python3
"""Regenerate leaderboard JSON/Markdown.

MVP behavior:
- optional upsert for a player
- deterministic sorting by score desc then player
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_PATH = ROOT / "leaderboard" / "entries.json"
MARKDOWN_PATH = ROOT / "leaderboard" / "leaderboard.md"


def _spec_count() -> int:
    return len(sorted((ROOT / "specs" / "challenges").glob("*.agent.yaml")))


def _score(entry: dict[str, Any]) -> int:
    passed = int(entry.get("scenarios_passed", 0))
    deaths = int(entry.get("deaths", 0))
    return (passed * 100) - (deaths * 10)


def _badges(score: int) -> list[str]:
    badges: list[str] = ["Seed"]
    if score >= 100:
        badges.append("Survivor")
    if score >= 300:
        badges.append("Apex")
    return badges


def _load_entries() -> list[dict[str, Any]]:
    if not ENTRIES_PATH.exists():
        return []
    payload = json.loads(ENTRIES_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("leaderboard/entries.json must contain a list")
    return [entry for entry in payload if isinstance(entry, dict)]


def _write_entries(entries: list[dict[str, Any]]) -> None:
    ENTRIES_PATH.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")


def _write_markdown(entries: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# Merge or Die Leaderboard")
    lines.append("")
    lines.append("| Rank | Player | Score | Passed | Deaths | Badges | Updated |")
    lines.append("|---:|---|---:|---:|---:|---|---|")
    for idx, entry in enumerate(entries, start=1):
        lines.append(
            "| "
            f"{idx} | "
            f"@{entry['player']} | "
            f"{entry['score']} | "
            f"{entry['scenarios_passed']} | "
            f"{entry['deaths']} | "
            f"{', '.join(entry['badges'])} | "
            f"{entry['last_updated']} |"
        )
    lines.append("")
    MARKDOWN_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--player", default="")
    parser.add_argument("--agent-path", default="agents/contenders/default.py")
    parser.add_argument("--season", default="s1")
    parser.add_argument("--scenarios-passed", type=int, default=None)
    parser.add_argument("--deaths", type=int, default=0)
    args = parser.parse_args()

    entries = _load_entries()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    player = args.player.strip().lstrip("@")
    if player:
        scenarios_passed = int(args.scenarios_passed) if args.scenarios_passed is not None else _spec_count()
        existing = None
        for entry in entries:
            if str(entry.get("player", "")).strip() == player:
                existing = entry
                break

        if existing is None:
            existing = {"player": player}
            entries.append(existing)

        existing["agent_path"] = args.agent_path
        existing["season"] = args.season
        existing["scenarios_passed"] = scenarios_passed
        existing["deaths"] = int(args.deaths)
        existing["score"] = _score(existing)
        existing["badges"] = _badges(existing["score"])
        existing["last_updated"] = now

    for entry in entries:
        entry["score"] = _score(entry)
        entry["badges"] = _badges(entry["score"])
        entry["player"] = str(entry.get("player", "unknown")).strip().lstrip("@")
        entry["agent_path"] = str(entry.get("agent_path", "agents/contenders/default.py"))
        entry["season"] = str(entry.get("season", "s1"))
        entry["scenarios_passed"] = int(entry.get("scenarios_passed", 0))
        entry["deaths"] = int(entry.get("deaths", 0))
        entry["last_updated"] = str(entry.get("last_updated", now))

    entries.sort(key=lambda item: (-int(item["score"]), str(item["player"])))
    _write_entries(entries)
    _write_markdown(entries)


if __name__ == "__main__":
    main()
