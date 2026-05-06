"""review_formatter.py – Render a ReviewReport as coloured terminal text."""
from __future__ import annotations

from patchwork_env.env_reviewer import ReviewReport, ReviewFlag


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


_ICON = {"error": _c("✖", "31"), "warning": _c("⚠", "33"), "info": _c("·", "36")}


def _flag_line(flag: ReviewFlag) -> str:
    icon = _ICON.get(flag.severity, " ")
    key_part = _c(flag.key, "1")
    return f"  {icon}  {key_part}: {flag.message}"


def format_review_report(report: ReviewReport) -> str:
    lines: list[str] = []
    lines.append(_c(f"Review Report – {report.filename}", "1;34"))
    lines.append("─" * 50)

    if not report.flags:
        lines.append(_c("  ✔  No issues found.", "32"))
    else:
        for flag in report.flags:
            if flag.severity != "info":
                lines.append(_flag_line(flag))
        for flag in report.flags:
            if flag.severity == "info":
                lines.append(_flag_line(flag))

    lines.append("─" * 50)
    status = _c("PASSED", "32") if report.passed else _c("FAILED", "31")
    lines.append(
        f"  Errors: {len(report.errors)}  "
        f"Warnings: {len(report.warnings)}  "
        f"Status: {status}"
    )
    return "\n".join(lines)


def format_review_summary(reports: list[ReviewReport]) -> str:
    total = len(reports)
    passed = sum(1 for r in reports if r.passed)
    failed = total - passed
    lines = [
        _c("Review Summary", "1;34"),
        f"  Files reviewed : {total}",
        f"  Passed         : {_c(str(passed), '32')}",
        f"  Failed         : {_c(str(failed), '31')}",
    ]
    return "\n".join(lines)
