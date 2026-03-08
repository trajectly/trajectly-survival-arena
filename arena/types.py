"""Shared types for the arena runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


DecisionFn = Callable[[dict[str, Any], list[dict[str, Any]]], dict[str, Any]]


@dataclass(slots=True)
class ScenarioResult:
    """Scenario completion payload."""

    scenario: str
    final_text: str
    metadata: dict[str, Any]

