"""env_requirer.py – check that required keys are present in an env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class RequirementHit:
    key: str
    found: bool
    value: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        status = "OK" if self.found else "MISSING"
        return f"<RequirementHit {self.key}={status}>"


@dataclass
class RequirementReport:
    filename: str
    hits: List[RequirementHit] = field(default_factory=list)

    @property
    def missing(self) -> List[RequirementHit]:
        return [h for h in self.hits if not h.found]

    @property
    def satisfied(self) -> List[RequirementHit]:
        return [h for h in self.hits if h.found]

    @property
    def is_complete(self) -> bool:
        return len(self.missing) == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RequirementReport file={self.filename!r} "
            f"complete={self.is_complete} missing={len(self.missing)}>"
        )


def check_requirements(
    required_keys: Iterable[str],
    entries: Iterable[EnvEntry],
    filename: str = "<unknown>",
) -> RequirementReport:
    """Return a RequirementReport describing which required keys are present."""
    required = [k.upper() for k in required_keys]
    entry_map = {e.key.upper(): e for e in entries if e.key}

    hits: List[RequirementHit] = []
    for key in required:
        entry = entry_map.get(key)
        hits.append(
            RequirementHit(
                key=key,
                found=entry is not None,
                value=entry.value if entry else None,
            )
        )

    return RequirementReport(filename=filename, hits=hits)
