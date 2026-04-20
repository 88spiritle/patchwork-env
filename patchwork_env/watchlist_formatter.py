"""Formatter for watchlist scan reports."""
from __future__ import annotations

from patchwork_env.env_watchlist import WatchReport


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_watch_report(report: WatchReport) -> str:
    lines = []
    lines.append(_c("1", f"Watchlist scan: {report.filename}"))
    lines.append("")

    if report.hits:
        lines.append(_c("32", f"  Found ({len(report.hits)}):"))
        for hit in report.hits:
            note_str = f"  # {hit.note}" if hit.note else ""
            lines.append(f"    {_c('36', hit.key)} = {hit.entry.value}{note_str}")
    else:
        lines.append(_c("33", "  No watched keys found."))

    lines.append("")

    if report.misses:
        lines.append(_c("31", f"  Missing ({len(report.misses)}):"))
        for key in report.misses:
            lines.append(f"    {_c('33', key)}")
    else:
        lines.append(_c("32", "  All watched keys are present."))

    return "\n".join(lines)


def format_watch_summary(report: WatchReport) -> str:
    total = len(report.hits) + len(report.misses)
    found = len(report.hits)
    missing = len(report.misses)
    status = _c("32", "OK") if missing == 0 else _c("31", "MISSING KEYS")
    return (
        f"Watchlist [{report.filename}]: "
        f"{found}/{total} keys found — {status}"
    )
