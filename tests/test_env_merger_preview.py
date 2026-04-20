"""Tests for env_merger_preview and preview_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.differ import EnvDiff, DiffStatus
from patchwork_env.resolver import Resolution, ResolutionStrategy
from patchwork_env.env_merger_preview import build_preview, MergePreview, PreviewLine
from patchwork_env.preview_formatter import format_preview, format_preview_summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(key: str, value: str, comment: str = "") -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=comment, raw=f"{key}={value}")


def _make_resolution() -> Resolution:
    base_entries = [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("SECRET", "old-secret", comment="sensitive"),
    ]
    target_entries = [
        _entry("DB_HOST", "prod.db"),
        _entry("DB_PORT", "5432"),
        _entry("NEW_KEY", "hello"),
    ]

    diff = EnvDiff.compute(base_entries, target_entries, base_name=".env", target_name=".env.prod")

    decisions = {}
    for de in diff.entries:
        if de.status == DiffStatus.MODIFIED:
            decisions[de.key] = ResolutionStrategy.USE_TARGET
        elif de.status == DiffStatus.ADDED:
            decisions[de.key] = ResolutionStrategy.ADD
        elif de.status == DiffStatus.REMOVED:
            decisions[de.key] = ResolutionStrategy.REMOVE
        else:
            decisions[de.key] = ResolutionStrategy.USE_BASE

    return Resolution(
        base_name=".env",
        target_name=".env.prod",
        decisions=decisions,
        base_map={e.key: e for e in base_entries},
        target_map={e.key: e for e in target_entries},
    )


@pytest.fixture
def resolution() -> Resolution:
    return _make_resolution()


@pytest.fixture
def preview(resolution: Resolution) -> MergePreview:
    return build_preview(resolution)


# ---------------------------------------------------------------------------
# MergePreview tests
# ---------------------------------------------------------------------------

def test_preview_has_correct_names(preview: MergePreview) -> None:
    assert preview.base_name == ".env"
    assert preview.target_name == ".env.prod"


def test_preview_lines_are_non_empty(preview: MergePreview) -> None:
    assert len(preview.lines) > 0


def test_added_key_present(preview: MergePreview) -> None:
    keys = [pl.key for pl in preview.added()]
    assert "NEW_KEY" in keys


def test_removed_key_present(preview: MergePreview) -> None:
    keys = [pl.key for pl in preview.removed_keys()]
    assert "SECRET" in keys


def test_overridden_key_uses_target_value(preview: MergePreview) -> None:
    overridden = {pl.key: pl.value for pl in preview.overridden()}
    assert overridden.get("DB_HOST") == "prod.db"


def test_comment_preserved(preview: MergePreview) -> None:
    removed = {pl.key: pl.comment for pl in preview.removed_keys()}
    assert removed.get("SECRET") == "sensitive"


# ---------------------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------------------

def test_format_preview_contains_header(preview: MergePreview) -> None:
    output = format_preview(preview)
    assert "Merge Preview" in output
    assert ".env.prod" in output


def test_format_preview_shows_added_key(preview: MergePreview) -> None:
    output = format_preview(preview)
    assert "NEW_KEY" in output


def test_format_preview_shows_removed_key(preview: MergePreview) -> None:
    output = format_preview(preview)
    assert "SECRET" in output


def test_format_summary_contains_counts(preview: MergePreview) -> None:
    summary = format_preview_summary(preview)
    assert "+" in summary
    assert "-" in summary
    assert "Preview summary" in summary
