"""CLI sub-command: patchwork-env select"""
from __future__ import annotations

import argparse
import sys

from patchwork_env.parser import EnvEntry
from patchwork_env.env_selector import SelectionCriteria, select_entries
from patchwork_env.selector_formatter import (
    format_selection_result,
    format_selection_summary,
)


def _read_entries(path: str) -> list[EnvEntry]:
    from patchwork_env.parser import parse_env_file  # type: ignore[attr-defined]
    return parse_env_file(path)


def register_selector_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("select", help="Select env entries by criteria")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Exact key names")
    p.add_argument("--prefix", metavar="PREFIX", help="Key prefix filter")
    p.add_argument("--suffix", metavar="SUFFIX", help="Key suffix filter")
    p.add_argument(
        "--has-value",
        choices=["yes", "no"],
        help="Filter by whether value is set",
    )
    p.add_argument("--value-contains", metavar="STR", help="Substring in value")
    p.add_argument("--summary", action="store_true", help="One-line summary")
    p.set_defaults(func=cmd_select)


def cmd_select(args: argparse.Namespace) -> None:
    try:
        entries = _read_entries(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    has_value: bool | None = None
    if args.has_value == "yes":
        has_value = True
    elif args.has_value == "no":
        has_value = False

    criteria = SelectionCriteria(
        keys=args.keys,
        prefix=args.prefix,
        suffix=args.suffix,
        has_value=has_value,
        value_contains=args.value_contains,
    )

    result = select_entries(entries, criteria, filename=args.file)

    if args.summary:
        print(format_selection_summary(result))
    else:
        print(format_selection_result(result))
