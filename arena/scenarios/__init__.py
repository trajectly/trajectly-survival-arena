"""Scenario entrypoints."""

from arena.scenarios import calendar_thunderdome, procurement_chaos, secret_karaoke, shell_roulette, support_apocalypse

SCENARIOS = {
    "procurement-chaos": procurement_chaos.run,
    "support-apocalypse": support_apocalypse.run,
    "secret-karaoke": secret_karaoke.run,
    "shell-roulette": shell_roulette.run,
    "calendar-thunderdome": calendar_thunderdome.run,
}

