"""Formatter for CrossEnvReport output."""
from __future__ import annotations
from patchwork_env.env_comparer import CrossEnvReport, KeyComparison


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _row(cmp: KeyComparison) -> str:
    status = _c("32", "✔ consistent") if cmp.is_consistent else _c("31", "✘ differs")
    parts = [f"  {_c('1', cmp.key):<30} {status}"]
    for env, val in cmp.values.items():
        display = _c("33", repr(val)) if val is not None else _c("90", "(missing)")
        parts.append(f"    {env}: {display}")
    return "\n".join(parts)


def format_cross_env_report(report: CrossEnvReport) -> str:
    envs_label = ", ".join(report.env_names)
    lines = [
        _c("1;34", f"Cross-environment comparison — envs: [{envs_label}]"),
        "",
    ]
    if not report.comparisons:
        lines.append(_c("90", "  (no keys to compare)"))
        return "\n".join(lines)

    for cmp in report.comparisons:
        lines.append(_row(cmp))
        lines.append("")

    return "\n".join(lines)


def format_cross_env_summary(report: CrossEnvReport) -> str:
    total = len(report.comparisons)
    inconsistent = len(report.inconsistent_keys)
    consistent = len(report.consistent_keys)
    status = _c("32", "all consistent") if inconsistent == 0 else _c("31", f"{inconsistent} differ")
    return (
        f"Cross-env: {total} key(s) checked — "
        f"{_c('32', str(consistent))} consistent, {status}"
    )
