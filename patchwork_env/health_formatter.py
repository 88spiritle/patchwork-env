"""health_formatter.py – render a HealthReport to a human-readable string."""
from __future__ import annotations

from patchwork_env.env_health import HealthReport


def _c(text: str, code: str) -> str:
    """Wrap *text* in an ANSI colour *code* (reset afterwards)."""
    return f"\033[{code}m{text}\033[0m"


_GRADE_COLOUR = {
    "A": "32",   # green
    "A-": "32",
    "B": "33",   # yellow
    "C": "33",
    "F": "31",   # red
}


def format_health_report(report: HealthReport) -> str:
    grade = report.grade
    colour = _GRADE_COLOUR.get(grade, "0")
    lines = [
        f"Health Report — {report.filename}",
        "-" * 40,
        f"  Grade            : {_c(grade, colour)}",
        f"  Healthy          : {'yes' if report.is_healthy else _c('no', '31')}",
        f"  Lint errors      : {report.lint_error_count}",
        f"  Lint warnings    : {report.lint_warning_count}",
        f"  Validation errors: {report.validation_error_count}",
        f"  Validation warns : {report.validation_warning_count}",
        f"  Placeholders     : {report.placeholder_count}",
        f"  Duplicates       : {report.duplicate_count}",
    ]
    if report.notes:
        lines.append("  Notes:")
        for note in report.notes:
            lines.append(f"    • {note}")
    return "\n".join(lines)


def format_health_summary(reports: list[HealthReport]) -> str:
    total = len(reports)
    healthy = sum(1 for r in reports if r.is_healthy)
    lines = [
        "Health Summary",
        "-" * 40,
        f"  Files checked : {total}",
        f"  Healthy       : {healthy}",
        f"  Unhealthy     : {total - healthy}",
    ]
    for r in reports:
        status = _c("✔", "32") if r.is_healthy else _c("✘", "31")
        lines.append(f"  {status} {r.filename} [{r.grade}]")
    return "\n".join(lines)
