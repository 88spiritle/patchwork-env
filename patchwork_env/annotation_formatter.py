"""Format annotation registries and annotated entries for CLI output."""
from __future__ import annotations

from typing import List

from patchwork_env.env_annotator import AnnotatedEntry, AnnotationRegistry


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_annotated_entries(
    entries: List[AnnotatedEntry],
    filename: str = "",
) -> str:
    lines: List[str] = []
    header = f"Annotations — {filename}" if filename else "Annotations"
    lines.append(_c("1;34", header))
    lines.append(_c("34", "─" * 40))

    if not entries:
        lines.append(_c("2", "  (no entries)"))
        return "\n".join(lines)

    for ae in entries:
        key_part = _c("1", ae.entry.key)
        val_part = _c("32", ae.entry.raw_value)
        lines.append(f"  {key_part}={val_part}")
        if ae.annotation:
            lines.append(f"    {_c('33', '#')} {ae.annotation}")

    return "\n".join(lines)


def format_annotation_registry(reg: AnnotationRegistry) -> str:
    lines: List[str] = []
    lines.append(_c("1;34", f"Registry: {reg.name}"))
    lines.append(_c("34", "─" * 40))
    keys = reg.annotated_keys()
    if not keys:
        lines.append(_c("2", "  (no annotations)"))
    else:
        for k in keys:
            lines.append(f"  {_c('1', k)}: {reg.get(k)}")
    return "\n".join(lines)


def format_annotation_summary(reg: AnnotationRegistry) -> str:
    count = len(reg.annotated_keys())
    noun = "annotation" if count == 1 else "annotations"
    return _c("1", f"{count} {noun} in registry '{reg.name}'")
