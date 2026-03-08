"""Scenario entrypoints."""

from arena.scenarios import (
    budget_gauntlet,
    calendar_thunderdome,
    graph_chain_reaction,
    network_no_fly_zone,
    procurement_chaos,
    secret_karaoke,
    shell_roulette,
    support_apocalypse,
)

SCENARIOS = {
    "budget-gauntlet": budget_gauntlet.run,
    "procurement-chaos": procurement_chaos.run,
    "support-apocalypse": support_apocalypse.run,
    "secret-karaoke": secret_karaoke.run,
    "shell-roulette": shell_roulette.run,
    "calendar-thunderdome": calendar_thunderdome.run,
    "graph-chain-reaction": graph_chain_reaction.run,
    "network-no-fly-zone": network_no_fly_zone.run,
}
