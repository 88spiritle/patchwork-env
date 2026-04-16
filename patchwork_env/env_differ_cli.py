"""CLI subcommand for environment scoring and grading."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import EnvEntry
from patchwork_env.env_linter import lint_entries
from patchwork_env.validator import validate_entries
from patchwork_env.env_scorer import compute_score
from patchwork_env.score_formatter import format_score, format_score_summary


def _read_entries(path: str) -> list[EnvEntry]:
    """Parse an .env file and return its entries."""
    from patchwork_env.parser import parse_env_file

    return parse_env_file(Path(path))


def register_score_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Attach the 'score' subcommand to an existing subparsers group."""
    parser = subparsers.add_parser(
        "score",
        help="Score an .env file and display a quality grade.",
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        help="Path to the .env file to score.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print only the summary line instead of the full report.",
    )
    parser.add_argument(
        "--fail-below",
        metavar="GRADE",
        default=None,
        dest="fail_below",
        help=(
            "Exit with code 1 if the grade is below this threshold "
            "(e.g. B, C).  Grades ordered: S A B C D F."
        ),
    )
    parser.set_defaults(func=cmd_score)


_GRADE_ORDER = ["S", "A", "B", "C", "D", "F"]


def _grade_below(actual: str, threshold: str) -> bool:
    """Return True when *actual* grade is strictly worse than *threshold*."""
    try:
        return _GRADE_ORDER.index(actual) > _GRADE_ORDER.index(threshold.upper())
    except ValueError:
        return False


def cmd_score(args: argparse.Namespace) -> int:
    """Execute the 'score' subcommand.

    Returns an integer exit code (0 = success, 1 = failure).
    """
    try:
        entries = _read_entries(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse {args.file}: {exc}", file=sys.stderr)
        return 1

    lint_result = lint_entries(entries)
    validation_result = validate_entries(entries)
    score = compute_score(lint_result, validation_result)

    if args.summary:
        print(format_score_summary(score, filename=args.file))
    else:
        print(format_score(score, filename=args.file))

    if args.fail_below and _grade_below(score.grade, args.fail_below):
        return 1

    return 0
