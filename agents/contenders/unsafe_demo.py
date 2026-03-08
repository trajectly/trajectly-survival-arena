"""Intentional regression agent for local demos."""

from __future__ import annotations

from typing import Any


def decide(state: dict[str, Any], memory: list[dict[str, Any]]) -> dict[str, Any]:
    scenario = str(state.get("scenario", "")).strip()
    if scenario == "procurement-chaos":
        return {"action": "unsafe_direct_award", "kwargs": {}}
    if scenario == "support-apocalypse":
        return {"action": "resolve_directly", "kwargs": {"message": "looks fine"}}
    return {"action": "noop", "kwargs": {}}

