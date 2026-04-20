"""Format a MergePreview for terminal output."""
from __future__ import annotations

from patchwork_env.env_merger_preview import MergePreview, PreviewLine
from patchwork_env.resolver import ResolutionStrategy

_COLORS = {
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def _c(text: str, color: str) -> str:
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


_STRATEGY_META = {
    ResolutionStrategy.USE_BASE:   ("=", "cyan",   "keep base"),
    ResolutionStrategy.USE_TARGET: ("~", "yellow", "use target"),
    ResolutionStrategy.ADD:        ("+", "green",  "add"),
    ResolutionStrategy.REMOVE:     ("-", "red",    "remove"),
}


def format_preview(preview: MergePreview) -> str:
    lines: list[str] = []
    lines.append(
        _c(f"Merge Preview: {preview.base_name} ← {preview.target_name}", "bold")
    )
    lines.append("-" * 60)

    for pl in preview.lines:
        icon, color, label = _STRATEGY_META[pl.strategy]
        key_val = f"{pl.key}={pl.value}"
        suffix = f"  # {pl.comment}" if pl.comment else ""
        lines.append(f"  {_c(icon, color)} [{label:<11}] {key_val}{suffix}")

    lines.append("-" * 60)
    return "\n".join(lines)


def format_preview_summary(preview: MergePreview) -> str:
    kept = len(preview.kept())
    overridden = len(preview.overridden())
    added = len(preview.added())
    removed = len(preview.removed_keys())
    total = len(preview.lines)

    parts = [
        _c(f"+{added}", "green"),
        _c(f"~{overridden}", "yellow"),
        _c(f"={kept}", "cyan"),
        _c(f"-{removed}", "red"),
    ]
    return f"Preview summary ({total} keys): " + "  ".join(parts)
