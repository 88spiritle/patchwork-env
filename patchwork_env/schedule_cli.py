"""schedule_cli.py — CLI sub-command for scheduled env overrides."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from patchwork_env.env_scheduler import Schedule, ScheduledOverride
from patchwork_env.schedule_formatter import format_schedule, format_schedule_summary


def _load_schedule(path: str) -> Schedule:
    try:
        with open(path) as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return Schedule(name=path)
    overrides = [
        ScheduledOverride(
            key=o["key"],
            value=o["value"],
            start=datetime.fromisoformat(o["start"]),
            end=datetime.fromisoformat(o["end"]) if o.get("end") else None,
            label=o.get("label", ""),
        )
        for o in data.get("overrides", [])
    ]
    return Schedule(name=data.get("name", path), overrides=overrides)


def _save_schedule(schedule: Schedule, path: str) -> None:
    data = {
        "name": schedule.name,
        "overrides": [
            {
                "key": o.key,
                "value": o.value,
                "start": o.start.isoformat(),
                "end": o.end.isoformat() if o.end else None,
                "label": o.label,
            }
            for o in schedule.overrides
        ],
    }
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def register_schedule_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("schedule", help="manage scheduled env overrides")
    p.add_argument("--file", default=".patchwork_schedule.json", help="schedule store path")
    p.add_argument("--summary", action="store_true", help="show summary only")
    p.set_defaults(func=cmd_schedule)


def cmd_schedule(args: argparse.Namespace) -> int:
    schedule = _load_schedule(args.file)
    at = datetime.utcnow()
    if getattr(args, "summary", False):
        print(format_schedule_summary(schedule, at))
    else:
        print(format_schedule(schedule, at))
    return 0
