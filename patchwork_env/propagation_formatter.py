"""Formatter for PropagationResult objects."""
from __future__ import annotations

from patchwork_env.env_propagator import PropagationResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_propagation_result(result: PropagationResult) -> str:
    """Return a human-readable report of a propagation run."""
    lines: list[str] = []
    lines.append(_c("1", f"Propagation from: {result.source_file}"))
    lines.append("-" * 50)

    if not result.records:
        lines.append(_c("33", "  No keys were propagated."))
        return "\n".join(lines)

    for rec in result.records:
        action = _c("33", "overwrite") if rec.overwritten else _c("32", "add")
        old_hint = f"  (was: {rec.old_value!r})" if rec.overwritten else ""
        lines.append(
            f"  [{action}] {_c('36', rec.key)} -> {rec.target_file}"
            f"  =  {rec.new_value!r}{old_hint}"
        )

    lines.append("-" * 50)
    lines.append(
        f"  Total: {result.total_propagated} propagated  "
        f"({result.total_added} added, {result.total_overwritten} overwritten)"
    )
    return "\n".join(lines)


def format_propagation_summary(results: list[PropagationResult]) -> str:
    """Return a one-line summary across multiple propagation results."""
    total = sum(r.total_propagated for r in results)
    added = sum(r.total_added for r in results)
    overwritten = sum(r.total_overwritten for r in results)
    targets = len(results)
    return (
        _c("1", "Propagation summary") + f": {targets} target(s), "
        f"{total} key(s) propagated "
        f"({_c('32', str(added))} added, {_c('33', str(overwritten))} overwritten)"
    )
