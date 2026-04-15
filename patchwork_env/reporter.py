"""Human-readable report generation for validation results."""
from __future__ import annotations

from typing import List

from patchwork_env.validator import Severity, ValidationIssue, ValidationResult

_ICON = {Severity.WARNING: "⚠ ", Severity.ERROR: "✖ "}


def format_validation_report(result: ValidationResult, filename: str = "") -> str:
    """Return a formatted string report for a ValidationResult."""
    lines: List[str] = []
    header = f"Validation report{f' for {filename}' if filename else ''}"
    lines.append(header)
    lines.append("=" * len(header))

    if not result.issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    for issue in result.issues:
        icon = _ICON.get(issue.severity, "  ")
        lines.append(f"  {icon}[{issue.severity.value.upper()}] {issue.key}: {issue.message}")

    lines.append("")
    error_count = sum(1 for i in result.issues if i.severity == Severity.ERROR)
    warn_count = sum(1 for i in result.issues if i.severity == Severity.WARNING)
    summary_parts = []
    if error_count:
        summary_parts.append(f"{error_count} error(s)")
    if warn_count:
        summary_parts.append(f"{warn_count} warning(s)")
    lines.append("Summary: " + ", ".join(summary_parts))

    return "\n".join(lines)


def format_validation_summary(results: dict[str, ValidationResult]) -> str:
    """Summarise validation across multiple files."""
    lines: List[str] = ["Multi-file validation summary", "=" * 30]
    for filename, result in results.items():
        status = "OK" if result.is_valid else "FAIL"
        warn = sum(1 for i in result.issues if i.severity == Severity.WARNING)
        err = sum(1 for i in result.issues if i.severity == Severity.ERROR)
        lines.append(f"  [{status}] {filename}  (errors={err}, warnings={warn})")
    return "\n".join(lines)
