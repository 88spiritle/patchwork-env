"""Tests for patchwork_env.env_stasher."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_stasher import Stash, StashEntry


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, comment="")


@pytest.fixture()
def stash() -> Stash:
    return Stash()


@pytest.fixture()
def entries():
    return [_entry("DB_HOST", "localhost"), _entry("DB_PORT", "5432")]


# ---------------------------------------------------------------------------
# StashEntry
# ---------------------------------------------------------------------------

class TestStashEntry:
    def test_label_is_stored(self, entries):
        se = StashEntry(label="wip", entries=entries)
        assert se.label == "wip"

    def test_entries_are_copied(self, entries):
        se = StashEntry(label="wip", entries=entries)
        assert len(se.entries) == 2

    def test_stashed_at_is_set(self, entries):
        se = StashEntry(label="wip", entries=entries)
        assert se.stashed_at  # non-empty ISO string

    def test_round_trip_dict(self, entries):
        se = StashEntry(label="snap", entries=entries)
        restored = StashEntry.from_dict(se.to_dict())
        assert restored.label == se.label
        assert restored.stashed_at == se.stashed_at
        assert [e.key for e in restored.entries] == [e.key for e in entries]

    def test_to_dict_has_expected_keys(self, entries):
        d = StashEntry(label="x", entries=entries).to_dict()
        assert set(d.keys()) == {"label", "stashed_at", "entries"}


# ---------------------------------------------------------------------------
# Stash
# ---------------------------------------------------------------------------

class TestStash:
    def test_starts_empty(self, stash):
        assert len(stash) == 0

    def test_push_increases_length(self, stash, entries):
        stash.push("first", entries)
        assert len(stash) == 1

    def test_push_returns_stash_entry(self, stash, entries):
        se = stash.push("first", entries)
        assert isinstance(se, StashEntry)
        assert se.label == "first"

    def test_pop_returns_most_recent(self, stash, entries):
        stash.push("a", entries)
        stash.push("b", entries)
        popped = stash.pop()
        assert popped.label == "b"

    def test_pop_decreases_length(self, stash, entries):
        stash.push("a", entries)
        stash.pop()
        assert len(stash) == 0

    def test_pop_empty_returns_none(self, stash):
        assert stash.pop() is None

    def test_peek_does_not_remove(self, stash, entries):
        stash.push("a", entries)
        stash.peek()
        assert len(stash) == 1

    def test_peek_empty_returns_none(self, stash):
        assert stash.peek() is None

    def test_drop_by_label(self, stash, entries):
        stash.push("keep", entries)
        stash.push("remove", entries)
        result = stash.drop("remove")
        assert result is True
        assert all(se.label != "remove" for se in stash.list())

    def test_drop_missing_label_returns_false(self, stash, entries):
        stash.push("a", entries)
        assert stash.drop("nonexistent") is False

    def test_list_returns_all_entries(self, stash, entries):
        stash.push("x", entries)
        stash.push("y", entries)
        labels = [se.label for se in stash.list()]
        assert labels == ["x", "y"]
