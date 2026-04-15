"""Tests for patchwork_env.auditor."""

import json
import pytest
from pathlib import Path

from patchwork_env.auditor import (
    AuditEvent,
    AuditLog,
    make_diff_event,
    make_merge_event,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sample_event(op: str = "diff") -> AuditEvent:
    return AuditEvent(
        timestamp="2024-01-01T00:00:00Z",
        operation=op,
        base_file=".env.base",
        target_file=".env.prod",
        summary="+1 -0 ~2",
        details={"added": 1, "removed": 0, "modified": 2},
    )


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------

class TestAuditLog:
    def test_starts_empty(self):
        log = AuditLog()
        assert log.events == []

    def test_record_appends_event(self):
        log = AuditLog()
        ev = _sample_event()
        log.record(ev)
        assert len(log.events) == 1
        assert log.events[0] is ev

    def test_to_dict_contains_events_key(self):
        log = AuditLog()
        log.record(_sample_event())
        d = log.to_dict()
        assert "events" in d
        assert len(d["events"]) == 1

    def test_round_trip_dict(self):
        log = AuditLog()
        log.record(_sample_event("merge"))
        restored = AuditLog.from_dict(log.to_dict())
        assert len(restored.events) == 1
        assert restored.events[0].operation == "merge"
        assert restored.events[0].base_file == ".env.base"

    def test_save_and_load(self, tmp_path):
        log = AuditLog()
        log.record(_sample_event())
        audit_file = tmp_path / "audit.json"
        log.save(audit_file)
        assert audit_file.exists()
        loaded = AuditLog.load(audit_file)
        assert len(loaded.events) == 1
        assert loaded.events[0].summary == "+1 -0 ~2"

    def test_save_produces_valid_json(self, tmp_path):
        log = AuditLog()
        log.record(_sample_event())
        audit_file = tmp_path / "audit.json"
        log.save(audit_file)
        data = json.loads(audit_file.read_text())
        assert isinstance(data["events"], list)


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def test_make_diff_event_operation():
    ev = make_diff_event(".env", ".env.prod", added=2, removed=1, modified=3)
    assert ev.operation == "diff"


def test_make_diff_event_summary_format():
    ev = make_diff_event(".env", ".env.prod", added=2, removed=1, modified=3)
    assert "+2" in ev.summary
    assert "-1" in ev.summary
    assert "~3" in ev.summary


def test_make_diff_event_details():
    ev = make_diff_event(".env", ".env.prod", added=2, removed=1, modified=3)
    assert ev.details["added"] == 2
    assert ev.details["removed"] == 1
    assert ev.details["modified"] == 3


def test_make_merge_event_operation():
    ev = make_merge_event(".env", ".env.prod", ".env.out", keys_written=10)
    assert ev.operation == "merge"


def test_make_merge_event_summary_contains_output():
    ev = make_merge_event(".env", ".env.prod", ".env.out", keys_written=10)
    assert ".env.out" in ev.summary
    assert "10" in ev.summary


def test_make_merge_event_details():
    ev = make_merge_event(".env", ".env.prod", ".env.out", keys_written=7)
    assert ev.details["keys_written"] == 7
    assert ev.details["output_file"] == ".env.out"


def test_event_timestamp_is_string():
    ev = make_diff_event(".env", ".env.prod", 0, 0, 0)
    assert isinstance(ev.timestamp, str)
    assert ev.timestamp.endswith("Z")
