"""Format a ComparisonReport for terminal output."""
from patchwork_env.env_comparator import ComparisonReport


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_comparison(report: ComparisonReport) -> str:
    lines = [
        _c("1", f"Comparing: {report.file_a}  vs  {report.file_b}"),
        "",
        f"  Similarity score : {_c('36', str(report.similarity_score))}",
        f"  Common keys      : {len(report.common_keys)}",
        f"  Only in A        : {len(report.only_in_a)}",
        f"  Only in B        : {len(report.only_in_b)}",
        f"  Value matches    : {len(report.value_matches)}",
        f"  Value mismatches : {len(report.value_mismatches)}",
    ]
    if report.only_in_a:
        lines.append("")
        lines.append(_c("33", "  Keys only in A:"))
        for k in report.only_in_a:
            lines.append(f"    - {k}")
    if report.only_in_b:
        lines.append("")
        lines.append(_c("34", "  Keys only in B:"))
        for k in report.only_in_b:
            lines.append(f"    + {k}")
    if report.value_mismatches:
        lines.append("")
        lines.append(_c("31", "  Value mismatches:"))
        for k in report.value_mismatches:
            lines.append(f"    ~ {k}")
    return "\n".join(lines)


def format_comparison_summary(report: ComparisonReport) -> str:
    score = report.similarity_score
    colour = "32" if score >= 0.8 else "33" if score >= 0.5 else "31"
    return _c(colour, f"Similarity: {score} | mismatches: {len(report.value_mismatches)} | unique-A: {len(report.only_in_a)} | unique-B: {len(report.only_in_b)}")
