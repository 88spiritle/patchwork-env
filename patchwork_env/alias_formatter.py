"""alias_formatter.py — human-readable output for alias reports."""
from __future__ import annotations

from patchwork_env.env_aliaser import AliasReport


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_alias_report(report: AliasReport) -> str:
    lines = [
        _c(1, f"Alias Report — {report.filename}"),
        "",
    ]

    resolved = report.resolved()
    if resolved:
        lines.append(_c(36, "  Resolved aliases:"))
        for alias, canonical, value in resolved:
            lines.append(
                f"    {_c(33, alias)} -> {_c(32, canonical)}  "
                f"value={_c(90, repr(value))}"
            )
    else:
        lines.append(_c(90, "  No alias hits found."))

    missing = report.missing_canonicals()
    if missing:
        lines.append("")
        lines.append(_c(31, "  Missing canonical keys:"))
        for key in missing:
            lines.append(f"    {_c(31, key)}")

    return "\n".join(lines)


def format_alias_summary(report: AliasReport) -> str:
    resolved = report.resolved()
    missing = report.missing_canonicals()
    total_registered = sum(
        len(r.aliases) for r in report.registry.records.values()
    )
    parts = [
        f"{total_registered} alias(es) registered",
        f"{len(resolved)} resolved",
        f"{len(missing)} canonical key(s) missing",
    ]
    return "Alias summary: " + " | ".join(parts)
