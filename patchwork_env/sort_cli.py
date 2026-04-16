"""CLI sub-command: patchwork-env sort"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.env_sorter import SortMode, group_by_prefix, sort_entries
from patchwork_env.parser import parse_env_file
from patchwork_env.sort_formatter import format_grouped_entries, format_sorted_entries


def register_sort_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("sort", help="Sort and group keys in an .env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--mode",
        choices=[m.value for m in SortMode],
        default=SortMode.ALPHABETICAL.value,
        help="Sort mode (default: alpha)",
    )
    p.add_argument(
        "--group",
        action="store_true",
        default=False,
        help="Group output by key prefix",
    )
    p.add_argument(
        "--prefix-order",
        nargs="*",
        metavar="PREFIX",
        help="Explicit prefix order when --mode=prefix",
    )
    p.set_defaults(func=cmd_sort)


def cmd_sort(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    entries = parse_env_file(path)
    mode = SortMode(args.mode)
    sorted_entries = sort_entries(entries, mode=mode, custom_order=args.prefix_order)

    if args.group:
        groups = group_by_prefix(sorted_entries)
        print(format_grouped_entries(groups, filename=path.name))
    else:
        print(format_sorted_entries(sorted_entries, filename=path.name))

    return 0
