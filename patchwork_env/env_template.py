"""Template generation: produce a .env.template from parsed entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    comment: Optional[str] = None
    required: bool = True

    def __repr__(self) -> str:  # pragma: no cover
        return f"TemplateEntry(key={self.key!r}, placeholder={self.placeholder!r})"


@dataclass
class EnvTemplate:
    name: str
    entries: List[TemplateEntry] = field(default_factory=list)

    def keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def get(self, key: str) -> Optional[TemplateEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def build_template(entries: List[EnvEntry], name: str = "template") -> EnvTemplate:
    """Convert a list of parsed EnvEntry objects into a template.

    Values are replaced with ``<KEY>`` placeholders.  Blank/comment-only
    lines are skipped.
    """
    template_entries: List[TemplateEntry] = []
    for entry in entries:
        if entry.key is None:
            continue
        placeholder = f"<{entry.key}>"
        template_entries.append(
            TemplateEntry(
                key=entry.key,
                placeholder=placeholder,
                comment=entry.comment,
                required=True,
            )
        )
    return EnvTemplate(name=name, entries=template_entries)


def template_to_text(template: EnvTemplate) -> str:
    """Render an EnvTemplate back to .env.template file content."""
    lines: List[str] = []
    for entry in template.entries:
        if entry.comment:
            lines.append(f"# {entry.comment}")
        lines.append(f"{entry.key}={entry.placeholder}")
    return "\n".join(lines) + "\n" if lines else ""
