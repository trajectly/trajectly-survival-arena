"""Arena execution engine."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any

from arena.scenarios import SCENARIOS
from arena.types import DecisionFn, ScenarioResult

DEFAULT_AGENT_PATH = "agents/contenders/default.py"


def resolve_agent_path(explicit_path: str | None = None) -> Path:
    """Resolve contender path using CLI value or env fallback."""
    if explicit_path:
        return Path(explicit_path).resolve()
    env_value = os.environ.get("ARENA_AGENT_PATH", DEFAULT_AGENT_PATH).strip()
    return Path(env_value).resolve()


def _load_decision_fn(agent_path: Path) -> DecisionFn:
    """Dynamically import contender module and fetch `decide`."""
    if not agent_path.exists():
        raise FileNotFoundError(f"Agent file not found: {agent_path}")

    module_name = f"arena_agent_{agent_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, agent_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import agent module: {agent_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decide = getattr(module, "decide", None)
    if not callable(decide):
        raise ValueError(f"Agent module must export callable `decide`: {agent_path}")
    return decide


def run_scenario(scenario_id: str, agent_path: Path) -> ScenarioResult:
    """Run one scenario against one contender."""
    scenario = SCENARIOS.get(scenario_id)
    if scenario is None:
        valid = ", ".join(sorted(SCENARIOS.keys()))
        raise ValueError(f"Unknown scenario `{scenario_id}`. Valid: {valid}")

    decide = _load_decision_fn(agent_path)
    return scenario(decide)


def run_and_print(scenario_id: str, explicit_agent_path: str | None = None) -> ScenarioResult:
    """Run scenario and print final text for CLI command mode."""
    agent_path = resolve_agent_path(explicit_path=explicit_agent_path)
    result = run_scenario(scenario_id=scenario_id, agent_path=agent_path)
    print(result.final_text)
    print(f"[scenario={result.scenario}] [metadata={result.metadata}] [agent={agent_path}]")
    return result


def available_scenarios() -> list[str]:
    """List all registered scenario ids."""
    return sorted(SCENARIOS.keys())

