"""CLI sub-command for placeholder scanning."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.env_placeholder import scan_placeholders
from patchwork_env.placeholder_formatter import (
    format_placeholder_report,
    format_placeholder_summary,
)


def register_placeholder_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "placeholder",
        help="Scan .env files for unfilled placeholder values.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to scan")
    p.add_argument(
        "--fail-on-hit",
        action="store_true",
        help="Exit with code 1 if any placeholder is found.",
    )
    p.set_defaults(func=cmd_placeholder)


def cmd_placeholder(args: argparse.Namespace) -> None:
    reports = []
    for path_str in args.files:
        path = Path(path_str)
        entries = parse_env_file(path)
        report = scan_placeholders(entries, filename=str(path))
        reports.append(report)
        print(format_placeholder_report(report))
        print()

    print(format_placeholder_summary(reports))

    if args.fail_on_hit and any(r.has_placeholders for r in reports):
        sys.exit(1)
