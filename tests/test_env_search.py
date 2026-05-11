import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_search import (
    SearchCriteria,
    SearchHit,
    SearchResult,
    search_entries,
)
from patchwork_env.search_formatter import format_search_result, format_search_summary


def _entry(key: str, value: str) -> EnvEntry:
    e = EnvEntry.__new__(EnvEntry)
    e.key = key
    e.value = value
    e.raw = f"{key}={value}"
    e.comment = None
    return e


@pytest.fixture
def entries():
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("API_KEY", "secret-token"),
        _entry("APP_ENV", "production"),
        _entry("EMPTY_VAL", ""),
    ]


def test_no_criteria_returns_all_entries(entries):
    result = search_entries(entries, SearchCriteria(), filename=".env")
    assert result.total_hits == len(entries)


def test_key_pattern_filters_matching_keys(entries):
    result = search_entries(entries, SearchCriteria(key_pattern="^DB_"), filename=".env")
    assert result.total_hits == 2
    assert "DB_HOST" in result.hit_keys
    assert "DB_PORT" in result.hit_keys


def test_value_pattern_filters_matching_values(entries):
    result = search_entries(entries, SearchCriteria(value_pattern="secret"), filename=".env")
    assert result.total_hits == 1
    assert "API_KEY" in result.hit_keys


def test_both_patterns_must_match(entries):
    result = search_entries(
        entries,
        SearchCriteria(key_pattern="DB_", value_pattern="5432"),
        filename=".env",
    )
    assert result.total_hits == 1
    assert result.hits[0].entry.key == "DB_PORT"


def test_case_insensitive_by_default(entries):
    result = search_entries(entries, SearchCriteria(key_pattern="api_key"), filename=".env")
    assert result.total_hits == 1


def test_case_sensitive_no_match(entries):
    result = search_entries(
        entries,
        SearchCriteria(key_pattern="api_key", case_sensitive=True),
        filename=".env",
    )
    assert result.total_hits == 0


def test_hit_matched_key_flag_set():
    e = _entry("TOKEN", "abc")
    result = search_entries([e], SearchCriteria(key_pattern="TOKEN"), filename=".env")
    assert result.hits[0].matched_key is True
    assert result.hits[0].matched_value is False


def test_hit_matched_value_flag_set():
    e = _entry("TOKEN", "abc")
    result = search_entries([e], SearchCriteria(value_pattern="abc"), filename=".env")
    assert result.hits[0].matched_value is True
    assert result.hits[0].matched_key is False


def test_empty_entries_returns_empty_result():
    result = search_entries([], SearchCriteria(key_pattern="DB"), filename=".env")
    assert result.total_hits == 0
    assert result.hit_keys == []


def test_search_result_repr():
    r = SearchResult(filename=".env", criteria=SearchCriteria())
    assert ".env" in repr(r)


def test_format_search_result_no_hits():
    result = SearchResult(filename=".env", criteria=SearchCriteria(key_pattern="MISSING"))
    output = format_search_result(result)
    assert "No matches found" in output


def test_format_search_result_with_hits(entries):
    result = search_entries(entries, SearchCriteria(key_pattern="^DB_"), filename=".env")
    output = format_search_result(result)
    assert "DB_HOST" in output
    assert "2" in output


def test_format_search_summary_no_hits():
    result = SearchResult(filename=".env", criteria=SearchCriteria())
    summary = format_search_summary(result)
    assert ".env" in summary
    assert "no matches" in summary


def test_format_search_summary_with_hits(entries):
    result = search_entries(entries, SearchCriteria(key_pattern="DB_"), filename=".env")
    summary = format_search_summary(result)
    assert "2" in summary
