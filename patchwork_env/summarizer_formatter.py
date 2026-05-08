"""Format an EnvSummary for terminal output."""
from __future__ import annotations

from patchwork_env.env_summarizer import EnvSummary


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_summary(summary: EnvSummary) -> str:
    lines = [
        _c(f"Summary: {summary.filename or '(unnamed)'}", "1;36"),
        "-" * 40,
        f"  Total keys       : {summary.total_keys}",
        f"  Empty values     : {summary.empty_values}",
        f"  Commented lines  : {summary.commented_lines}",
        f"  Unique prefixes  : {len(summary.unique_prefixes)}",
    ]

    if summary.unique_prefixes:
        prefix_str = ", ".join(summary.unique_prefixes[:8])
        if len(summary.unique_prefixes) > 8:
            prefix_str += f" (+{len(summary.unique_prefixes) - 8} more)"
        lines.append(f"  Prefixes         : {prefix_str}")

    if summary.longest_key:
        lines.append(f"  Longest key      : {_c(summary.longest_key, '33')}")
    if summary.longest_value_key:
        lines.append(f"  Longest value in : {_c(summary.longest_value_key, '33')}")

    return "\n".join(lines)


def format_summary_oneliner(summary: EnvSummary) -> str:
    return (
        f"{summary.filename or '(unnamed)'}: "
        f"{summary.total_keys} keys, "
        f"{summary.empty_values} empty, "
        f"{len(summary.unique_prefixes)} prefixes"
    )
