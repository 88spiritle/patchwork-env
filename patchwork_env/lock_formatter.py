"""lock_formatter.py – human-readable output for LockRegistry."""
from __future__ import annotations

from patchwork_env.env_locker import LockedKey, LockRegistry


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_locked_key(lk: LockedKey) -> str:
    """Single-line summary for one locked key."""
    reason_part = f"  # {lk.reason}" if lk.reason else ""
    key_str = _c("33", lk.key)
    return f"  🔒 {key_str}{reason_part}  (since {lk.locked_at[:10]})"


def format_lock_registry(registry: LockRegistry) -> str:
    """Full formatted report for a LockRegistry."""
    lines: list[str] = []
    lines.append(_c("1;34", f"Lock Registry: {registry.name}"))
    lines.append("-" * 40)

    if not registry.locked_keys:
        lines.append(_c("2", "  (no locked keys)"))
    else:
        for lk in sorted(registry.locked_keys, key=lambda x: x.key):
            lines.append(format_locked_key(lk))

    return "\n".join(lines)


def format_lock_summary(registry: LockRegistry) -> str:
    """One-line summary suitable for CLI output."""
    count = len(registry.locked_keys)
    noun = "key" if count == 1 else "keys"
    label = _c("1", registry.name)
    count_str = _c("33", str(count))
    return f"{label}: {count_str} locked {noun}"
