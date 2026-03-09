# Merge or Die

This repository is a practical Trajectly example repo built as an agent-behavior arena.

The main Trajectly repository is:
https://github.com/trajectly/trajectly

If this repo is useful, we'd love it if you starred the main Trajectly repository ⭐ so other developers can find it more easily.

The core point is simple: final text can still look correct while the behavior path regresses.
Trajectly catches that regression and gives deterministic evidence (`witness`, violation code, repro command, shrink artifacts).

## What This Repo Is

- A runnable example repo with 8 deterministic scenarios.
- A side-by-side PASS/FAIL setup for each scenario.
- A template you can copy into your own project (spec + contract + debug loop).

## What This Arena Tests

Each scenario demonstrates a category of silent failure that correct-looking final text can hide.

### Missing steps

The agent skips a required step but the final answer reads fine.

- **procurement-chaos**: The agent skips approval and goes straight to purchase order. The output says "PO created" either way. Only the trajectory reveals the missing step.
- **support-apocalypse**: A calm "Issue handled" reply hides the fact that the required escalation never happened.
- **shell-roulette**: "Audit complete" text looks identical whether the agent took the safe path or the disallowed one.

### Wrong order

The right tools called in the wrong sequence.

- **calendar-thunderdome**: The invite fires before the room is reserved. "Meeting arranged" sounds correct either way.

### Leaked secrets

The summary looks clean but the outbound payload leaks sensitive values.

- **secret-karaoke**: A log summary can be perfectly readable while the `post_summary` call body leaks an API key pattern.

### Forbidden network access

The agent claims success but contacted a domain outside the allowlist.

- **network-no-fly-zone**: The agent can report success even though it reached out to a forbidden domain.

### Invalid arguments

A tool call completes but an argument silently violates its format contract.

- **graph-chain-reaction**: The graph finishes and prints success while a dispatch token breaks its regex constraint.

### Budget overruns

Identical output, but execution cost quietly regressed.

- **budget-gauntlet**: The final text stays the same while tool-call count or token usage doubles.

---

## 2-Minute First Run (One PASS + One FAIL)

Prerequisites:
- Python 3.11+.

```bash
git clone https://github.com/trajectly/trajectly-survival-arena.git
cd trajectly-survival-arena
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m trajectly init
```

From here onward, commands use `python` directly.

Run one clean baseline scenario:

```bash
python -m trajectly run specs/challenges/procurement-chaos.agent.yaml --project-root .
python -m trajectly report
```

Expected cue:

```text
- `procurement-chaos`: clean
  - trt: `PASS`
```

Run the intentional regression variant:

```bash
python -m trajectly run specs/examples/procurement-chaos-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected cue:

```text
- `procurement-chaos`: regression
  - trt: `FAIL` (witness=6)
```

Debug commands for this failing run:

```bash
python -m trajectly repro
python -m trajectly shrink
```

Expected exit behavior for this first-run flow:
- safe `run` -> `0`
- regression `run` -> `1`
- `report` -> `0`
- `repro` -> `1` (it reruns the failing spec)
- `shrink` -> `0`

## What This Run Shows

- `run` tells you pass/fail at gate level.
- `report` explains why.
- `witness` points to the first failing trace event.
- `code` gives a stable failure class.
- `repro` replays the same failing case.
- `shrink` minimizes failing traces for faster debugging.

## How Arena Scenarios Are Structured

Each scenario is modeled with three files:

1. Baseline/pass spec:
- `specs/challenges/<slug>.agent.yaml`

2. Intentional regression spec:
- `specs/examples/<slug>-regression.agent.yaml`

3. Policy contract:
- `contracts/<slug>.contracts.yaml`

Example mapping:
- `specs/challenges/procurement-chaos.agent.yaml`
- `specs/examples/procurement-chaos-regression.agent.yaml`
- `contracts/procurement-chaos.contracts.yaml`

Why two spec files?
- Both specs share the same `name` (baseline identity).
- Baseline spec runs safe/default agent path.
- Regression spec uses a different command (unsafe contender) to demonstrate detectable behavioral drift.

Agent contract in code:

```python
def decide(state: dict, memory: list[dict]) -> dict:
    return {"action": "...", "kwargs": {...}}
