"""Formatting utilities for EnvProfile and ProfileRegistry."""
from __future__ import annotations

from typing import List

from patchwork_env.profiler import EnvProfile, ProfileRegistry

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}"


def format_profile(profile: EnvProfile) -> str:
    """Render a single profile as a human-readable block."""
    lines: List[str] = [
        _c(_BOLD, f"Profile: {profile.name}") + f"  [{_c(_CYAN, profile.environment)}]",
        "-" * 40,
    ]
    if not profile.overrides:
        lines.append("  (no overrides)")
    else:
        for key, value in sorted(profile.overrides.items()):
            lines.append(f"  {_c(_YELLOW, key)} = {_c(_GREEN, value)}")
    return "\n".join(lines)


def format_registry(registry: ProfileRegistry) -> str:
    """Render all profiles in the registry."""
    names = registry.list_names()
    if not names:
        return "No profiles registered."
    sections: List[str] = []
    for name in names:
        profile = registry.get(name)
        if profile is not None:
            sections.append(format_profile(profile))
    return "\n\n".join(sections)


def format_registry_summary(registry: ProfileRegistry) -> str:
    """One-line summary of the registry."""
    names = registry.list_names()
    count = len(names)
    if count == 0:
        return "Registry: 0 profiles."
    joined = ", ".join(names)
    return f"Registry: {count} profile(s) — {joined}"
