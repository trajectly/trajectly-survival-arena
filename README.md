# Merge or Die

Your agent can pass a demo and still fail the workflow.
This repo is a small GitHub-native game that makes that failure visible with Trajectly.

In this arena, each PR is an evolution attempt:
- pass Trajectly gates -> evolve
- fail Trajectly gates -> death report with witness index, violated rule, repro command, and shrink stats

## Why this exists

Final-answer checks can miss important regressions:
- skipped required tool calls
- bad tool-call order
- unsafe tools
- malformed arguments

Trajectly catches those using trajectory-level checks over deterministic replay.

## Scenarios

- `procurement-chaos` (Budget Dragon)
- `support-apocalypse` (Ticket Apocalypse)
- `secret-karaoke` (Secret Karaoke)
- `shell-roulette` (Shell Roulette)
- `calendar-thunderdome` (Calendar Thunderdome)

All scenarios are deterministic, local, and do not require API keys.

## Quickstart

```bash
python -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m trajectly --version
./.venv/bin/python -m trajectly init
PATH="$PWD/.venv/bin:$PATH" ./.venv/bin/python -m trajectly run specs/challenges/*.agent.yaml --project-root .
./.venv/bin/python -m trajectly report
```

If a run fails:

```bash
./.venv/bin/python -m trajectly repro
./.venv/bin/python -m trajectly shrink
```

## Intentional regression demo

Run with the unsafe demo contender to see trajectory-level failure:

```bash
PATH="$PWD/.venv/bin:$PATH" ARENA_AGENT_PATH=agents/contenders/unsafe_demo.py ./.venv/bin/python -m trajectly run specs/challenges/*.agent.yaml --project-root .
./.venv/bin/python -m trajectly report
PATH="$PWD/.venv/bin:$PATH" ARENA_AGENT_PATH=agents/contenders/unsafe_demo.py ./.venv/bin/python -m trajectly repro
PATH="$PWD/.venv/bin:$PATH" ARENA_AGENT_PATH=agents/contenders/unsafe_demo.py ./.venv/bin/python -m trajectly shrink
```

Typical failure cues:
- `trt: FAIL (witness=...)`
- primary violation such as `REFINEMENT_BASELINE_CALL_MISSING`
- reproducible command in report output

## Play loop

1. Copy `agents/template_agent.py` to `agents/contenders/<your_handle>.py`.
2. Run locally with your agent path:
   - `PATH="$PWD/.venv/bin:$PATH" ARENA_AGENT_PATH=agents/contenders/<your_handle>.py ./.venv/bin/python -m trajectly run specs/challenges/*.agent.yaml --project-root .`
3. Open a PR.
4. CI posts a pass/fail comment and uploads `.trajectly/**` artifacts.

## Repo map

```text
agents/                   player and reference agents
arena/                    scenario runtime + reporting helpers
specs/challenges/         Trajectly specs
contracts/                scenario rules
leaderboard/              markdown/json scoreboard
scripts/                  leaderboard and card helpers
.github/workflows/        CI gates and leaderboard updates
```

## Notes

- Baselines and fixtures are committed for deterministic CI.
- Dynamic outputs (`.trajectly/reports`, `.trajectly/repros`, `.trajectly/current/*.run.jsonl`) are ignored.
- Baseline pointers in `.trajectly/current/*.json` are committed.
