"""Tests for FormatterRegistry."""
import pytest
from patchwork_env.env_formatter_registry import FormatterRecord, FormatterRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _noop_formatter(data):
    return str(data)


@pytest.fixture()
def registry():
    r = FormatterRegistry()
    r.register("json", ".json", "JSON export", _noop_formatter)
    r.register("csv", ".csv", "CSV export", _noop_formatter)
    return r


# ---------------------------------------------------------------------------
# FormatterRecord
# ---------------------------------------------------------------------------

def test_record_stores_name():
    rec = FormatterRecord("json", "json", "JSON", _noop_formatter)
    assert rec.name == "json"


def test_record_stores_extension():
    rec = FormatterRecord("json", "json", "JSON", _noop_formatter)
    assert rec.extension == "json"


def test_record_stores_description():
    rec = FormatterRecord("json", "json", "JSON export", _noop_formatter)
    assert rec.description == "JSON export"


def test_record_callable_is_stored():
    rec = FormatterRecord("json", "json", "JSON", _noop_formatter)
    assert rec.formatter is _noop_formatter


# ---------------------------------------------------------------------------
# FormatterRegistry.register
# ---------------------------------------------------------------------------

def test_register_adds_record(registry):
    assert "json" in registry


def test_register_strips_leading_dot_from_extension():
    r = FormatterRegistry()
    rec = r.register("md", ".md", "Markdown", _noop_formatter)
    assert rec.extension == "md"


def test_register_lowercases_name():
    r = FormatterRegistry()
    rec = r.register("JSON", "json", "JSON", _noop_formatter)
    assert rec.name == "json"
    assert "json" in r


def test_register_returns_record(registry):
    r = FormatterRegistry()
    rec = r.register("txt", "txt", "Text", _noop_formatter)
    assert isinstance(rec, FormatterRecord)


# ---------------------------------------------------------------------------
# FormatterRegistry.unregister
# ---------------------------------------------------------------------------

def test_unregister_removes_record(registry):
    registry.unregister("json")
    assert "json" not in registry


def test_unregister_missing_is_noop(registry):
    registry.unregister("xml")  # should not raise
    assert len(registry) == 2


# ---------------------------------------------------------------------------
# FormatterRegistry.get
# ---------------------------------------------------------------------------

def test_get_returns_record(registry):
    rec = registry.get("json")
    assert rec is not None
    assert rec.name == "json"


def test_get_missing_returns_none(registry):
    assert registry.get("xml") is None


def test_get_is_case_insensitive(registry):
    assert registry.get("JSON") is not None


# ---------------------------------------------------------------------------
# FormatterRegistry.names / all / __len__
# ---------------------------------------------------------------------------

def test_names_returns_sorted_list(registry):
    assert registry.names() == ["csv", "json"]


def test_all_returns_all_records(registry):
    assert len(registry.all()) == 2


def test_len_reflects_count(registry):
    assert len(registry) == 2
