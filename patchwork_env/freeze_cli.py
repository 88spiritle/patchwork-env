"""CLI sub-command for managing the freeze registry."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from patchwork_env.env_freezer import FreezeRegistry
from patchwork_env.freeze_formatter import format_freeze_summary

_REGISTRY_FILE = Path(".patchwork_freeze.json")


def _load_registry() -> FreezeRegistry:
    reg = FreezeRegistry()
    if _REGISTRY_FILE.exists():
        data = json.loads(_REGISTRY_FILE.read_text())
        for item in data.get("frozen", []):
            reg.freeze(item["key"], item["frozen_value"], item.get("reason"))
    return reg


def _save_registry(reg: FreezeRegistry) -> None:
    data = {
        "frozen": [
            {"key": fk.key, "frozen_value": fk.frozen_value, "reason": fk.reason}
            for fk in reg.all_frozen
        ]
    }
    _REGISTRY_FILE.write_text(json.dumps(data, indent=2))


def register_freeze_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("freeze", help="Manage frozen env keys")
    sub = p.add_subparsers(dest="freeze_action", required=True)

    add_p = sub.add_parser("add", help="Freeze a key to a specific value")
    add_p.add_argument("key", help="Key name to freeze")
    add_p.add_argument("value", help="Value to lock the key to")
    add_p.add_argument("--reason", default=None, help="Optional reason")

    rm_p = sub.add_parser("remove", help="Unfreeze a key")
    rm_p.add_argument("key", help="Key name to unfreeze")

    sub.add_parser("list", help="List all frozen keys")
    p.set_defaults(func=cmd_freeze)


def cmd_freeze(args: argparse.Namespace) -> None:
    reg = _load_registry()

    if args.freeze_action == "add":
        reg.freeze(args.key, args.value, args.reason)
        _save_registry(reg)
        print(f"Frozen: {args.key} = {args.value}")

    elif args.freeze_action == "remove":
        if not reg.is_frozen(args.key):
            print(f"Key '{args.key}' is not frozen.", file=sys.stderr)
            sys.exit(1)
        reg.unfreeze(args.key)
        _save_registry(reg)
        print(f"Unfrozen: {args.key}")

    elif args.freeze_action == "list":
        print(format_freeze_summary(reg.all_frozen))
