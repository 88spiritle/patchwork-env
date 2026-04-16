"""Tests for patchwork_env.template_formatter."""
from __future__ import annotations

import pytest
from patchwork_env.env_template import EnvTemplate, TemplateEntry
from patchwork_env.template_formatter import format_template, format_template_summary


def _tmpl(keys: list[str], required_flags: list[bool] | None = None) -> EnvTemplate:
    if required_flags is None:
        required_flags = [True] * len(keys)
    entries = [
        TemplateEntry(key=k, placeholder=f"<{k}>", required=r)
        for k, r in zip(keys, required_flags)
    ]
    return EnvTemplate(name="test_template", entries=entries)


class TestFormatTemplate:
    def test_contains_template_name(self):
        output = format_template(_tmpl(["A"]))
        assert "test_template" in output

    def test_shows_all_keys(self):
        output = format_template(_tmpl(["FOO", "BAR", "BAZ"]))
        assert "FOO" in output
        assert "BAR" in output
        assert "BAZ" in output

    def test_shows_placeholders(self):
        output = format_template(_tmpl(["PORT"]))
        assert "<PORT>" in output

    def test_required_tag_present(self):
        output = format_template(_tmpl(["X"], required_flags=[True]))
        assert "required" in output

    def test_optional_tag_present(self):
        output = format_template(_tmpl(["Y"], required_flags=[False]))
        assert "optional" in output

    def test_empty_template_shows_no_entries_message(self):
        output = format_template(EnvTemplate(name="empty", entries=[]))
        assert "no entries" in output

    def test_comment_is_shown(self):
        t = EnvTemplate(
            name="t",
            entries=[TemplateEntry(key="K", placeholder="<K>", comment="my note")],
        )
        output = format_template(t)
        assert "my note" in output


class TestFormatTemplateSummary:
    def test_contains_name(self):
        summary = format_template_summary(_tmpl(["A", "B"]))
        assert "test_template" in summary

    def test_shows_total_count(self):
        summary = format_template_summary(_tmpl(["A", "B", "C"]))
        assert "3" in summary

    def test_shows_required_count(self):
        summary = format_template_summary(_tmpl(["A", "B"], [True, False]))
        assert "1" in summary

    def test_summary_is_single_line(self):
        summary = format_template_summary(_tmpl(["X"]))
        assert "\n" not in summary.strip()
