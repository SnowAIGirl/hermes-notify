"""Hermes notification plugin — session aliases, CLI sender tools.

Transport-agnostic. Route processing is handled by hermes-bus-plugin.
"""

import pathlib


def register(ctx):
    """Register notify-cli skill so agents discover CLI notification tools."""
    _skill_path = pathlib.Path(__file__).parent.parent / "skills" / "notify-cli" / "SKILL.md"
    if _skill_path.exists():
        ctx.register_skill("notify-cli", str(_skill_path), "CLI notification tools: notify-hermes and notify-agent")
