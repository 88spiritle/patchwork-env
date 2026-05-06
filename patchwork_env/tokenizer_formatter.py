"""Format TokenizeResult objects for terminal display."""
from __future__ import annotations

from typing import List

from .env_tokenizer import TokenizeResult, TokenType


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _render_token(value: str, ttype: TokenType) -> str:
    if ttype == TokenType.VARIABLE_REF:
        return _c(f"${{{value}}}", "36")  # cyan
    if ttype == TokenType.SPECIAL:
        return _c(value, "33")  # yellow
    if ttype == TokenType.WHITESPACE:
        return _c("·", "90")  # dark grey dot
    return value


def format_tokenize_result(result: TokenizeResult, filename: str = "") -> str:
    lines: List[str] = []
    header = f"Tokens — {result.key}"
    if filename:
        header += f"  [{filename}]"
    lines.append(_c(header, "1"))
    lines.append(_c("-" * len(header), "90"))
    for tok in result.tokens:
        label = tok.type.value.upper().ljust(14)
        rendered = _render_token(tok.value, tok.type)
        lines.append(f"  {_c(label, '90')} {rendered}")
    ref_count = len(result.variable_refs)
    lines.append("")
    lines.append(
        f"  {_c(str(len(result.tokens)), '1')} token(s), "
        f"{_c(str(ref_count), '36')} variable ref(s)"
    )
    return "\n".join(lines)


def format_tokenize_summary(results: List[TokenizeResult], filename: str = "") -> str:
    lines: List[str] = []
    title = f"Tokenize Summary — {filename}" if filename else "Tokenize Summary"
    lines.append(_c(title, "1;4"))
    with_refs = [r for r in results if r.has_variable_refs]
    lines.append(f"  Total keys   : {len(results)}")
    lines.append(f"  With var refs: {len(with_refs)}")
    if with_refs:
        lines.append(_c("  Keys with variable references:", "90"))
        for r in with_refs:
            refs = ", ".join(r.variable_refs)
            lines.append(f"    {_c(r.key, '36')} → {refs}")
    return "\n".join(lines)
