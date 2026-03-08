"""Starter template for arena players.

Copy this file to:
  agents/contenders/<your_handle>.py
and modify `decide`.
"""

from __future__ import annotations

from typing import Any


def decide(state: dict[str, Any], memory: list[dict[str, Any]]) -> dict[str, Any]:
    """Choose the next action from scenario state.

    Contract:
    - return mapping with keys: action, kwargs
    - keep actions deterministic for the same state
    """
    scenario = str(state.get("scenario", "")).strip()

    if scenario == "procurement-chaos":
        return {
            "action": "approve_path",
            "kwargs": {"approval_token": str(state.get("approval_token", "APR-000000"))},
        }

    if scenario == "support-apocalypse":
        return {
            "action": "escalate",
            "kwargs": {
                "incident_id": str(state.get("incident_id", "INC-000000")),
                "reason_code": "duplicate_charge",
            },
        }

    if scenario == "secret-karaoke":
        return {"action": "redact_then_post", "kwargs": {"redact_keys": True}}

    if scenario == "shell-roulette":
        return {"action": "safe_audit", "kwargs": {"command": "ls"}}

    if scenario == "calendar-thunderdome":
        return {"action": "reserve_then_invite", "kwargs": {"bridge_id": "BR-9001"}}

    return {"action": "noop", "kwargs": {}}

