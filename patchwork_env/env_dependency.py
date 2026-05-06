"""Detect and report dependencies between .env keys.

A dependency exists when a key's value references another key via
${OTHER_KEY} or $OTHER_KEY interpolation syntax.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Set
import re

_REF_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}|\$([A-Z_][A-Z0-9_]*)")


def _refs_in_value(value: str) -> List[str]:
    """Return all key names referenced inside *value*."""
    return [
        m.group(1) or m.group(2)
        for m in _REF_RE.finditer(value)
    ]


@dataclass
class DependencyEdge:
    source_key: str
    target_key: str
    defined: bool  # True when target_key exists in the same file

    def __repr__(self) -> str:  # pragma: no cover
        arrow = "->" if self.defined else "-?>"
        return f"DependencyEdge({self.source_key!r} {arrow} {self.target_key!r})"


@dataclass
class DependencyReport:
    filename: str
    edges: List[DependencyEdge] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    @property
    def has_missing(self) -> bool:
        return any(not e.defined for e in self.edges)

    @property
    def missing_edges(self) -> List[DependencyEdge]:
        return [e for e in self.edges if not e.defined]

    @property
    def defined_edges(self) -> List[DependencyEdge]:
        return [e for e in self.edges if e.defined]

    def dependency_map(self) -> Dict[str, Set[str]]:
        """Return {source_key: {target_keys}} for all edges."""
        result: Dict[str, Set[str]] = {}
        for edge in self.edges:
            result.setdefault(edge.source_key, set()).add(edge.target_key)
        return result

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DependencyReport(filename={self.filename!r}, "
            f"edges={len(self.edges)}, missing={len(self.missing_edges)})"
        )


def analyse_dependencies(entries, filename: str = "<env>") -> DependencyReport:
    """Build a *DependencyReport* from a sequence of *EnvEntry* objects."""
    key_set: Set[str] = {e.key for e in entries if e.key}
    report = DependencyReport(filename=filename)
    for entry in entries:
        if not entry.key:
            continue
        for ref in _refs_in_value(entry.value or ""):
            report.edges.append(
                DependencyEdge(
                    source_key=entry.key,
                    target_key=ref,
                    defined=ref in key_set,
                )
            )
    return report
