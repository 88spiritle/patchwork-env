"""requirer_formatter.py – human-readable output for RequirementReport."""
from __future__ import annotations

from patchwork_env.env_requirer import RequirementReport


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_requirement_report(report: RequirementReport) -> str:
    lines = [
        _c("1", f"Requirement check: {report.filename}"),
        "",
    ]

    for hit in report.hits:
        if hit.found:
            marker = _c("32", "✔")
            detail = _c("2", f"  (value set)")
        else:
            marker = _c("31", "✘")
            detail = _c("31", "  MISSING")
        lines.append(f"  {marker}  {hit.key}{detail}")

    lines.append("")
    if report.is_complete:
        lines.append(_c("32", "All required keys are present."))
    else:
        missing_list = ", ".join(h.key for h in report.missing)
        lines.append(_c("31", f"Missing keys ({len(report.missing)}): {missing_list}"))

    return "\n".join(lines)


def format_requirement_summary(report: RequirementReport) -> str:
    total = len(report.hits)
    ok = len(report.satisfied)
    missing = len(report.missing)
    status = _c("32", "PASS") if report.is_complete else _c("31", "FAIL")
    return (
        f"{report.filename}: [{status}] "
        f"{ok}/{total} keys present, {missing} missing"
    )
