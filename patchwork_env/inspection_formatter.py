"""Format an :class:`InspectionReport` for terminal output."""
from __future__ import annotations

from patchwork_env.env_inspector import InspectionReport


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_inspection(report: InspectionReport) -> str:
    lines: list[str] = []
    lines.append(_c(f"=== Inspection: {report.filename} ===", "1;36"))
    lines.append(f"  Total keys    : {report.total_keys}")
    lines.append(f"  Blank lines   : {report.blank_lines}")
    lines.append(f"  Comment lines : {report.comment_lines}")

    if report.longest_key:
        lines.append(f"  Longest key   : {_c(report.longest_key, '33')}")
    if report.longest_value_key:
        lines.append(f"  Longest value : key {_c(report.longest_value_key, '33')}")

    if report.has_empty_values:
        keys = ", ".join(report.empty_values)
        lines.append(_c(f"  Empty values  : {keys}", "31"))
    else:
        lines.append(_c("  Empty values  : none", "32"))

    if report.has_duplicates:
        keys = ", ".join(report.duplicate_keys)
        lines.append(_c(f"  Duplicate keys: {keys}", "31"))
    else:
        lines.append(_c("  Duplicate keys: none", "32"))

    return "\n".join(lines)


def format_inspection_summary(reports: list[InspectionReport]) -> str:
    total_keys = sum(r.total_keys for r in reports)
    files_with_dupes = sum(1 for r in reports if r.has_duplicates)
    files_with_empty = sum(1 for r in reports if r.has_empty_values)

    lines: list[str] = [
        _c("=== Inspection Summary ===", "1;36"),
        f"  Files inspected : {len(reports)}",
        f"  Total keys      : {total_keys}",
        f"  Files w/ dupes  : {files_with_dupes}",
        f"  Files w/ empty  : {files_with_empty}",
    ]
    return "\n".join(lines)
