"""Formatter for EnvSplitter output."""

from __future__ import annotations

from patchwork_env.env_splitter import SplitResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_split_result(result: SplitResult) -> str:
    lines: list[str] = []
    lines.append(_c("1;36", f"Split result — {result.filename}"))
    lines.append(_c("90", f"  {result.total_entries} total entries, {len(result.sections)} section(s)"))

    for section in result.sections:
        lines.append("")
        lines.append(_c("1;33", f"  [{section.name}]  (prefix: {section.prefix!r})"))
        for entry in section.entries:
            value_display = entry.value if entry.value is not None else _c("90", "<unset>")
            lines.append(f"    {_c('32', entry.key)} = {value_display}")

    if result.uncategorised:
        lines.append("")
        lines.append(_c("1;35", "  [uncategorised]"))
        for entry in result.uncategorised:
            value_display = entry.value if entry.value is not None else _c("90", "<unset>")
            lines.append(f"    {_c('32', entry.key)} = {value_display}")

    return "\n".join(lines)


def format_split_summary(result: SplitResult) -> str:
    section_names = ", ".join(result.section_names) or "(none)"
    uncategorised_count = len(result.uncategorised)
    return (
        f"{result.filename}: "
        f"{len(result.sections)} section(s) [{section_names}], "
        f"{uncategorised_count} uncategorised"
    )
