"""CLI for running Merge or Die scenarios."""

from __future__ import annotations

import argparse

from arena.engine import available_scenarios, run_and_print


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Merge or Die scenario")
    parser.add_argument("command", nargs="?", default="run", choices=["run", "list"])
    parser.add_argument("--scenario", required=False, choices=available_scenarios())
    parser.add_argument(
        "--agent",
        default=None,
        help="Path to contender agent file. Defaults to ARENA_AGENT_PATH or agents/contenders/default.py",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "list":
        for scenario in available_scenarios():
            print(scenario)
        return
    if not args.scenario:
        parser.error("--scenario is required when command is run")
    run_and_print(scenario_id=args.scenario, explicit_agent_path=args.agent)


if __name__ == "__main__":
    main()
