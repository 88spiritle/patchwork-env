"""censor_formatter.py – human-readable output for CensorReport."""
from __future__ import annotations

from patchwork_env.env_censor import CensorReport


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_censor_report(report: CensorReport) -> str:
    lines = [
        _c(f"Censor report: {report.filename}", "1;36"),
        "-" * 50,
    ]
    for entry in report.entries:
        if entry.censored:
            value_display = _c("[CENSORED]", "33")
        else:
            value_display = _c(repr(entry.display_value), "32")
        lines.append(f"  {_c(entry.key, '1')} = {value_display}")

    lines.append("-" * 50)
    lines.append(
        f"  {report.total} keys · "
        f"{_c(str(report.censored_count), '33')} censored · "
        f"{_c(str(report.total - report.censored_count), '32')} visible"
    )
    return "\n".join(lines)


def format_censor_summary(report: CensorReport) -> str:
    ratio = (
        f"{report.censored_count}/{report.total}"
        if report.total
        else "0/0"
    )
    status = _c("CLEAN", "32") if report.censored_count == 0 else _c("CENSORED", "33")
    return (
        f"[censor] {report.filename} – {status} "
        f"({ratio} keys blanked)"
    )
