"""CLI subcommand: classify — group env keys by semantic category."""
from __future__ import annotations

import argparse
from pathlib import Path

from patchwork_env.parser import EnvEntry
from patchwork_env.env_classifier import classify_entries
from patchwork_env.classifier_formatter import format_classification, format_classification_summary


def _read_entries(path: str) -> list[EnvEntry]:
    from patchwork_env.parser import parse_env_file  # local import to avoid circular
    return parse_env_file(Path(path))


def register_classify_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("classify", help="Classify env keys by semantic category")
    p.add_argument("file", help="Path to .env file")
    p.add_argument("--summary", action="store_true", help="Print one-line summary only")
    p.set_defaults(func=cmd_classify)


def cmd_classify(args: argparse.Namespace) -> None:
    entries = _read_entries(args.file)
    report = classify_entries(entries, filename=args.file)

    if args.summary:
        print(format_classification_summary(report))
    else:
        print(format_classification(report))
