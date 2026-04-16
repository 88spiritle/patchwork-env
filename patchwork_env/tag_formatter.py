"""Format tagged entries for terminal output."""
from typing import List
from patchwork_env.env_tagger import TaggedEntry, TagRegistry


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_tagged_entries(entries: List[TaggedEntry], filename: str = "") -> str:
    lines: List[str] = []
    header = f"Tagged entries{'  (' + filename + ')' if filename else ''}"
    lines.append(_c(1, header))
    lines.append("-" * max(40, len(header)))
    for te in entries:
        tag_str = ", ".join(sorted(te.tags)) if te.tags else _c(2, "(no tags)")
        key_part = _c(36, te.entry.key)
        lines.append(f"  {key_part}  [{tag_str}]")
    if not entries:
        lines.append("  (no entries)")
    return "\n".join(lines)


def format_tag_registry(registry: TagRegistry) -> str:
    lines: List[str] = []
    lines.append(_c(1, f"Tag registry: {registry.name}"))
    lines.append("-" * 40)
    data = registry.to_dict()["tags"]
    if not data:
        lines.append("  (empty)")
    for key, tags in sorted(data.items()):
        lines.append(f"  {_c(36, key)}: {', '.join(tags)}")
    return "\n".join(lines)


def format_tag_summary(registry: TagRegistry) -> str:
    total_keys = len(registry.to_dict()["tags"])
    all_tags: set = set()
    for tags in registry.to_dict()["tags"].values():
        all_tags.update(tags)
    return _c(1, f"Registry '{registry.name}': {total_keys} tagged key(s), {len(all_tags)} unique tag(s)")
