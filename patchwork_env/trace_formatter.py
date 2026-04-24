"""Formatter for TraceReport output."""
from __future__ import annotations

from typing import List

from patchwork_env.env_tracer import TraceRecord, TraceReport


def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI colour *code*."""
    return f"\033[{code}m{text}\033[0m"


def format_trace_record(record: TraceRecord) -> str:
    """Return a human-readable block for a single TraceRecord."""
    lines: List[str] = []
    status = (
        _c("31", "CONFLICT")
        if record.is_conflicted
        else _c("32", "ok")
    )
    lines.append(f"  {_c('1', record.key)}  [{status}]")
    for src, val in zip(record.sources, record.values):
        lines.append(f"    {_c('36', src)}: {val}")
    return "\n".join(lines)


def format_trace_report(report: TraceReport) -> str:
    """Return the full formatted trace report string."""
    lines: List[str] = []
    header = "Trace Report — " + ", ".join(report.file_names)
    lines.append(_c("1;34", header))
    lines.append("-" * len(header))

    for key in sorted(report.records):
        lines.append(format_trace_record(report.records[key]))

    return "\n".join(lines)


def format_trace_summary(report: TraceReport) -> str:
    """Return a one-line summary of the trace report."""
    total = len(report.records)
    conflicts = len(report.conflicted_keys)
    unique = len(report.unique_keys)
    return (
        f"Traced {total} key(s) across {len(report.file_names)} file(s): "
        f"{_c('32', str(unique))} unique, "
        f"{_c('31', str(conflicts))} conflicted."
    )
