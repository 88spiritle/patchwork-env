"""Formatters for :mod:`patchwork_env.env_encryptr` output."""
from __future__ import annotations

from patchwork_env.env_encryptr import EncryptReport


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_encrypt_report(report: EncryptReport) -> str:
    lines: list[str] = []
    header = _c(1, f"Encrypted entries — {report.filename}")
    lines.append(header)
    if report.passphrase_hint:
        lines.append(f"  Hint : {_c(33, report.passphrase_hint)}")
    lines.append("")

    for entry in report.entries:
        key_col = _c(36, entry.key.ljust(30))
        backend_col = _c(90, f"[{entry.backend}]")
        token_preview = entry.token[:24] + "…" if len(entry.token) > 24 else entry.token
        lines.append(f"  {key_col}  {_c(33, token_preview)}  {backend_col}")

    lines.append("")
    return "\n".join(lines)


def format_encrypt_summary(report: EncryptReport) -> str:
    backend_label = report.entries[0].backend if report.entries else "n/a"
    return (
        _c(1, "Encryption summary") + "\n"
        f"  File    : {report.filename}\n"
        f"  Keys    : {_c(32, str(report.total))}\n"
        f"  Backend : {_c(36, backend_label)}\n"
    )
