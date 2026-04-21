"""Tests for patchwork_env.schedule_formatter."""
from __future__ import annotations

from datetime import datetime

import pytest

from patchwork_env.env_scheduler import Schedule, ScheduledOverride
from patchwork_env.schedule_formatter import format_schedule, format_schedule_summary


PAST = datetime(2000, 1, 1)
FUTURE = datetime(2099, 1, 1)
NOW = datetime(2024, 6, 1, 12, 0, 0)


@pytest.fixture()
def schedule() -> Schedule:
    s = Schedule(name="production")
    s.add(ScheduledOverride(key="ACTIVE_KEY", value="on", start=PAST, end=FUTURE, label="rollout"))
    s.add(ScheduledOverride(key="EXPIRED_KEY", value="off", start=PAST, end=datetime(2001, 1, 1)))
    return s


def test_format_schedule_contains_name(schedule: Schedule):
    out = format_schedule(schedule, at=NOW)
    assert "production" in out


def test_format_schedule_shows_active_key(schedule: Schedule):
    out = format_schedule(schedule, at=NOW)
    assert "ACTIVE_KEY" in out


def test_format_schedule_shows_expired_key(schedule: Schedule):
    out = format_schedule(schedule, at=NOW)
    assert "EXPIRED_KEY" in out


def test_format_schedule_shows_active_status(schedule: Schedule):
    out = format_schedule(schedule, at=NOW)
    assert "ACTIVE" in out


def test_format_schedule_shows_label(schedule: Schedule):
    out = format_schedule(schedule, at=NOW)
    assert "rollout" in out


def test_format_empty_schedule():
    s = Schedule(name="empty")
    out = format_schedule(s)
    assert "no overrides" in out


def test_format_summary_contains_name(schedule: Schedule):
    out = format_schedule_summary(schedule, at=NOW)
    assert "production" in out


def test_format_summary_shows_counts(schedule: Schedule):
    out = format_schedule_summary(schedule, at=NOW)
    assert "2" in out  # total
    assert "1" in out  # active
