"""Tests for env_watchlist module."""
import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_watchlist import Watchlist, WatchedKey, WatchHit, WatchReport


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture
def wl() -> Watchlist:
    w = Watchlist()
    w.watch("DATABASE_URL", note="primary DB")
    w.watch("SECRET_KEY")
    w.watch("REDIS_URL")
    return w


@pytest.fixture
def entries():
    return [
        _entry("DATABASE_URL", "postgres://localhost/db"),
        _entry("SECRET_KEY", "supersecret"),
        _entry("DEBUG", "true"),
    ]


def test_watch_adds_key(wl):
    assert wl.is_watched("DATABASE_URL")


def test_unwatch_removes_key(wl):
    wl.unwatch("SECRET_KEY")
    assert not wl.is_watched("SECRET_KEY")


def test_unwatch_missing_is_noop(wl):
    wl.unwatch("NONEXISTENT")
    assert "NONEXISTENT" not in wl.keys


def test_keys_returns_all_watched(wl):
    assert set(wl.keys) == {"DATABASE_URL", "SECRET_KEY", "REDIS_URL"}


def test_scan_returns_watch_report(wl, entries):
    report = wl.scan(entries, filename=".env.test")
    assert isinstance(report, WatchReport)
    assert report.filename == ".env.test"


def test_scan_hits_present_keys(wl, entries):
    report = wl.scan(entries, filename=".env")
    assert "DATABASE_URL" in report.hit_keys
    assert "SECRET_KEY" in report.hit_keys


def test_scan_misses_absent_keys(wl, entries):
    report = wl.scan(entries, filename=".env")
    assert "REDIS_URL" in report.miss_keys


def test_scan_hit_carries_note(wl, entries):
    report = wl.scan(entries, filename=".env")
    db_hit = next(h for h in report.hits if h.key == "DATABASE_URL")
    assert db_hit.note == "primary DB"


def test_scan_hit_no_note_for_unwatched_note(wl, entries):
    report = wl.scan(entries, filename=".env")
    sk_hit = next(h for h in report.hits if h.key == "SECRET_KEY")
    assert sk_hit.note is None


def test_scan_all_present_no_misses():
    w = Watchlist()
    w.watch("FOO")
    report = w.scan([_entry("FOO", "bar")], filename=".env")
    assert report.misses == []


def test_scan_empty_entries_all_miss(wl):
    report = wl.scan([], filename=".env")
    assert set(report.miss_keys) == {"DATABASE_URL", "SECRET_KEY", "REDIS_URL"}
    assert report.hits == []
