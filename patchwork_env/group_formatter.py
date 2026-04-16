"""Format grouped .env entries for terminal display."""
from __future__ import annotations
from typing import Dict, List
from patchwork_env.env_grouper import EntryGroup, flat_sorted_groups

try:
    from colorama import Fore, Style
    def _c(text: str, color: str) -> str:
        return color + text + Style.RESET_ALL
except ImportError:
    def _c(text: str, color: str) -> str:  # type: ignore
        return text


def format_group(group: EntryGroup) -> str:
    lines: List[str] = []
    header = _c(f"[{group.label}]", Fore.CYAN if 'Fore' in dir() else "")
    lines.append(header)
    for entry in group.entries:
        if entry.key is None:
            continue
        value_display = entry.raw_value if entry.raw_value is not None else ""
        lines.append(f"  {_c(entry.key, Fore.GREEN if 'Fore' in dir() else '')}={value_display}")
    return "\n".join(lines)


def format_all_groups(groups: Dict[str, EntryGroup], filename: str = "") -> str:
    lines: List[str] = []
    title = f"Grouped entries"
    if filename:
        title += f" — {filename}"
    lines.append(_c(title, Fore.YELLOW if 'Fore' in dir() else ""))
    lines.append("=" * max(len(title), 40))
    for group in flat_sorted_groups(groups):
        lines.append("")
        lines.append(format_group(group))
    return "\n".join(lines)


def format_group_summary(groups: Dict[str, EntryGroup]) -> str:
    total = sum(len(g.entries) for g in groups.values())
    lines = [f"{len(groups)} group(s), {total} total entry/entries."]
    for label, group in sorted(groups.items()):
        lines.append(f"  {label}: {len(group.entries)}")
    return "\n".join(lines)
