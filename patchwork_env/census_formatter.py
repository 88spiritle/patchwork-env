"""census_formatter.py – human-readable output for CensusReport."""
from __future__ import annotations

from patchwork_env.env_census import CensusReport, CensusRow


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_census_row(row: CensusRow) -> str:
    status = _c("32", "consistent") if row.is_consistent else _c("31", "inconsistent")
    sources = ", ".join(row.sources)
    values_preview = " | ".join(repr(v) for v in row.unique_values[:3])
    if len(row.unique_values) > 3:
        values_preview += " ..."
    lines = [
        f"  {_c('1', row.key)}  [{status}]  occurrences={row.occurrences}",
        f"    values : {values_preview}",
        f"    sources: {sources}",
    ]
    return "\n".join(lines)


def format_census(report: CensusReport) -> str:
    header = _c("1;34", f"Census Report — {len(report.filenames)} file(s)")
    file_list = "  " + "  ".join(report.filenames)
    rows_text = "\n".join(format_census_row(r) for r in report.rows) if report.rows else "  (no entries found)"
    sep = "-" * 60
    return "\n".join([
        header,
        file_list,
        sep,
        rows_text,
        sep,
        f"  total keys  : {report.total_keys}",
        f"  consistent  : {len(report.consistent_keys)}",
        f"  inconsistent: {len(report.inconsistent_keys)}",
    ])


def format_census_summary(report: CensusReport) -> str:
    if not report.inconsistent_keys:
        status = _c("32", "✔ all keys consistent")
    else:
        keys = ", ".join(r.key for r in report.inconsistent_keys[:5])
        status = _c("31", f"✘ inconsistent keys: {keys}")
    return (
        f"Census: {report.total_keys} keys across "
        f"{len(report.filenames)} file(s) — {status}"
    )
