"""Tests for patchwork_env.env_scheduler."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from patchwork_env.env_scheduler import Schedule, ScheduledOverride
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment="", raw=f"{key}={value}")


PAST = datetime(2000, 1, 1)
FUTURE = datetime(2099, 1, 1)
NOW = datetime(2024, 6, 1, 12, 0, 0)


# ── ScheduledOverride.is_active ───────────────────────────────────────────────

def test_active_within_window():
    o = ScheduledOverride(key="K", value="v", start=PAST, end=FUTURE)
    assert o.is_active(NOW) is True


def test_inactive_before_start():
    o = ScheduledOverride(key="K", value="v", start=FUTURE)
    assert o.is_active(NOW) is False


def test_inactive_after_end():
    o = ScheduledOverride(key="K", value="v", start=PAST, end=datetime(2001, 1, 1))
    assert o.is_active(NOW) is False


def test_no_end_means_perpetual():
    o = ScheduledOverride(key="K", value="v", start=PAST, end=None)
    assert o.is_active(FUTURE) is True


# ── Schedule helpers ──────────────────────────────────────────────────────────

@pytest.fixture()
def schedule() -> Schedule:
    s = Schedule(name="staging")
    s.add(ScheduledOverride(key="FEATURE_X", value="true", start=PAST, end=FUTURE, label="beta"))
    s.add(ScheduledOverride(key="OLD_KEY", value="gone", start=PAST, end=datetime(2001, 1, 1)))
    return s


def test_active_overrides_filters_expired(schedule: Schedule):
    active = schedule.active_overrides(NOW)
    assert len(active) == 1
    assert active[0].key == "FEATURE_X"


def test_remove_deletes_by_key(schedule: Schedule):
    schedule.remove("FEATURE_X")
    assert all(o.key != "FEATURE_X" for o in schedule.overrides)


def test_remove_missing_key_is_noop(schedule: Schedule):
    before = len(schedule.overrides)
    schedule.remove("NONEXISTENT")
    assert len(schedule.overrides) == before


# ── Schedule.apply ────────────────────────────────────────────────────────────

def test_apply_overrides_active_key(schedule: Schedule):
    entries = [_entry("FEATURE_X", "false"), _entry("OTHER", "val")]
    result = schedule.apply(entries, at=NOW)
    by_key = {e.key: e.value for e in result if e.key}
    assert by_key["FEATURE_X"] == "true"


def test_apply_leaves_inactive_unchanged(schedule: Schedule):
    entries = [_entry("OLD_KEY", "original")]
    result = schedule.apply(entries, at=NOW)
    assert result[0].value == "original"


def test_apply_preserves_unrelated_entries(schedule: Schedule):
    entries = [_entry("UNRELATED", "keep")]
    result = schedule.apply(entries, at=NOW)
    assert result[0].value == "keep"
