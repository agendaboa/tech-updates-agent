"""Fetch and parse RSS/Atom feeds; normalize to common item shape."""

import feedparser
from typing import Any


def _normalize_item(entry: Any, source_name: str = "") -> dict[str, str] | None:
    """Normalize a feedparser entry to {title, link, published, summary}. Returns None if no link."""
    link = getattr(entry, "link", None) or (entry.get("link") if hasattr(entry, "get") else None)
    if not link or not str(link).strip().startswith(("http://", "https://")):
        return None

    title = getattr(entry, "title", None) or entry.get("title", "") if hasattr(entry, "get") else ""
    title = (title or "").strip() or "No title"

    summary = ""
    for key in ("summary", "description", "content"):
        val = getattr(entry, key, None)
        if val is None and hasattr(entry, "get"):
            val = entry.get(key)
        if val:
            if hasattr(val, "value"):
                summary = (val.value or "").strip()
            else:
                summary = (str(val) or "").strip()
            break

    published = ""
    for key in ("published", "updated"):
        val = getattr(entry, key, None)
        if val is None and hasattr(entry, "get"):
            val = entry.get(key)
        if val:
            published = str(val).strip()
            break

    return {
        "title": title,
        "link": link.strip(),
        "published": published,
        "summary": summary,
        "source": source_name,
    }


def fetch_feed(url: str, name: str = "", max_items: int = 10) -> list[dict[str, str]]:
    """
    Fetch a single RSS/Atom feed and return normalized items.
    Only returns items that have a valid link; limits to max_items per feed.
    """
    try:
        parsed = feedparser.parse(url)
    except Exception:
        return []

    items: list[dict[str, str]] = []
    source_name = name or url
    entries = getattr(parsed, "entries", []) or []

    for entry in entries[: max_items * 2]:
        if len(items) >= max_items:
            break
        normalized = _normalize_item(entry, source_name)
        if normalized:
            items.append(normalized)

    return items


def fetch_all_feeds(feed_configs: list[dict]) -> list[dict[str, str]]:
    """
    Fetch all configured RSS feeds and return a single list of normalized items.
    Each config can have: url (required), name (optional), max_items (optional).
    """
    all_items: list[dict[str, str]] = []
    for cfg in feed_configs:
        url = cfg.get("url") or cfg.get("link")
        if not url:
            continue
        name = cfg.get("name", "")
        max_items = cfg.get("max_items", 10)
        all_items.extend(fetch_feed(url, name=name, max_items=max_items))
    return all_items
