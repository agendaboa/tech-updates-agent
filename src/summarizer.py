"""Deduplicate by link, produce short summaries, enforce link per item."""

import re
from typing import Any


def _normalize_url(url: str) -> str:
    """Normalize URL for dedup: strip trailing slash and fragment, lowercase scheme/host."""
    if not url or not isinstance(url, str):
        return ""
    u = url.strip()
    if not u.startswith(("http://", "https://")):
        return ""
    u = re.sub(r"#.*$", "", u)
    u = u.rstrip("/")
    return u


def _has_valid_link(item: dict[str, Any]) -> bool:
    link = item.get("link") or item.get("url")
    if not link or not isinstance(link, str):
        return False
    return link.strip().startswith(("http://", "https://"))


def _short_summary(text: str, max_length: int) -> str:
    """Truncate to max_length chars; add '...' if truncated. Strip HTML-ish content."""
    if not text or not isinstance(text, str):
        return ""
    # Simple strip of common HTML tags for RSS content
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 3].rstrip() + "..."


def process_items(
    items: list[dict[str, Any]],
    summary_max_length: int = 160,
    max_items: int = 15,
) -> list[dict[str, str]]:
    """
    - Drop items without a valid link.
    - Deduplicate by normalized link (keep first occurrence).
    - Shorten summary to summary_max_length.
    - Return at most max_items, in original order.
    """
    seen: set[str] = set()
    result: list[dict[str, str]] = []

    for item in items:
        if not _has_valid_link(item):
            continue
        link = (item.get("link") or item.get("url") or "").strip()
        norm = _normalize_url(link)
        if not norm or norm in seen:
            continue
        seen.add(norm)

        title = (item.get("title") or "").strip() or "No title"
        raw_summary = (item.get("summary") or item.get("description") or "").strip()
        short = _short_summary(raw_summary, summary_max_length)

        result.append({
            "title": title,
            "link": link,
            "summary": short,
        })
        if len(result) >= max_items:
            break

    return result