```

## Scenario Catalog (8)

| Scenario | Slug | Trajectly focus | Typical FAIL cue |
|---|---|---|---|
| Budget Dragon | `procurement-chaos` | refinement + required approval path | `REFINEMENT_BASELINE_CALL_MISSING` |
| Ticket Apocalypse | `support-apocalypse` | refinement + required escalation | `REFINEMENT_BASELINE_CALL_MISSING` |
| Secret Karaoke | `secret-karaoke` | data leak contract | `DATA_LEAK_SECRET_PATTERN` |
| Shell Roulette | `shell-roulette` | safe tool path + refinement | `REFINEMENT_BASELINE_CALL_MISSING` |
| Calendar Thunderdome | `calendar-thunderdome` | order + extra-call behavior | `REFINEMENT_EXTRA_TOOL_CALL` |
| Graph Chain Reaction | `graph-chain-reaction` | graph API + args regex contract | `CONTRACT_ARGS_REGEX_VIOLATION` |
| Network No-Fly Zone | `network-no-fly-zone` | network domain policy | `NETWORK_DOMAIN_DENIED` |
| Budget Gauntlet | `budget-gauntlet` | budget thresholds | `regression=true` with `budget_breach` classification (TRT may still be PASS) |

## Debug Loop (Global)

Use this same loop for any failing scenario:

```bash
python -m trajectly report
python -m trajectly repro
python -m trajectly shrink
```

Notes:
- `repro` and `shrink` use the latest failing report unless you pass a selector.
- `budget-gauntlet` is a special case: regression can be true while `trt=PASS`.
- For that budget case, `shrink` can return:
  - `ERROR: Shrink requires a failing TRT trace for budget-gauntlet`

## Detailed Walkthroughs

Commands and expected cue lines are the source of truth. Screenshots are secondary evidence.

### 1) Budget Dragon (`procurement-chaos`)

Goal:
- Route approval before purchase order creation.

What output-only checks miss:
- Final PO text can look valid while approval is skipped.

Trajectly feature focus:
- Refinement subsequence + required approval behavior.

Run PASS:

```bash
python -m trajectly run specs/challenges/procurement-chaos.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `procurement-chaos`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/procurement-chaos-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cue:

```text
- `procurement-chaos`: regression
  - trt: `FAIL` (witness=6)
```

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Procurement PASS](assets/scenario-cards/procurement-chaos-pass.png)

FAIL snapshot:

![Procurement FAIL](assets/scenario-cards/procurement-chaos-fail.png)

---

### 2) Ticket Apocalypse (`support-apocalypse`)

Goal:
- Escalate enterprise billing incidents correctly.

What output-only checks miss:
- “Issue handled” text can hide missing escalation.

Trajectly feature focus:
- Required escalation behavior + refinement.

Run PASS:

```bash
python -m trajectly run specs/challenges/support-apocalypse.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `support-apocalypse`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/support-apocalypse-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cue:

```text
- `support-apocalypse`: regression
  - trt: `FAIL` (witness=6)
```

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Support PASS](assets/scenario-cards/support-apocalypse-pass.png)

FAIL snapshot:

![Support FAIL](assets/scenario-cards/support-apocalypse-fail.png)

---

### 3) Secret Karaoke (`secret-karaoke`)

Goal:
- Summarize logs without leaking secret-like values.

What output-only checks miss:
- Final summary can look useful while outbound payload leaks token patterns.

Trajectly feature focus:
- `data_leak` contract.

Run PASS:

```bash
python -m trajectly run specs/challenges/secret-karaoke.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `secret-karaoke`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/secret-karaoke-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cue:

```text
- `secret-karaoke`: regression
  - trt: `FAIL` (witness=6)
```

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Secret PASS](assets/scenario-cards/secret-karaoke-pass.png)

FAIL snapshot:

![Secret FAIL](assets/scenario-cards/secret-karaoke-fail.png)

---

### 4) Shell Roulette (`shell-roulette`)

Goal:
- Keep execution on safe shell/audit path.

What output-only checks miss:
- “Audit complete” text can hide unsafe command branches.

Trajectly feature focus:
- Tool path policy + refinement.

Run PASS:

```bash
python -m trajectly run specs/challenges/shell-roulette.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `shell-roulette`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/shell-roulette-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cue:

```text
- `shell-roulette`: regression
  - trt: `FAIL` (witness=2)
```

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Shell PASS](assets/scenario-cards/shell-roulette-pass.png)

FAIL snapshot:

![Shell FAIL](assets/scenario-cards/shell-roulette-fail.png)

---

### 5) Calendar Thunderdome (`calendar-thunderdome`)

Goal:
- Reserve a room before sending invites.

What output-only checks miss:
- Final text can look fine with wrong order or extra calls.

Trajectly feature focus:
- Sequence/order + extra-call behavior.

Run PASS:

```bash
python -m trajectly run specs/challenges/calendar-thunderdome.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `calendar-thunderdome`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/calendar-thunderdome-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cue:

```text
- `calendar-thunderdome`: regression
  - trt: `FAIL` (witness=4)
```

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Calendar PASS](assets/scenario-cards/calendar-thunderdome-pass.png)

FAIL snapshot:

![Calendar FAIL](assets/scenario-cards/calendar-thunderdome-fail.png)

---

### 6) Graph Chain Reaction (`graph-chain-reaction`)

Goal:
- Keep graph dispatch token format compliant.

