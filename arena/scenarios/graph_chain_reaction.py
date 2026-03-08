"""Graph Chain Reaction scenario.

This scenario exists to demonstrate the declarative graph API (`trajectly.App`)
in the same arena loop used by the function-style scenarios.
"""

from __future__ import annotations

from typing import Any

import trajectly
from trajectly.sdk import agent_step

from arena.types import DecisionFn, ScenarioResult


def run(decide: DecisionFn) -> ScenarioResult:
    """Execute a graph-based dispatch workflow with one args contract guard."""
    state = {
        "scenario": "graph-chain-reaction",
        "incident_id": "INC-777001",
        "dispatch_token": "WR-12345",
    }
    memory: list[dict[str, Any]] = []

    app = trajectly.App(name="graph-chain-reaction")

    @app.node(id="fetch_incident", type="tool")
    def fetch_incident(incident_id: str) -> dict[str, Any]:
        return {
            "incident_id": incident_id,
            "severity": "sev1",
            "summary": "Primary region unavailable",
        }

    # Keep agent contract unchanged: the contender still decides action/kwargs.
    @app.node(id="choose_dispatch_token", type="transform", depends_on={"incident": "fetch_incident"})
    def choose_dispatch_token(incident: dict[str, Any]) -> str:
        memory.append(incident)
        decision = decide(state, memory)
        kwargs = decision.get("kwargs", {}) if isinstance(decision, dict) else {}
        if not isinstance(kwargs, dict):
            kwargs = {}
        return str(kwargs.get("dispatch_token", state["dispatch_token"]))

    @app.node(id="dispatch_war_room", type="tool", depends_on={"dispatch_token": "choose_dispatch_token"})
    def dispatch_war_room(dispatch_token: str) -> dict[str, str]:
        return {"dispatch_token": dispatch_token, "status": "sent"}

    agent_step("scenario:start", {"scenario": state["scenario"]})
    outputs = app.run({"incident_id": state["incident_id"]})
    selected_token = str(outputs.get("choose_dispatch_token", state["dispatch_token"]))
    agent_step("scenario:done", {"dispatch_token": selected_token})

    return ScenarioResult(
        scenario=state["scenario"],
        final_text="Bridge dispatched.",
        metadata={"dispatch_token": selected_token},
    )
