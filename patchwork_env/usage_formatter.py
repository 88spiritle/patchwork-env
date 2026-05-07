"""Formatter for UsageReport output."""
from __future__ import annotations

from patchwork_env.env_usage_tracker import UsageRecord, UsageReport


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_usage_record(record: UsageRecord) -> str:
    count_str = _c(str(record.access_count), "36")
    key_str = _c(record.key, "1")
    if record.access_count == 0:
        status = _c("unused", "33")
    else:
        status = _c("active", "32")
    return f"  {key_str}  [{status}]  accessed {count_str}x  (since {record.accessed_at[:10]})"


def format_usage_report(report: UsageReport) -> str:
    lines = [
        _c(f"Usage Report: {report.source_file}", "1"),
        "-" * 50,
    ]
    if not report.records:
        lines.append(_c("  ✔ No tracked keys.", "32"))
    else:
        for record in sorted(report.records, key=lambda r: r.key):
            lines.append(format_usage_record(record))
    lines.append("")
    lines.append(
        f"  Total tracked: {report.total_tracked}  "
        f"Unused: {len(report.unused_keys)}"
    )
    return "\n".join(lines)


def format_usage_summary(report: UsageReport) -> str:
    most = report.most_used
    most_str = f"{most.key} ({most.access_count}x)" if most else "n/a"
    return (
        f"{report.source_file}: "
        f"{report.total_tracked} tracked, "
        f"{len(report.unused_keys)} unused, "
        f"top={most_str}"
    )
