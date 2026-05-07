"""CLI subcommand for env key usage tracking."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from patchwork_env.env_usage_tracker import UsageTracker
from patchwork_env.parser import parse_env_file
from patchwork_env.usage_formatter import format_usage_report, format_usage_summary


def register_usage_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("usage", help="Track and report env key usage")
    p.add_argument("env_file", help="Path to .env file")
    p.add_argument(
        "--access",
        metavar="KEY",
        action="append",
        default=[],
        help="Mark KEY as accessed (can be repeated)",
    )
    p.add_argument("--summary", action="store_true", help="One-line summary output")
    p.add_argument("--json", dest="as_json", action="store_true", help="JSON output")
    p.set_defaults(func=cmd_usage)


def cmd_usage(args: argparse.Namespace) -> int:
    path = Path(args.env_file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    entries = parse_env_file(str(path))
    tracker = UsageTracker()

    for entry in entries:
        tracker.track(entry.key, str(path))

    for key in args.access:
        tracker.track(key, str(path))

    report = tracker.report(str(path))

    if args.as_json:
        data = {"source_file": report.source_file, "records": [r.to_dict() for r in report.records]}
        print(json.dumps(data, indent=2))
    elif args.summary:
        print(format_usage_summary(report))
    else:
        print(format_usage_report(report))

    return 0
