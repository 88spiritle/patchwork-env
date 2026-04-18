"""Compare two sets of env entries and produce a similarity report."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from patchwork_env.parser import EnvEntry


@dataclass
class ComparisonReport:
    file_a: str
    file_b: str
    common_keys: List[str] = field(default_factory=list)
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    value_matches: List[str] = field(default_factory=list)
    value_mismatches: List[str] = field(default_factory=list)

    @property
    def similarity_score(self) -> float:
        total = len(self.common_keys) + len(self.only_in_a) + len(self.only_in_b)
        if total == 0:
            return 1.0
        return round(len(self.value_matches) / total, 4)

    def __repr__(self) -> str:
        return (
            f"ComparisonReport({self.file_a!r} vs {self.file_b!r}, "
            f"score={self.similarity_score})"
        )


def compare_envs(
    entries_a: List[EnvEntry],
    entries_b: List[EnvEntry],
    file_a: str = "a",
    file_b: str = "b",
) -> ComparisonReport:
    map_a = {e.key: e.value for e in entries_a if e.key}
    map_b = {e.key: e.value for e in entries_b if e.key}

    keys_a = set(map_a)
    keys_b = set(map_b)
    common = keys_a & keys_b

    value_matches = [k for k in common if map_a[k] == map_b[k]]
    value_mismatches = [k for k in common if map_a[k] != map_b[k]]

    return ComparisonReport(
        file_a=file_a,
        file_b=file_b,
        common_keys=sorted(common),
        only_in_a=sorted(keys_a - keys_b),
        only_in_b=sorted(keys_b - keys_a),
        value_matches=sorted(value_matches),
        value_mismatches=sorted(value_mismatches),
    )
