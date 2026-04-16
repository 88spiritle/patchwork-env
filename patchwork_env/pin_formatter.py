"""Formatter for PinRegistry output."""
from patchwork_env.env_pinner import PinRegistry, PinnedKey


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_pin_registry(registry: PinRegistry, *, colour: bool = True) -> str:
    lines = []
    header = f"Pin Registry: {registry.name}"
    lines.append(_c(header, "1;36") if colour else header)
    lines.append("-" * len(header))

    if not registry.pins:
        lines.append("  (no pins defined)")
        return "\n".join(lines)

    for key, pinned in sorted(registry.pins.items()):
        value_str = _c(pinned.value, "33") if colour else pinned.value
        key_str = _c(key, "1") if colour else key
        line = f"  {key_str} = {value_str}"
        if pinned.reason:
            reason_str = _c(f"# {pinned.reason}", "2") if colour else f"# {pinned.reason}"
            line += f"  {reason_str}"
        lines.append(line)

    return "\n".join(lines)


def format_pin_summary(registry: PinRegistry) -> str:
    count = len(registry.pins)
    noun = "pin" if count == 1 else "pins"
    return f"Registry '{registry.name}': {count} {noun} active."
