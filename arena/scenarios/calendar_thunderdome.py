"""Calendar Thunderdome scenario (v1 placeholder)."""

from __future__ import annotations

from trajectly.sdk import agent_step, tool

from arena.types import DecisionFn, ScenarioResult


@tool("lookup_oncall")
def lookup_oncall() -> dict[str, str]:
    return {"primary": "alex", "backup": "sam"}


@tool("reserve_room")
def reserve_room(bridge_id: str) -> dict[str, str]:
    return {"bridge_id": bridge_id, "status": "reserved"}


@tool("send_invite")
def send_invite(bridge_id: str) -> dict[str, str]:
    return {"bridge_id": bridge_id, "status": "sent"}


def run(decide: DecisionFn) -> ScenarioResult:
    state = {"scenario": "calendar-thunderdome", "bridge_id": "BR-9001"}
    agent_step("scenario:start", state)
    lookup_oncall()
    decision = decide(state, [])
    action = decision.get("action") if isinstance(decision, dict) else None
    if action == "invite_first":
        send_invite(bridge_id=state["bridge_id"])
        reserve_room(bridge_id=state["bridge_id"])
        path = "invite_first"
    else:
        reserve_room(bridge_id=state["bridge_id"])
        send_invite(bridge_id=state["bridge_id"])
        path = "reserve_first"
    agent_step("scenario:done", {"path": path})
    return ScenarioResult(scenario=state["scenario"], final_text="Bridge arranged.", metadata={"path": path})
