"""Format sorted / grouped env entries for human-readable output."""

from __future__ import annotations

from typing import Dict, List

from patchwork_env.parser import EnvEntry

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_DIM = "\033[2m"


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}"


def format_sorted_entries(entries: List[EnvEntry], filename: str = "") -> str:
    """Render a flat sorted list of entries."""
    lines: List[str] = []
    header = f"Sorted entries{f' — {filename}' if filename else ''}"
    lines.append(_c(_BOLD, header))
    lines.append(_c(_DIM, "─" * max(len(header), 40)))
    for entry in entries:
        lines.append(f"  {_c(_CYAN, entry.key)}={entry.value}")
    lines.append("")
    lines.append(_c(_DIM, f"{len(entries)} key(s)"))
    return "\n".join(lines)


def format_grouped_entries(
    groups: Dict[str, List[EnvEntry]], filename: str = ""
) -> str:
    """Render entries grouped by prefix."""
    lines: List[str] = []
    header = f"Grouped entries{f' — {filename}' if filename else ''}"
    lines.append(_c(_BOLD, header))
    lines.append(_c(_DIM, "─" * max(len(header), 40)))
    total = 0
    for prefix, members in groups.items():
        lines.append(f"\n  {_c(_BOLD, f'[{prefix}]')}")
        for entry in members:
            lines.append(f"    {_c(_CYAN, entry.key)}={entry.value}")
        total += len(members)
    lines.append("")
    lines.append(_c(_DIM, f"{total} key(s) in {len(groups)} group(s)"))
    return "\n".join(lines)
