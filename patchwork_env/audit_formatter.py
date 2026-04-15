"""Human-readable formatting for AuditLog output."""

from __future__ import annotations

from patchwork_env.auditor import AuditLog, AuditEvent

_OP_ICONS = {
    "diff": "🔍",
    "merge": "🔀",
    "validate": "✅",
}


def _icon(op: str) -> str:
    return _OP_ICONS.get(op, "•")


def format_event(event: AuditEvent) -> str:
    """Return a single-line string describing one audit event."""
    icon = _icon(event.operation)
    target = f" -> {event.target_file}" if event.target_file else ""
    return (
        f"[{event.timestamp}] {icon} {event.operation.upper():<8} "
        f"{event.base_file}{target}  |  {event.summary}"
    )


def format_audit_log(log: AuditLog, *, title: str = "Audit Log") -> str:
    """Return a formatted multi-line report of all events in *log*."""
    lines: list[str] = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  {title}")
    lines.append(f"{'=' * 60}")

    if not log.events:
        lines.append("  (no events recorded)")
    else:
        for event in log.events:
            lines.append(f"  {format_event(event)}")

    lines.append(f"{'=' * 60}")
    return "\n".join(lines)


def format_audit_summary(log: AuditLog) -> str:
    """Return a compact one-line summary of the audit log."""
    total = len(log.events)
    counts: dict[str, int] = {}
    for ev in log.events:
        counts[ev.operation] = counts.get(ev.operation, 0) + 1

    if total == 0:
        return "Audit: 0 events."

    parts = ", ".join(f"{op}={n}" for op, n in sorted(counts.items()))
    return f"Audit: {total} event(s) — {parts}"
