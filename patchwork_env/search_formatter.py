from __future__ import annotations

from patchwork_env.env_search import SearchResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_search_result(result: SearchResult) -> str:
    lines = []
    label = _c("1;36", f"Search results for: {result.filename}")
    lines.append(label)

    crit = result.criteria
    if crit.key_pattern:
        lines.append(f"  Key pattern  : {_c('33', crit.key_pattern)}")
    if crit.value_pattern:
        lines.append(f"  Value pattern: {_c('33', crit.value_pattern)}")
    lines.append("")

    if not result.hits:
        lines.append(_c("90", "  No matches found."))
        return "\n".join(lines)

    for hit in result.hits:
        key_part = _c("1;32", hit.entry.key) if hit.matched_key else hit.entry.key
        val = hit.entry.value or ""
        val_part = _c("1;33", val) if hit.matched_value else val
        lines.append(f"  {key_part} = {val_part}")

    lines.append("")
    lines.append(f"  {_c('1', str(result.total_hits))} match(es) found.")
    return "\n".join(lines)


def format_search_summary(result: SearchResult) -> str:
    if result.total_hits == 0:
        status = _c("90", "no matches")
    else:
        status = _c("32", f"{result.total_hits} match(es)")
    return f"{result.filename}: {status}"
