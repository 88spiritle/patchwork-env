"""Format ClassificationReport for terminal output."""
from __future__ import annotations

from typing import List

from patchwork_env.env_classifier import ClassificationReport, Category


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


_CATEGORY_COLOURS: dict[Category, str] = {
    Category.DATABASE: "34",      # blue
    Category.AUTH: "31",          # red
    Category.NETWORK: "36",       # cyan
    Category.LOGGING: "33",       # yellow
    Category.FEATURE_FLAG: "35",  # magenta
    Category.STORAGE: "32",       # green
    Category.MISC: "90",          # dark grey
}


def format_classification(report: ClassificationReport) -> str:
    lines: List[str] = []
    lines.append(_c("1", f"Classification Report — {report.filename or 'unknown'}"))
    lines.append("")

    by_cat = report.by_category()
    for category in Category:
        entries = by_cat.get(category, [])
        if not entries:
            continue
        colour = _CATEGORY_COLOURS[category]
        lines.append(_c(colour, f"  [{category.value.upper()}]"))
        for ce in entries:
            lines.append(f"    {ce.entry.key}")
        lines.append("")

    return "\n".join(lines)


def format_classification_summary(report: ClassificationReport) -> str:
    total = len(report.entries)
    counts = report.category_counts
    parts = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()) if v)
    return _c("1", f"{report.filename or 'env'}") + f" — {total} keys classified ({parts})"
