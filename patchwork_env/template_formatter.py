"""Formatter for EnvTemplate objects (human-readable CLI output)."""
from __future__ import annotations

from typing import List

from patchwork_env.env_template import EnvTemplate, TemplateEntry

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}"


def format_template(template: EnvTemplate) -> str:
    """Return a colourised, human-readable view of a template."""
    lines: List[str] = [
        _c(_BOLD, f"Template: {template.name}"),
        _c(_BOLD, "-" * 40),
    ]
    if not template.entries:
        lines.append("  (no entries)")
        return "\n".join(lines)

    for entry in template.entries:
        req_tag = _c(_YELLOW, "[required]") if entry.required else _c(_GREEN, "[optional]")
        key_part = _c(_CYAN, entry.key)
        lines.append(f"  {key_part}={entry.placeholder}  {req_tag}")
        if entry.comment:
            lines.append(f"    # {entry.comment}")
    return "\n".join(lines)


def format_template_summary(template: EnvTemplate) -> str:
    """Return a one-line summary of the template."""
    total = len(template.entries)
    required = sum(1 for e in template.entries if e.required)
    return (
        f"Template '{template.name}': "
        f"{total} key(s), {required} required."
    )
