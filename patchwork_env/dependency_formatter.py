"""Format a DependencyReport for terminal output."""
from __future__ import annotations

from patchwork_env.env_dependency import DependencyReport


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_dependency_report(report: DependencyReport) -> str:
    lines: list[str] = []
    lines.append(_c("1", f"Dependency analysis — {report.filename}"))
    lines.append("")

    if not report.edges:
        lines.append(_c("32", "  ✔ No inter-key dependencies found."))
        return "\n".join(lines)

    lines.append(_c("36", f"  Resolved dependencies ({len(report.defined_edges)}):"))
    for edge in report.defined_edges:
        lines.append(
            f"    {_c('33', edge.source_key)} → {_c('32', edge.target_key)}"
        )

    if report.missing_edges:
        lines.append("")
        lines.append(_c("31", f"  Missing references ({len(report.missing_edges)}):"))
        for edge in report.missing_edges:
            lines.append(
                f"    {_c('33', edge.source_key)} → {_c('31', edge.target_key + ' [UNDEFINED]')}"
            )

    return "\n".join(lines)


def format_dependency_summary(report: DependencyReport) -> str:
    total = len(report.edges)
    missing = len(report.missing_edges)
    status = _c("31", "WARN") if missing else _c("32", "OK")
    return (
        f"[{status}] {report.filename}: "
        f"{total} edge(s), {missing} unresolved"
    )
