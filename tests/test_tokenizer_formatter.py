"""Tests for patchwork_env.tokenizer_formatter."""
from patchwork_env.env_tokenizer import tokenize_value
from patchwork_env.tokenizer_formatter import (
    format_tokenize_result,
    format_tokenize_summary,
)


def _result(key: str, value: str):
    return tokenize_value(key, value)


# ---------------------------------------------------------------------------
# format_tokenize_result
# ---------------------------------------------------------------------------

def test_result_contains_key():
    out = format_tokenize_result(_result("DB_HOST", "localhost"), "prod.env")
    assert "DB_HOST" in out


def test_result_contains_filename():
    out = format_tokenize_result(_result("K", "v"), "staging.env")
    assert "staging.env" in out


def test_result_shows_literal_token_type():
    out = format_tokenize_result(_result("K", "hello"), "")
    assert "LITERAL" in out


def test_result_shows_variable_ref_type():
    out = format_tokenize_result(_result("DSN", "${HOST}"), "")
    assert "VARIABLE_REF" in out


def test_result_shows_token_count():
    result = _result("URL", "${A}://host")
    out = format_tokenize_result(result, "")
    assert str(len(result.tokens)) in out


def test_result_whitespace_shown_as_dot():
    out = format_tokenize_result(_result("MSG", "hello world"), "")
    assert "·" in out


# ---------------------------------------------------------------------------
# format_tokenize_summary
# ---------------------------------------------------------------------------

def test_summary_contains_filename():
    results = [_result("A", "1"), _result("B", "2")]
    out = format_tokenize_summary(results, "test.env")
    assert "test.env" in out


def test_summary_shows_total_keys():
    results = [_result("A", "1"), _result("B", "2"), _result("C", "3")]
    out = format_tokenize_summary(results, "")
    assert "3" in out


def test_summary_shows_ref_count():
    results = [_result("A", "${X}"), _result("B", "plain")]
    out = format_tokenize_summary(results, "")
    assert "1" in out


def test_summary_lists_keys_with_refs():
    results = [_result("DSN", "${HOST}/db"), _result("PORT", "5432")]
    out = format_tokenize_summary(results, "")
    assert "DSN" in out
    assert "HOST" in out
