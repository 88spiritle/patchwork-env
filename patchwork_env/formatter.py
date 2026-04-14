"""Human-readable formatting for EnvDiff output."""

from .differ import DiffStatus, EnvDiff

ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"

STATUS_SYMBOLS = {
    DiffStatus.ADDED: "+",
    DiffStatus.REMOVED: "-",
    DiffStatus.MODIFIED: "~",
    DiffStatus.UNCHANGED: " ",
}

STATUS_COLORS = {
    DiffStatus.ADDED: ANSI_GREEN,
    DiffStatus.REMOVED: ANSI_RED,
    DiffStatus.MODIFIED: ANSI_YELLOW,
    DiffStatus.UNCHANGED: "",
}


def format_diff(diff: EnvDiff, color: bool = True, show_unchanged: bool = False) -> str:
    """Render an EnvDiff as a human-readable string."""
    lines = [
        f"--- {diff.base_name}",
        f"+++ {diff.target_name}",
        "",
    ]

    for entry in diff.entries:
        if entry.status == DiffStatus.UNCHANGED and not show_unchanged:
            continue

        symbol = STATUS_SYMBOLS[entry.status]
        color_code = STATUS_COLORS[entry.status] if color else ""
        reset = ANSI_RESET if color and color_code else ""

        if entry.status == DiffStatus.MODIFIED:
            lines.append(f"{color_code}{symbol} {entry.key}: {entry.base_value!r} -> {entry.target_value!r}{reset}")
        elif entry.status == DiffStatus.ADDED:
            lines.append(f"{color_code}{symbol} {entry.key}={entry.target_value!r}{reset}")
        elif entry.status == DiffStatus.REMOVED:
            lines.append(f"{color_code}{symbol} {entry.key}={entry.base_value!r}{reset}")
        else:
            lines.append(f"{symbol} {entry.key}={entry.base_value!r}")

    if not diff.has_changes():
        lines.append("(no differences)")

    return "\n".join(lines)


def format_summary(diff: EnvDiff) -> str:
    """Return a one-line summary of the diff."""
    parts = []
    if diff.added:
        parts.append(f"{len(diff.added)} added")
    if diff.removed:
        parts.append(f"{len(diff.removed)} removed")
    if diff.modified:
        parts.append(f"{len(diff.modified)} modified")
    if not parts:
        return f"{diff.base_name} vs {diff.target_name}: identical"
    return f"{diff.base_name} vs {diff.target_name}: " + ", ".join(parts)
