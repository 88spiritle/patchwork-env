"""Tests for env_requirer.py."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_requirer import (
    RequirementHit,
    RequirementReport,
    check_requirements,
)


def _entry(key: str, value: str = "x") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# RequirementHit
# ---------------------------------------------------------------------------

def test_hit_found_true():
    h = RequirementHit(key="FOO", found=True, value="bar")
    assert h.found is True
    assert h.value == "bar"


def test_hit_found_false_has_no_value():
    h = RequirementHit(key="FOO", found=False)
    assert h.found is False
    assert h.value is None


# ---------------------------------------------------------------------------
# RequirementReport
# ---------------------------------------------------------------------------

@pytest.fixture
def partial_report():
    hits = [
        RequirementHit(key="DB_HOST", found=True, value="localhost"),
        RequirementHit(key="DB_PASS", found=False),
        RequirementHit(key="API_KEY", found=True, value="secret"),
        RequirementHit(key="SECRET_TOKEN", found=False),
    ]
    return RequirementReport(filename=".env", hits=hits)


def test_missing_filters_unfound(partial_report):
    assert len(partial_report.missing) == 2
    assert all(not h.found for h in partial_report.missing)


def test_satisfied_filters_found(partial_report):
    assert len(partial_report.satisfied) == 2
    assert all(h.found for h in partial_report.satisfied)


def test_is_complete_false_when_missing(partial_report):
    assert partial_report.is_complete is False


def test_is_complete_true_when_all_found():
    hits = [
        RequirementHit(key="A", found=True, value="1"),
        RequirementHit(key="B", found=True, value="2"),
    ]
    report = RequirementReport(filename=".env", hits=hits)
    assert report.is_complete is True


# ---------------------------------------------------------------------------
# check_requirements
# ---------------------------------------------------------------------------

def test_check_all_present():
    entries = [_entry("DB_HOST", "localhost"), _entry("API_KEY", "abc123")]
    report = check_requirements(["DB_HOST", "API_KEY"], entries, filename=".env")
    assert report.is_complete is True
    assert len(report.missing) == 0


def test_check_missing_key():
    entries = [_entry("DB_HOST", "localhost")]
    report = check_requirements(["DB_HOST", "API_KEY"], entries, filename=".env")
    assert report.is_complete is False
    assert report.missing[0].key == "API_KEY"


def test_check_key_case_insensitive():
    entries = [_entry("db_host", "localhost")]
    report = check_requirements(["DB_HOST"], entries, filename=".env")
    assert report.is_complete is True


def test_check_filename_stored():
    report = check_requirements([], [], filename="prod.env")
    assert report.filename == "prod.env"


def test_check_empty_requirements():
    entries = [_entry("FOO", "bar")]
    report = check_requirements([], entries)
    assert report.is_complete is True
    assert report.hits == []


def test_check_value_stored_for_found_key():
    entries = [_entry("TOKEN", "mysecret")]
    report = check_requirements(["TOKEN"], entries)
    hit = report.satisfied[0]
    assert hit.value == "mysecret"
