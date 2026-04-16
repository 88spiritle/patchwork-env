"""CLI subcommand: patchwork-env template — generate a .env.template file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import parse_env_file
from patchwork_env.env_template import build_template, template_to_text
from patchwork_env.template_formatter import format_template, format_template_summary


def register_template_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "template",
        help="Generate a .env.template from an existing .env file",
    )
    p.add_argument("env_file", help="Path to the source .env file")
    p.add_argument(
        "-o", "--output",
        help="Write template to this file (default: print to stdout)",
        default=None,
    )
    p.add_argument(
        "--name",
        help="Name label for the template (default: source filename)",
        default=None,
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary after generating",
    )
    p.set_defaults(func=cmd_template)


def cmd_template(args: argparse.Namespace) -> int:
    source = Path(args.env_file)
    if not source.exists():
        print(f"Error: file not found: {source}", file=sys.stderr)
        return 1

    entries = parse_env_file(source)
    name = args.name or source.name
    template = build_template(entries, name=name)

    print(format_template(template))

    text = template_to_text(template)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Template written to {args.output}")
    else:
        print("\n--- Raw template ---")
        print(text, end="")

    if args.summary:
        print(format_template_summary(template))

    return 0
