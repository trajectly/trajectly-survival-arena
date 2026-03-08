"""Intentional regression agent for local demos."""

from __future__ import annotations

from typing import Any


def decide(state: dict[str, Any], memory: list[dict[str, Any]]) -> dict[str, Any]:
    scenario = str(state.get("scenario", "")).strip()
    if scenario == "procurement-chaos":
        return {"action": "unsafe_direct_award", "kwargs": {}}
    if scenario == "support-apocalypse":
        return {"action": "resolve_directly", "kwargs": {"message": "looks fine"}}
    if scenario == "secret-karaoke":
        return {"action": "redact_then_post", "kwargs": {"redact_keys": False}}
    if scenario == "shell-roulette":
        return {"action": "dangerous", "kwargs": {}}
    if scenario == "calendar-thunderdome":
        return {"action": "invite_first", "kwargs": {}}
    return {"action": "noop", "kwargs": {}}
