"""Tests for patchwork_env.env_template."""
from __future__ import annotations

import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_template import (
    TemplateEntry,
    EnvTemplate,
    build_template,
    template_to_text,
)


def _entry(key: str, value: str = "val", comment: str | None = None) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=comment, raw=f"{key}={value}")


def _blank() -> EnvEntry:
    return EnvEntry(key=None, value=None, comment=None, raw="")


class TestBuildTemplate:
    def test_returns_env_template(self):
        t = build_template([], name="test")
        assert isinstance(t, EnvTemplate)

    def test_name_is_set(self):
        t = build_template([], name="myenv")
        assert t.name == "myenv"

    def test_blank_lines_are_skipped(self):
        entries = [_blank(), _entry("FOO"), _blank()]
        t = build_template(entries)
        assert t.keys() == ["FOO"]

    def test_placeholder_format(self):
        entries = [_entry("DB_HOST", "localhost")]
        t = build_template(entries)
        assert t.entries[0].placeholder == "<DB_HOST>"

    def test_comment_is_preserved(self):
        entries = [_entry("API_KEY", "secret", comment="your api key")]
        t = build_template(entries)
        assert t.entries[0].comment == "your api key"

    def test_all_entries_required_by_default(self):
        entries = [_entry("A"), _entry("B")]
        t = build_template(entries)
        assert all(e.required for e in t.entries)

    def test_keys_method(self):
        entries = [_entry("X"), _entry("Y"), _entry("Z")]
        t = build_template(entries)
        assert t.keys() == ["X", "Y", "Z"]

    def test_get_existing_key(self):
        entries = [_entry("PORT", "8080")]
        t = build_template(entries)
        result = t.get("PORT")
        assert result is not None
        assert result.key == "PORT"

    def test_get_missing_key_returns_none(self):
        t = build_template([])
        assert t.get("MISSING") is None


class TestTemplateToText:
    def test_empty_template_produces_empty_string(self):
        t = EnvTemplate(name="empty", entries=[])
        assert template_to_text(t) == ""

    def test_key_uses_placeholder(self):
        t = EnvTemplate(
            name="t",
            entries=[TemplateEntry(key="HOST", placeholder="<HOST>")],
        )
        text = template_to_text(t)
        assert "HOST=<HOST>" in text

    def test_comment_appears_before_key(self):
        t = EnvTemplate(
            name="t",
            entries=[TemplateEntry(key="A", placeholder="<A>", comment="note")],
        )
        text = template_to_text(t)
        lines = text.splitlines()
        comment_idx = next(i for i, l in enumerate(lines) if "note" in l)
        key_idx = next(i for i, l in enumerate(lines) if "A=<A>" in l)
        assert comment_idx < key_idx

    def test_output_ends_with_newline(self):
        t = EnvTemplate(
            name="t",
            entries=[TemplateEntry(key="K", placeholder="<K>")],
        )
        assert template_to_text(t).endswith("\n")
