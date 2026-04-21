"""schedule_formatter.py — render Schedule and ScheduledOverride objects."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from patchwork_env.env_scheduler import Schedule, ScheduledOverride


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_override(override: ScheduledOverride, at: Optional[datetime] = None) -> str:
    status = "ACTIVE" if override.is_active(at) else "inactive"
    colour = 32 if status == "ACTIVE" else 90
    end_s = override.end.isoformat() if override.end else "∞"
    label_s = f"  [{override.label}]" if override.label else ""
    return (
        f"  {_c(colour, status):>10}  {_c(1, override.key)}={override.value}"
        f"  ({override.start.isoformat()} → {end_s}){label_s}"
    )


def format_schedule(schedule: Schedule, at: Optional[datetime] = None) -> str:
    lines = [_c(1, f"Schedule: {schedule.name}")]
    if not schedule.overrides:
        lines.append("  (no overrides scheduled)")
        return "\n".join(lines)
    for override in schedule.overrides:
        lines.append(format_override(override, at))
    return "\n".join(lines)


def format_schedule_summary(schedule: Schedule, at: Optional[datetime] = None) -> str:
    total = len(schedule.overrides)
    active = len(schedule.active_overrides(at))
    return (
        f"Schedule '{schedule.name}': {total} override(s), "
        f"{_c(32, str(active))} active"
    )
