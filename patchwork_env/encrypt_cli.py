"""CLI sub-command for encrypting / decrypting .env values."""
from __future__ import annotations

import getpass
import sys
from pathlib import Path

from patchwork_env.encrypt_formatter import format_encrypt_report, format_encrypt_summary
from patchwork_env.env_encryptr import encrypt_entries, decrypt_entry
from patchwork_env.parser import parse_env_file  # type: ignore[attr-defined]


def register_encrypt_subcommand(subparsers) -> None:
    p = subparsers.add_parser("encrypt", help="Encrypt or inspect encrypted .env values")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--hint",
        metavar="HINT",
        default=None,
        help="Optional passphrase hint stored in the report",
    )
    p.add_argument(
        "--decrypt-key",
        metavar="KEY",
        default=None,
        help="Decrypt and print the plaintext value for this key",
    )
    p.add_argument("--summary", action="store_true", help="Print summary only")
    p.set_defaults(func=cmd_encrypt)


def cmd_encrypt(args) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    passphrase = getpass.getpass("Passphrase: ")

    try:
        entries = parse_env_file(str(path))
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = encrypt_entries(entries, passphrase, filename=str(path), passphrase_hint=args.hint)

    if args.decrypt_key:
        target = next((e for e in report.entries if e.key == args.decrypt_key), None)
        if target is None:
            print(f"error: key {args.decrypt_key!r} not found", file=sys.stderr)
            return 1
        from patchwork_env.env_encryptr import decrypt_entry as _dec
        print(_dec(target, passphrase))
        return 0

    if args.summary:
        print(format_encrypt_summary(report))
    else:
        print(format_encrypt_report(report))
    return 0
