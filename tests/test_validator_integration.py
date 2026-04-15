"""Integration: parse a real .env text, then validate it."""
import textwrap

from patchwork_env.parser import parse_env_text
from patchwork_env.validator import Severity, validate_entries
from patchwork_env.reporter import format_validation_report


VALID_ENV = textwrap.dedent("""\
    APP_NAME=patchwork
    APP_ENV=production
    DB_HOST=localhost
    DB_PORT=5432
    SECRET_KEY=supersecret
""")

INVALID_ENV = textwrap.dedent("""\
    app_name=patchwork
    APP_ENV=production
    APP_ENV=staging
    EMPTY_VAL=
""")


def test_valid_env_passes_validation():
    entries = parse_env_text(VALID_ENV)
    result = validate_entries(entries)
    assert result.is_valid
    assert not result.has_warnings


def test_invalid_env_reports_errors_and_warnings():
    entries = parse_env_text(INVALID_ENV)
    result = validate_entries(entries)

    assert not result.is_valid

    severities = {i.severity for i in result.issues}
    assert Severity.ERROR in severities
    assert Severity.WARNING in severities


def test_duplicate_key_error_present():
    entries = parse_env_text(INVALID_ENV)
    result = validate_entries(entries)
    errors = [i for i in result.issues if i.severity == Severity.ERROR]
    assert any(i.key == "APP_ENV" for i in errors)


def test_lowercase_key_warning_present():
    entries = parse_env_text(INVALID_ENV)
    result = validate_entries(entries)
    warnings = [i for i in result.issues if i.severity == Severity.WARNING]
    assert any(i.key == "app_name" for i in warnings)


def test_report_generated_without_error():
    entries = parse_env_text(INVALID_ENV)
    result = validate_entries(entries)
    report = format_validation_report(result, filename=".env.test")
    assert isinstance(report, str)
    assert len(report) > 0
    assert ".env.test" in report
