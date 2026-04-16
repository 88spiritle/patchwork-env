"""Format EnvScore results for terminal output."""
from __future__ import annotations
from patchwork_env.env_scorer import EnvScore

_GRADE_COLOR = {
    "A": "\033[92m",
    "B": "\033[96m",
    "C": "\033[93m",
    "D": "\033[33m",
    "F": "\033[91m",
}
_RESET = "\033[0m"


def _c(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}"


def format_score(score: EnvScore, *, color: bool = True) -> str:
    grade_color = _GRADE_COLOR.get(score.grade, "") if color else ""
    grade_str = _c(score.grade, grade_color) if color else score.grade
    lines = [
        f"=== Quality Score: {score.filename} ===",
        f"  Grade : {grade_str}",
        f"  Score : {score.breakdown.total}/100",
        f"  Lint penalty       : -{score.breakdown.lint_penalty}",
        f"  Validation penalty : -{score.breakdown.validation_penalty}",
        f"  Bonus              : +{score.breakdown.bonus}",
        "",
        "  Notes:",
    ]
    for note in score.notes:
        lines.append(f"    • {note}")
    return "\n".join(lines)


def format_score_summary(scores: list[EnvScore]) -> str:
    lines = ["=== Score Summary ==="]
    for s in scores:
        lines.append(f"  {s.filename:<30} grade={s.grade}  score={s.breakdown.total}")
    avg = sum(s.breakdown.total for s in scores) // len(scores) if scores else 0
    lines.append(f"\n  Average score: {avg}")
    return "\n".join(lines)
