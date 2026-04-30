"""Format placeholder scan results for terminal output."""
from __future__ import annotations

from typing import List

from patchwork_env.env_placeholder import PlaceholderReport


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_placeholder_report(report: PlaceholderReport) -> str:
    lines: List[str] = []
    header = _c(1, f"Placeholder Scan — {report.filename}")
    lines.append(header)
    lines.append("=" * 50)

    if not report.has_placeholders:
        lines.append(_c(32, "  ✔ No placeholder values detected."))
        return "\n".join(lines)

    for hit in report.hits:
        key_str = _c(33, hit.key)
        pat_str = _c(31, hit.matched_pattern)
        val_preview = hit.value[:40] + ("…" if len(hit.value) > 40 else "")
        lines.append(f"  ⚠  {key_str}  =  {val_preview!r}  (matched: {pat_str})")

    return "\n".join(lines)


def format_placeholder_summary(reports: List[PlaceholderReport]) -> str:
    total_hits = sum(len(r.hits) for r in reports)
    affected = sum(1 for r in reports if r.has_placeholders)
    lines = [
        _c(1, "Placeholder Scan Summary"),
        f"  Files scanned : {len(reports)}",
        f"  Files affected: {affected}",
        f"  Total hits    : {total_hits}",
    ]
    return "\n".join(lines)
