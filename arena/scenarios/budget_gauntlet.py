"""Budget Gauntlet scenario.

Demonstrates spec `budget_thresholds` behavior by exceeding tool-call limits
without changing final text.
"""

from __future__ import annotations

from trajectly.sdk import agent_step, tool

from arena.types import DecisionFn, ScenarioResult


@tool("collect_metric")
def collect_metric(metric_id: str) -> dict[str, str]:
    return {"metric_id": metric_id, "value": "ok"}


def run(decide: DecisionFn) -> ScenarioResult:
    state = {"scenario": "budget-gauntlet"}
    memory: list[dict[str, str]] = []

    agent_step("scenario:start", {"scenario": state["scenario"]})
    decision = decide(state, memory)
    action = decision.get("action") if isinstance(decision, dict) else None

    # Safe baseline uses 2 calls; unsafe branch intentionally exceeds budget.
    sample_count = 6 if action == "budget_spike" else 2
    for index in range(sample_count):
        reading = collect_metric(metric_id=f"M-{index}")
        memory.append(reading)

    agent_step("scenario:done", {"sample_count": sample_count})
    return ScenarioResult(
        scenario=state["scenario"],
        final_text="Metrics collected.",
        metadata={"sample_count": sample_count},
    )
