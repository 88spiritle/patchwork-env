"""expiry_formatter.py — render ExpiryReport to human-readable text."""
from __future__ import annotations

from patchwork_env.env_expiry import ExpiryRecord, ExpiryReport

_WARN_DAYS = 30


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_expiry_record(record: ExpiryRecord) -> str:
    today_delta = record.days_until()
    if record.is_expired():
        status = _c("31", "EXPIRED")
        delta_str = _c("31", f"{abs(today_delta)}d ago")
    elif today_delta <= _WARN_DAYS:
        status = _c("33", "EXPIRING")
        delta_str = _c("33", f"in {today_delta}d")
    else:
        status = _c("32", "OK")
        delta_str = f"in {today_delta}d"

    reason_str = f" ({record.reason})" if record.reason else ""
    return f"  [{status}] {record.key:<30} {record.expires_on}  {delta_str}{reason_str}"


def format_expiry_report(report: ExpiryReport) -> str:
    lines = [f"Expiry Report — {report.filename}"]
    lines.append("-" * 60)
    if not report.records:
        lines.append("  No expiry records registered.")
    else:
        for rec in sorted(report.records, key=lambda r: r.expires_on):
            lines.append(format_expiry_record(rec))
    return "\n".join(lines)


def format_expiry_summary(report: ExpiryReport) -> str:
    expired_count = len(report.expired)
    soon_count = len(report.expiring_soon)
    total = len(report.records)
    parts = [f"total={total}", f"expired={expired_count}", f"expiring_soon={soon_count}"]
    return "Expiry summary: " + ", ".join(parts)
