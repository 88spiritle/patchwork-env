"""Tokenize .env file values into typed segments."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TokenType(str, Enum):
    LITERAL = "literal"
    VARIABLE_REF = "variable_ref"
    WHITESPACE = "whitespace"
    SPECIAL = "special"


@dataclass
class Token:
    type: TokenType
    value: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"Token({self.type.value}, {self.value!r})"


@dataclass
class TokenizeResult:
    key: str
    raw_value: str
    tokens: List[Token] = field(default_factory=list)

    @property
    def has_variable_refs(self) -> bool:
        return any(t.type == TokenType.VARIABLE_REF for t in self.tokens)

    @property
    def variable_refs(self) -> List[str]:
        return [t.value for t in self.tokens if t.type == TokenType.VARIABLE_REF]

    @property
    def literal_count(self) -> int:
        return sum(1 for t in self.tokens if t.type == TokenType.LITERAL)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TokenizeResult(key={self.key!r}, tokens={len(self.tokens)})"


_SPECIAL_CHARS = frozenset("!@#%^&*()[]{};:,<>?/|\\")


def tokenize_value(key: str, raw_value: str) -> TokenizeResult:
    """Split *raw_value* into typed Token segments."""
    tokens: List[Token] = []
    buf = ""
    i = 0
    while i < len(raw_value):
        # Variable reference: ${VAR} or $VAR
        if raw_value[i] == "$":
            if buf:
                tokens.append(Token(TokenType.LITERAL, buf))
                buf = ""
            i += 1
            if i < len(raw_value) and raw_value[i] == "{":
                end = raw_value.find("}", i)
                if end == -1:
                    ref = raw_value[i + 1:]
                    i = len(raw_value)
                else:
                    ref = raw_value[i + 1: end]
                    i = end + 1
            else:
                j = i
                while j < len(raw_value) and (raw_value[j].isalnum() or raw_value[j] == "_"):
                    j += 1
                ref = raw_value[i:j]
                i = j
            tokens.append(Token(TokenType.VARIABLE_REF, ref))
        elif raw_value[i] == " ":
            if buf:
                tokens.append(Token(TokenType.LITERAL, buf))
                buf = ""
            tokens.append(Token(TokenType.WHITESPACE, " "))
            i += 1
        elif raw_value[i] in _SPECIAL_CHARS:
            if buf:
                tokens.append(Token(TokenType.LITERAL, buf))
                buf = ""
            tokens.append(Token(TokenType.SPECIAL, raw_value[i]))
            i += 1
        else:
            buf += raw_value[i]
            i += 1
    if buf:
        tokens.append(Token(TokenType.LITERAL, buf))
    return TokenizeResult(key=key, raw_value=raw_value, tokens=tokens)
