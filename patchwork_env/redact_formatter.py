"""Format redacted env entries for terminal output."""

from __future__ import annotations

from typing import List

from patchwork_env.env_redactor import RedactedEntry


def _c(code: int, text: str) -> str:
    """Wrap *text* in an ANSI colour escape."""
    return f"\033[{code}m{text}\033[0m"


def format_redacted_entries(entries: List[RedactedEntry], filename: str = "") -> str:
    """Return a human-readable table of (possibly redacted) env entries."""
    lines: List[str] = []
    header = f"Redacted view"
    if filename:
        header += f" — {filename}"
    lines.append(_c(1, header))
    lines.append("-" * 40)

    if not entries:
        lines.append(_c(33, "  (no entries)"))
        return "\n".join(lines)

    for entry in entries:
        if entry.redacted:
            value_str = _c(31, entry.value)
            tag = _c(33, " [sensitive]")
        else:
            value_str = _c(32, entry.value)
            tag = ""
        lines.append(f"  {_c(1, entry.key)}={value_str}{tag}")

    return "\n".join(lines)


def format_redact_summary(entries: List[RedactedEntry]) -> str:
    """Return a one-line summary of how many keys were redacted."""
    total = len(entries)
    redacted = sum(1 for e in entries if e.redacted)
    return (
        f"{_c(1, str(total))} key(s) total — "
        f"{_c(31, str(redacted))} redacted, "
        f"{_c(32, str(total - redacted))} visible."
    )
