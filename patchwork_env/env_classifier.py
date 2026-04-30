"""Classify .env entries into semantic categories based on key naming patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from patchwork_env.parser import EnvEntry


class Category(str, Enum):
    DATABASE = "database"
    AUTH = "auth"
    NETWORK = "network"
    LOGGING = "logging"
    FEATURE_FLAG = "feature_flag"
    STORAGE = "storage"
    MISC = "misc"


_PATTERNS: List[tuple[Category, List[str]]] = [
    (Category.DATABASE, ["DB_", "DATABASE_", "POSTGRES", "MYSQL", "MONGO", "REDIS", "SQL"]),
    (Category.AUTH, ["AUTH_", "JWT_", "SECRET", "TOKEN", "PASSWORD", "API_KEY", "OAUTH"]),
    (Category.NETWORK, ["HOST", "PORT", "URL", "ENDPOINT", "DOMAIN", "PROXY", "CORS"]),
    (Category.LOGGING, ["LOG_", "LOGGING_", "SENTRY", "DEBUG", "TRACE", "VERBOSE"]),
    (Category.FEATURE_FLAG, ["FEATURE_", "FLAG_", "ENABLE_", "DISABLE_", "FF_"]),
    (Category.STORAGE, ["S3_", "BUCKET_", "STORAGE_", "CDN_", "UPLOAD_", "FILE_"]),
]


def classify_key(key: str) -> Category:
    """Return the best-matching Category for a given env key."""
    upper = key.upper()
    for category, patterns in _PATTERNS:
        if any(upper.startswith(p) or p in upper for p in patterns):
            return category
    return Category.MISC


@dataclass
class ClassifiedEntry:
    entry: EnvEntry
    category: Category

    def __repr__(self) -> str:  # pragma: no cover
        return f"ClassifiedEntry(key={self.entry.key!r}, category={self.category.value})"


@dataclass
class ClassificationReport:
    filename: str
    entries: List[ClassifiedEntry] = field(default_factory=list)

    def by_category(self) -> Dict[Category, List[ClassifiedEntry]]:
        result: Dict[Category, List[ClassifiedEntry]] = {c: [] for c in Category}
        for ce in self.entries:
            result[ce.category].append(ce)
        return result

    @property
    def category_counts(self) -> Dict[str, int]:
        counts = {}
        for ce in self.entries:
            counts[ce.category.value] = counts.get(ce.category.value, 0) + 1
        return counts


def classify_entries(entries: List[EnvEntry], filename: str = "") -> ClassificationReport:
    """Classify a list of EnvEntry objects and return a ClassificationReport."""
    classified = [
        ClassifiedEntry(entry=e, category=classify_key(e.key))
        for e in entries
        if e.key is not None
    ]
    return ClassificationReport(filename=filename, entries=classified)