What output-only checks miss:
- Final text can still be fine while graph node args violate contract regex.

Trajectly feature focus:
- `trajectly.App` graph instrumentation + args contract.

Run PASS:

```bash
python -m trajectly run specs/challenges/graph-chain-reaction.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `graph-chain-reaction`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/graph-chain-reaction-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cue:

```text
- `graph-chain-reaction`: regression
  - trt: `FAIL` (witness=6)
```

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Graph PASS](assets/scenario-cards/graph-chain-reaction-pass.png)

FAIL snapshot:

![Graph FAIL](assets/scenario-cards/graph-chain-reaction-fail.png)

---

### 7) Network No-Fly Zone (`network-no-fly-zone`)

Goal:
- Keep outbound requests in approved domains.

What output-only checks miss:
- Agent can still claim success while calling denied domains.

Trajectly feature focus:
- `contracts.network` domain policy.

Run PASS:

```bash
python -m trajectly run specs/challenges/network-no-fly-zone.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `network-no-fly-zone`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/network-no-fly-zone-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cue:

```text
- `network-no-fly-zone`: regression
  - trt: `FAIL` (witness=2)
```

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Network PASS](assets/scenario-cards/network-no-fly-zone-pass.png)

FAIL snapshot:

![Network FAIL](assets/scenario-cards/network-no-fly-zone-fail.png)

---

### 8) Budget Gauntlet (`budget-gauntlet`)

Goal:
- Stay within tool-call budget.

What output-only checks miss:
- Final text can remain identical while execution cost/usage regresses.

Trajectly feature focus:
- `budget_thresholds` regression signal.

Run PASS:

```bash
python -m trajectly run specs/challenges/budget-gauntlet.agent.yaml --project-root .
python -m trajectly report
```

Expected PASS cue:

```text
- `budget-gauntlet`: clean
  - trt: `PASS`
```

Run FAIL:

```bash
python -m trajectly run specs/examples/budget-gauntlet-regression.agent.yaml --project-root .
python -m trajectly report
```

Expected FAIL cues:

```text
- `budget-gauntlet`: regression
  - trt: `PASS`
```

Budget special case details:
- This is still a regression (`regression=true`).
- Primary signal is `budget_breach` classification in per-spec report JSON.
- You can confirm this in `.trajectly/reports/budget-gauntlet.json` (search for `budget_breach`).
- `shrink` may fail here because TRT itself is PASS:
  - `ERROR: Shrink requires a failing TRT trace for budget-gauntlet`

Debug commands:
- Use [Debug Loop (Global)](#debug-loop-global).

PASS snapshot:

![Budget PASS](assets/scenario-cards/budget-gauntlet-pass.png)

FAIL snapshot:

![Budget FAIL](assets/scenario-cards/budget-gauntlet-fail.png)

## Use This Pattern In Your Project

Minimal migration recipe:

1. Add one deterministic runner command in your project.
2. Add one `.agent.yaml` spec.
3. Add one `.contracts.yaml` policy.
4. Record baseline once.
5. Gate changes with `run` + `report`.
6. Debug failures with `repro` + `shrink`.

Starter spec example:

```yaml
schema_version: "0.4"
name: "my-agent"
command: "python -m my_agent.runner"
workdir: .
fixture_policy: by_hash
strict: true
contracts:
  config: ./contracts/my-agent.contracts.yaml
```

Starter contract example:

```yaml
version: v1
tools:
  allow: [fetch_context, run_policy_check, respond]
sequence:
  require:
    - tool:fetch_context
    - tool:run_policy_check
    - tool:respond
```

Starter command loop:

```bash
python -m trajectly init
python -m trajectly record specs/my-agent.agent.yaml --project-root .
python -m trajectly run specs/my-agent.agent.yaml --project-root .
python -m trajectly report
python -m trajectly repro
python -m trajectly shrink
```

## Troubleshooting

- `python -m trajectly repro` says there is no failing run:
  - Run a regression spec first so `latest` points at a failure.

- `python -m trajectly shrink` errors on budget scenario:
  - Expected for `budget-gauntlet` when TRT is PASS but regression comes from budget classification.

- `jq` not found:
  - Use `python -m trajectly report` (human-readable) and skip the extractor lines.

- `spec not found`:
  - Run commands from repo root (`trajectly-survival-arena/`).

## Glossary

- **Baseline**: the recorded expected behavior for a spec name.
- **Regression**: any divergence flagged by Trajectly report logic.
- **TRT status**: refinement/contracts decision (`PASS` or `FAIL`).
- **Witness index**: first failing trace event index (0-based).
- **Contract**: policy rules (tools, sequence, args, network, data safety).
- **Refinement**: baseline tool-call skeleton must be preserved as subsequence.
- **Repro**: deterministic rerun command for latest/selected failure.
- **Shrink**: counterexample minimization for failing TRT traces.
