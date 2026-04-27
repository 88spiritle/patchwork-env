"""Format an EnvDiffSummary for terminal output."""

from __future__ import annotations

from patchwork_env.env_differ_summary import EnvDiffSummary


def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI colour escape."""
    return f"\033[{code}m{text}\033[0m"


def format_diff_summary(summary: EnvDiffSummary) -> str:
    """Return a human-readable multi-line string for *summary*."""
    lines: list[str] = []
    lines.append(_c("1;34", "=== Diff Summary ==="))

    if not summary.names:
        lines.append("  No diffs recorded.")
        return "\n".join(lines)

    lines.append(f"  Pairs analysed : {len(summary.names)}")
    for name in summary.names:
        lines.append(f"    • {name}")

    lines.append("")
    lines.append(f"  {'Added':<12}: {_c('32', str(summary.total_added))}")
    lines.append(f"  {'Removed':<12}: {_c('31', str(summary.total_removed))}")
    lines.append(f"  {'Modified':<12}: {_c('33', str(summary.total_modified))}")
    lines.append(f"  {'Unchanged':<12}: {_c('90', str(summary.total_unchanged))}")
    lines.append(f"  {'Total keys':<12}: {summary.total_keys}")

    pct = round(summary.change_ratio * 100, 1)
    colour = "32" if pct == 0 else ("33" if pct < 50 else "31")
    lines.append(f"  {'Change rate':<12}: {_c(colour, f'{pct} %')}")

    return "\n".join(lines)


def format_diff_summary_oneliner(summary: EnvDiffSummary) -> str:
    """Compact single-line representation suitable for logs."""
    return (
        f"pairs={len(summary.names)} "
        f"added={summary.total_added} "
        f"removed={summary.total_removed} "
        f"modified={summary.total_modified} "
        f"unchanged={summary.total_unchanged}"
    )
