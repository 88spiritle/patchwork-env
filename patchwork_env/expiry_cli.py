"""expiry_cli.py — CLI subcommand for env-key expiry management."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import List

from patchwork_env.env_expiry import ExpiryRecord, build_expiry_report
from patchwork_env.expiry_formatter import format_expiry_report, format_expiry_summary

_DEFAULT_REGISTRY = ".patchwork_expiry.json"


def _load_registry(path: str) -> List[ExpiryRecord]:
    p = Path(path)
    if not p.exists():
        return []
    data = json.loads(p.read_text())
    return [ExpiryRecord.from_dict(d) for d in data.get("records", [])]


def _save_registry(path: str, records: List[ExpiryRecord]) -> None:
    payload = {"records": [r.to_dict() for r in records]}
    Path(path).write_text(json.dumps(payload, indent=2))


def register_expiry_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("expiry", help="Manage key expiry dates")
    p.add_argument("--registry", default=_DEFAULT_REGISTRY)
    sub = p.add_subparsers(dest="expiry_cmd")

    add_p = sub.add_parser("add", help="Register an expiry date for a key")
    add_p.add_argument("key")
    add_p.add_argument("expires_on", help="ISO date, e.g. 2025-12-31")
    add_p.add_argument("--reason", default=None)

    sub.add_parser("list", help="List all expiry records")
    sub.add_parser("check", help="Show expired / expiring-soon keys")

    remove_p = sub.add_parser("remove", help="Remove expiry record for a key")
    remove_p.add_argument("key")
    p.set_defaults(func=cmd_expiry)


def cmd_expiry(args: argparse.Namespace) -> None:
    records = _load_registry(args.registry)

    if args.expiry_cmd == "add":
        expires = date.fromisoformat(args.expires_on)
        records = [r for r in records if r.key.upper() != args.key.upper()]
        records.append(ExpiryRecord(key=args.key.upper(), expires_on=expires, reason=args.reason))
        _save_registry(args.registry, records)
        print(f"Registered expiry for {args.key.upper()} on {expires}.")

    elif args.expiry_cmd == "remove":
        before = len(records)
        records = [r for r in records if r.key.upper() != args.key.upper()]
        _save_registry(args.registry, records)
        removed = before - len(records)
        print(f"Removed {removed} record(s) for {args.key.upper()}.")

    elif args.expiry_cmd in ("list", "check", None):
        report = build_expiry_report(args.registry, records)
        print(format_expiry_report(report))
        print(format_expiry_summary(report))
