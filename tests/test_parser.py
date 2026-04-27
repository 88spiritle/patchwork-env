"""Tests for patchwork_env.parser — .env file parsing logic."""

from pathlib import Path

import pytest

from patchwork_env.parser import (
    EnvEntry,
    EnvFile,
    parse_env_file,
    _strip_inline_comment,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_env_file(tmp_path: Path) -> Path:
    content = """# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp  # production db
SECRET_KEY='s3cr3t!'
EMPTY_VAR=
"""
    env_path = tmp_path / ".env"
    env_path.write_text(content, encoding="utf-8")
    return env_path


# ---------------------------------------------------------------------------
# _strip_inline_comment
# ---------------------------------------------------------------------------

class TestStripInlineComment:
    def test_plain_value_no_comment(self):
        value, comment = _strip_inline_comment("localhost")
        assert value == "localhost"
        assert comment is None

    def test_value_with_inline_comment(self):
        value, comment = _strip_inline_comment("myapp  # production db")
        assert value == "myapp"
        assert comment == "production db"

    def test_single_quoted_value(self):
        value, comment = _strip_inline_comment("'s3cr3t!'")
        assert value == "s3cr3t!"
        assert comment is None

    def test_double_quoted_value(self):
        value, comment = _strip_inline_comment('"hello world"')
        assert value == "hello world"
        assert comment is None

    def test_empty_value(self):
        value, comment = _strip_inline_comment("")
        assert value == ""
        assert comment is None


# ---------------------------------------------------------------------------
# parse_env_file
# ---------------------------------------------------------------------------

class TestParseEnvFile:
    def test_returns_env_file_instance(self, simple_env_file: Path):
        result = parse_env_file(simple_env_file)
        assert isinstance(result, EnvFile)
        assert result.path == simple_env_file

    def test_parses_all_key_value_pairs(self, simple_env_file: Path):
        result = parse_env_file(simple_env_file)
        keys = [e.key for e in result.entries]
        assert "DB_HOST" in keys
        assert "DB_PORT" in keys
        assert "DB_NAME" in keys
        assert "SECRET_KEY" in keys
        assert "EMPTY_VAR" in keys

    def test_ignores_comments_and_blank_lines(self, simple_env_file: Path):
        result = parse_env_file(simple_env_file)
        assert len(result.entries) == 5  # no comment lines included

    def test_correct_values(self, simple_env_file: Path):
        result = parse_env_file(simple_env_file)
        d = result.as_dict
        assert d["DB_HOST"] == "localhost"
        assert d["DB_PORT"] == "5432"
        assert d["DB_NAME"] == "myapp"
        assert d["SECRET_KEY"] == "s3cr3t!"
        assert d["EMPTY_VAR"] == ""

    def test_raises_for_missing_file(self, tmp_path: Path):
        """parse_env_file should raise FileNotFoundError for a non-existent path."""
        missing = tmp_path / "nonexistent.env"
        with pytest.raises(FileNotFoundError):
            parse_env_file(missing)
