"""Cross-environment value comparison for the same key across multiple env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyComparison:
    """Comparison result for a single key across multiple environments."""
    key: str
    values: Dict[str, Optional[str]]  # env_name -> value

    def __repr__(self) -> str:
        pairs = ", ".join(f"{e}={v!r}" for e, v in self.values.items())
        return f"KeyComparison(key={self.key!r}, {pairs})"

    @property
    def is_consistent(self) -> bool:
        """True when all environments share the same value."""
        vals = [v for v in self.values.values() if v is not None]
        return len(set(vals)) <= 1

    @property
    def missing_in(self) -> List[str]:
        """Environments where this key is absent."""
        return [env for env, val in self.values.items() if val is None]

    @property
    def unique_values(self) -> List[str]:
        return list({v for v in self.values.values() if v is not None})


@dataclass
class CrossEnvReport:
    """Report comparing a key across several environments."""
    key: str
    env_names: List[str]
    comparisons: List[KeyComparison] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"CrossEnvReport(key={self.key!r}, envs={self.env_names}, "
            f"entries={len(self.comparisons)})"
        )

    @property
    def inconsistent_keys(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if not c.is_consistent]

    @property
    def consistent_keys(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.is_consistent]


def compare_across_envs(
    env_maps: Dict[str, Dict[str, str]],
    keys: Optional[List[str]] = None,
) -> CrossEnvReport:
    """Compare values for *keys* (or all discovered keys) across *env_maps*.

    Args:
        env_maps: mapping of environment-name -> {KEY: value}.
        keys: optional explicit list of keys to compare; defaults to union of all keys.
    """
    env_names = list(env_maps.keys())
    all_keys: List[str] = keys if keys is not None else sorted(
        {k for env in env_maps.values() for k in env}
    )

    comparisons: List[KeyComparison] = []
    for key in all_keys:
        values = {env: env_maps[env].get(key) for env in env_names}
        comparisons.append(KeyComparison(key=key, values=values))

    # Use a synthetic label for the report key when comparing many keys
    report_key = keys[0] if (keys and len(keys) == 1) else "*"
    return CrossEnvReport(key=report_key, env_names=env_names, comparisons=comparisons)
