"""Lint .env files for common style and correctness issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from patchwork_env.parser import EnvEntry


class LintCode(str, Enum):
    UPPERCASE_KEY = "E001"          # keys should be UPPER_SNAKE_CASE
    NO_VALUE = "W001"               # key present but value is empty string
    WHITESPACE_IN_KEY = "E002"      # key contains spaces
    LEADING_TRAILING_SPACE = "W002" # unquoted value has leading/trailing space
    DOUBLE_UNDERSCORE = "W003"      # key contains __ (often a typo)
    VERY_LONG_VALUE = "W004"        # value exceeds 256 characters


@dataclass
class LintIssue:
    line: int
    code: LintCode
    key: str
    message: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"LintIssue(line={self.line}, code={self.code.value}, key={self.key!r})"


@dataclass
class LintResult:
    filename: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.code.value.startswith("E")]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.code.value.startswith("W")]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def lint_entries(entries: List[EnvEntry], filename: str = "<unknown>") -> LintResult:
    """Run all lint rules over a list of EnvEntry objects."""
    result = LintResult(filename=filename)

    for entry in entries:
        if entry.is_comment or entry.is_blank:
            continue

        key = entry.key
        value = entry.value or ""
        lineno = entry.lineno

        if " " in key or "\t" in key:
            result.issues.append(LintIssue(
                line=lineno, code=LintCode.WHITESPACE_IN_KEY, key=key,
                message=f"Key '{key}' contains whitespace."
            ))

        if key != key.upper():
            result.issues.append(LintIssue(
                line=lineno, code=LintCode.UPPERCASE_KEY, key=key,
                message=f"Key '{key}' is not UPPER_SNAKE_CASE."
            ))

        if "__" in key:
            result.issues.append(LintIssue(
                line=lineno, code=LintCode.DOUBLE_UNDERSCORE, key=key,
                message=f"Key '{key}' contains double underscore."
            ))

        if value == "":
            result.issues.append(LintIssue(
                line=lineno, code=LintCode.NO_VALUE, key=key,
                message=f"Key '{key}' has no value."
            ))
        else:
            if not entry.raw_value.startswith(("'", '"')) and value != value.strip():
                result.issues.append(LintIssue(
                    line=lineno, code=LintCode.LEADING_TRAILING_SPACE, key=key,
                    message=f"Unquoted value for '{key}' has leading/trailing whitespace."
                ))
            if len(value) > 256:
                result.issues.append(LintIssue(
                    line=lineno, code=LintCode.VERY_LONG_VALUE, key=key,
                    message=f"Value for '{key}' exceeds 256 characters ({len(value)})."
                ))

    return result
