"""Tests for patchwork_env.env_tokenizer."""
import pytest

from patchwork_env.env_tokenizer import (
    Token,
    TokenType,
    TokenizeResult,
    tokenize_value,
)


# ---------------------------------------------------------------------------
# tokenize_value — literal only
# ---------------------------------------------------------------------------

def test_plain_literal_produces_single_literal_token():
    result = tokenize_value("APP_NAME", "myapp")
    assert len(result.tokens) == 1
    assert result.tokens[0].type == TokenType.LITERAL
    assert result.tokens[0].value == "myapp"


def test_empty_value_produces_no_tokens():
    result = tokenize_value("EMPTY", "")
    assert result.tokens == []


# ---------------------------------------------------------------------------
# variable references
# ---------------------------------------------------------------------------

def test_brace_variable_ref_detected():
    result = tokenize_value("DSN", "${HOST}")
    assert result.has_variable_refs
    assert result.variable_refs == ["HOST"]


def test_bare_variable_ref_detected():
    result = tokenize_value("DSN", "$HOST")
    assert result.has_variable_refs
    assert result.variable_refs == ["HOST"]


def test_mixed_literal_and_ref():
    result = tokenize_value("URL", "postgres://${HOST}/db")
    types = [t.type for t in result.tokens]
    assert TokenType.LITERAL in types
    assert TokenType.VARIABLE_REF in types


def test_multiple_refs_collected():
    result = tokenize_value("CONN", "${USER}:${PASS}@${HOST}")
    assert result.variable_refs == ["USER", "PASS", "HOST"]


# ---------------------------------------------------------------------------
# whitespace and special chars
# ---------------------------------------------------------------------------

def test_whitespace_token_produced():
    result = tokenize_value("MSG", "hello world")
    types = [t.type for t in result.tokens]
    assert TokenType.WHITESPACE in types


def test_special_char_token_produced():
    result = tokenize_value("OPTS", "a;b")
    types = [t.type for t in result.tokens]
    assert TokenType.SPECIAL in types


# ---------------------------------------------------------------------------
# TokenizeResult properties
# ---------------------------------------------------------------------------

def test_has_variable_refs_false_for_plain_value():
    result = tokenize_value("X", "plain")
    assert not result.has_variable_refs


def test_literal_count():
    result = tokenize_value("URL", "${SCHEME}://host")
    assert result.literal_count >= 1


def test_raw_value_preserved():
    raw = "${A}_suffix"
    result = tokenize_value("K", raw)
    assert result.raw_value == raw


def test_key_stored_on_result():
    result = tokenize_value("MY_KEY", "value")
    assert result.key == "MY_KEY"
