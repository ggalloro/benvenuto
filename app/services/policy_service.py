"""Read the company policies (markdown files with a small front matter)."""

import re

import markdown as md

from app import config
from app.data_service import NotFound

_FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def _parse(path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta = {}
    match = _FRONT_MATTER.match(text)
    if match:
        for line in match.group(1).splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
        text = text[match.end():]
    return dict(name=path.stem, title=meta.get("title", path.stem), summary=meta.get("summary", ""),
                content_markdown=text.strip())


def list_policies() -> list[dict]:
    return [{k: v for k, v in _parse(p).items() if k != "content_markdown"}
            for p in sorted(config.POLICIES_DIR.glob("*.md"))]


def get_policy(name: str) -> dict:
    path = config.POLICIES_DIR / f"{name}.md"
    if not re.fullmatch(r"[a-z0-9-]+", name) or not path.exists():
        raise NotFound(f"Policy {name} not found")
    return _parse(path)


def render_policy_html(name: str) -> str:
    return md.markdown(get_policy(name)["content_markdown"], extensions=["tables"])
