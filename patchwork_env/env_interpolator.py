"""Resolve variable interpolation (${VAR}) within .env entries."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass
class InterpolationWarning:
    key: str
    ref: str
    message: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"InterpolationWarning({self.key!r} -> {self.ref!r}: {self.message})"


@dataclass
class InterpolatedEntry:
    original: EnvEntry
    resolved_value: str
    warnings: List[InterpolationWarning] = field(default_factory=list)

    @property
    def key(self) -> str:
        return self.original.key

    def __repr__(self) -> str:  # pragma: no cover
        return f"InterpolatedEntry({self.key!r}={self.resolved_value!r})"


def interpolate(
    entries: List[EnvEntry],
    extra: Optional[Dict[str, str]] = None,
) -> List[InterpolatedEntry]:
    """Resolve ${VAR} references using the entry list and optional extra mapping."""
    lookup: Dict[str, str] = {e.key: e.value for e in entries}
    if extra:
        lookup.update(extra)

    results: List[InterpolatedEntry] = []
    for entry in entries:
        warnings: List[InterpolationWarning] = []
        resolved = _resolve(entry.key, entry.value, lookup, warnings)
        results.append(InterpolatedEntry(original=entry, resolved_value=resolved, warnings=warnings))
    return results


def _resolve(
    key: str,
    value: str,
    lookup: Dict[str, str],
    warnings: List[InterpolationWarning],
) -> str:
    def replacer(m: re.Match) -> str:
        ref = m.group(1)
        if ref == key:
            warnings.append(InterpolationWarning(key, ref, "self-referential variable"))
            return m.group(0)
        if ref not in lookup:
            warnings.append(InterpolationWarning(key, ref, f"undefined variable '{ref}'"))
            return m.group(0)
        return lookup[ref]

    return _REF_RE.sub(replacer, value)
