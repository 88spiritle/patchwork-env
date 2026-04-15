"""CLI entry point for patchwork-env."""

import argparse
import sys
from pathlib import Path

from patchwork_env.parser import EnvFile
from patchwork_env.differ import EnvDiff
from patchwork_env.formatter import format_diff, format_summary
from patchwork_env.resolver import ResolutionStrategy, resolve_diff
from patchwork_env.merger import merge_to_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchwork-env",
        description="Diff and reconcile .env files across deployment environments.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- diff subcommand ---
    diff_cmd = subparsers.add_parser("diff", help="Show differences between two .env files.")
    diff_cmd.add_argument("base", type=Path, help="Base .env file.")
    diff_cmd.add_argument("target", type=Path, help="Target .env file.")
    diff_cmd.add_argument("--summary", action="store_true", help="Show summary only.")

    # --- merge subcommand ---
    merge_cmd = subparsers.add_parser("merge", help="Merge target into base using a strategy.")
    merge_cmd.add_argument("base", type=Path, help="Base .env file.")
    merge_cmd.add_argument("target", type=Path, help="Target .env file.")
    merge_cmd.add_argument(
        "--strategy",
        choices=[s.value for s in ResolutionStrategy],
        default=ResolutionStrategy.USE_TARGET.value,
        help="Conflict resolution strategy (default: use_target).",
    )
    merge_cmd.add_argument("--output", "-o", type=Path, default=None, help="Output file path.")

    return parser


def cmd_diff(args: argparse.Namespace) -> int:
    base = EnvFile.from_path(args.base)
    target = EnvFile.from_path(args.target)
    diff = EnvDiff(base, target)
    if args.summary:
        print(format_summary(diff))
    else:
        print(format_diff(diff))
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    base = EnvFile.from_path(args.base)
    target = EnvFile.from_path(args.target)
    diff = EnvDiff(base, target)
    strategy = ResolutionStrategy(args.strategy)
    resolution = resolve_diff(diff, strategy)
    text = merge_to_text(base, resolution)
    if args.output:
        args.output.write_text(text)
        print(f"Merged output written to {args.output}")
    else:
        print(text)
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {"diff": cmd_diff, "merge": cmd_merge}
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
