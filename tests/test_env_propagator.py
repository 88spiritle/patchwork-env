"""Tests for patchwork_env.env_propagator."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_propagator import (
    propagate,
    PropagationRecord,
    PropagationResult,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw=f"{key}={value}")


@pytest.fixture()
def source() -> list[EnvEntry]:
    return [
        _entry("DB_HOST", "prod-db.example.com"),
        _entry("DB_PORT", "5432"),
        _entry("API_KEY", "secret-prod"),
    ]


@pytest.fixture()
def target() -> list[EnvEntry]:
    return [
        _entry("DB_HOST", "localhost"),
        _entry("APP_ENV", "staging"),
    ]


# ---------------------------------------------------------------------------
# PropagationRecord
# ---------------------------------------------------------------------------

def test_record_repr_added():
    rec = PropagationRecord(
        key="FOO", target_file=".env.staging",
        old_value=None, new_value="bar", overwritten=False,
    )
    assert "added" in repr(rec)


def test_record_repr_overwritten():
    rec = PropagationRecord(
        key="FOO", target_file=".env.staging",
        old_value="old", new_value="new", overwritten=True,
    )
    assert "overwritten" in repr(rec)


# ---------------------------------------------------------------------------
# PropagationResult counters
# ---------------------------------------------------------------------------

def test_result_total_propagated(source, target):
    result = propagate(source, target, target_file=".env.staging")
    assert result.total_propagated == 3  # DB_HOST overwrite + DB_PORT + API_KEY added


def test_result_total_overwritten(source, target):
    result = propagate(source, target, target_file=".env.staging")
    assert result.total_overwritten == 1  # only DB_HOST existed


def test_result_total_added(source, target):
    result = propagate(source, target, target_file=".env.staging")
    assert result.total_added == 2  # DB_PORT and API_KEY


# ---------------------------------------------------------------------------
# Selective key propagation
# ---------------------------------------------------------------------------

def test_propagate_specific_keys_only(source, target):
    result = propagate(source, target, target_file=".env.staging", keys=["DB_PORT"])
    assert result.total_propagated == 1
    assert result.records[0].key == "DB_PORT"


def test_propagate_missing_key_is_skipped(source, target):
    result = propagate(source, target, target_file=".env.staging", keys=["NONEXISTENT"])
    assert result.total_propagated == 0


# ---------------------------------------------------------------------------
# overwrite=False behaviour
# ---------------------------------------------------------------------------

def test_no_overwrite_skips_existing(source, target):
    result = propagate(source, target, target_file=".env.staging", overwrite=False)
    # DB_HOST already exists -> skipped; DB_PORT and API_KEY should be added
    assert result.total_overwritten == 0
    assert result.total_added == 2


def test_no_overwrite_preserves_target_value(source, target):
    propagate(source, target, target_file=".env.staging", overwrite=False)
    target_map = {e.key: e for e in target}
    assert target_map["DB_HOST"].value == "localhost"  # unchanged


# ---------------------------------------------------------------------------
# Mutation of target list
# ---------------------------------------------------------------------------

def test_new_key_appended_to_target(source, target):
    propagate(source, target, target_file=".env.staging")
    keys = [e.key for e in target]
    assert "API_KEY" in keys


def test_existing_key_value_updated_in_target(source, target):
    propagate(source, target, target_file=".env.staging")
    target_map = {e.key: e for e in target}
    assert target_map["DB_HOST"].value == "prod-db.example.com"
