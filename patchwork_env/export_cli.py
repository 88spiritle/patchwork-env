"""CLI helpers for the 'export' sub-command of patchwork-env.

Registered by cli.py via build_parser; kept separate to avoid bloating
the main CLI module.
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from patchwork_env.exporter import (
    export_snapshot_dotenv,
    export_snapshot_json,
)
from patchwork_env.snapshot import capture


FORMATS = ("json", "dotenv")


def register_export_subcommand(subparsers) -> None:  # type: ignore[type-arg]
    """Attach the 'export' sub-command to an existing subparsers action."""
    p: ArgumentParser = subparsers.add_parser(
        "export",
        help="Export a .env file to a portable format.",
    )
    p.add_argument("env_file", help="Path to the .env file to export.")
    p.add_argument(
        "--format",
        dest="fmt",
        choices=FORMATS,
        default="json",
        help="Output format (default: json).",
    )
    p.add_argument(
        "--environment",
        dest="environment",
        default="default",
        help="Logical environment label stored in the snapshot.",
    )
    p.add_argument(
        "--output",
        dest="output",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    p.set_defaults(func=cmd_export)


def _write_output(text: str, output_path: str | None) -> None:
    """Write *text* to *output_path*, or to stdout when *output_path* is None.

    Raises OSError if the destination file cannot be written.
    """
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def cmd_export(args: Namespace) -> int:
    """Execute the export sub-command.  Returns an exit code."""
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"error: file not found: {env_path}", file=sys.stderr)
        return 1

    snapshot = capture(env_path, environment=args.environment)

    if args.fmt == "json":
        text = export_snapshot_json(snapshot)
    elif args.fmt == "dotenv":
        text = export_snapshot_dotenv(snapshot)
    else:  # pragma: no cover
        print(f"error: unknown format '{args.fmt}'", file=sys.stderr)
        return 1

    try:
        _write_output(text, args.output)
    except OSError as exc:
        print(f"error: could not write output: {exc}", file=sys.stderr)
        return 1

    return 0
