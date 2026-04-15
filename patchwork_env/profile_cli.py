"""CLI sub-commands for profile management."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from patchwork_env.profiler import EnvProfile, ProfileRegistry
from patchwork_env.profile_formatter import format_profile, format_registry, format_registry_summary


def _load_registry(path: str) -> ProfileRegistry:
    p = Path(path)
    if not p.exists():
        return ProfileRegistry()
    return ProfileRegistry.from_dict(json.loads(p.read_text()))


def _save_registry(registry: ProfileRegistry, path: str) -> None:
    Path(path).write_text(json.dumps(registry.to_dict(), indent=2))


def register_profile_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("profile", help="Manage environment profiles")
    sub = p.add_subparsers(dest="profile_cmd", required=True)

    add_p = sub.add_parser("add", help="Create or update a profile")
    add_p.add_argument("name")
    add_p.add_argument("environment")
    add_p.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), action="append", dest="pairs", default=[])
    add_p.add_argument("--store", default="profiles.json", help="Path to profile store")

    list_p = sub.add_parser("list", help="List all profiles")
    list_p.add_argument("--store", default="profiles.json")

    show_p = sub.add_parser("show", help="Show a specific profile")
    show_p.add_argument("name")
    show_p.add_argument("--store", default="profiles.json")

    rm_p = sub.add_parser("remove", help="Remove a profile")
    rm_p.add_argument("name")
    rm_p.add_argument("--store", default="profiles.json")


def cmd_profile(args: argparse.Namespace) -> int:
    registry = _load_registry(args.store)

    if args.profile_cmd == "add":
        profile = EnvProfile(name=args.name, environment=args.environment)
        for key, value in args.pairs:
            profile.set(key, value)
        registry.register(profile)
        _save_registry(registry, args.store)
        print(f"Profile '{args.name}' saved.")

    elif args.profile_cmd == "list":
        print(format_registry_summary(registry))
        if registry.list_names():
            print(format_registry(registry))

    elif args.profile_cmd == "show":
        profile = registry.get(args.name)
        if profile is None:
            print(f"Profile '{args.name}' not found.", file=sys.stderr)
            return 1
        print(format_profile(profile))

    elif args.profile_cmd == "remove":
        removed = registry.remove(args.name)
        _save_registry(registry, args.store)
        if removed:
            print(f"Profile '{args.name}' removed.")
        else:
            print(f"Profile '{args.name}' not found.", file=sys.stderr)
            return 1

    return 0
