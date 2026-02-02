"""Orchestrate: load config, fetch RSS (and optional scrape), process, send to Slack."""

import sys
from pathlib import Path
from urllib.parse import quote_plus

import yaml

from fetchers.rss import fetch_all_feeds
from fetchers.scraper import fetch_scrape_targets
from summarizer import process_items
from slack import send_to_slack

# Google News RSS search: topic name → feed URL (no config URLs needed).
DEFAULT_MAX_ITEMS_PER_TOPIC = 5


def load_config(config_path: str | Path | None = None) -> dict:
    """Load config/sources.yaml; use config_path if provided."""
    if config_path is None:
        base = Path(__file__).resolve().parent.parent
        config_path = base / "config" / "sources.yaml"
    path = Path(config_path)
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def topic_to_feed(topic: str, max_items: int = DEFAULT_MAX_ITEMS_PER_TOPIC) -> dict:
    """Turn a topic name into an RSS feed config. Uses Google News search RSS; no URL in config."""
    q = quote_plus(topic.strip())
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    return {"url": url, "name": topic.strip(), "max_items": max_items}


def topics_to_rss_feeds(topics: list[str], max_items_per_topic: int = DEFAULT_MAX_ITEMS_PER_TOPIC) -> list[dict]:
    """Convert topic names to RSS feed configs. No URLs in config—feeds are derived from topics."""
    feeds: list[dict] = []
    for topic in topics:
        if not topic or not isinstance(topic, str):
            continue
        feeds.append(topic_to_feed(topic, max_items_per_topic))
    return feeds


def run(config_path: str | Path | None = None) -> bool:
    """
    Run the agent: fetch from RSS (and optional scrape), dedup/summarize, send to Slack.
    Returns True if Slack send succeeded (or there were no items), False on failure.
    """
    config = load_config(config_path)
    topics = config.get("topics") or []
    max_items_per_topic = config.get("max_items_per_topic", DEFAULT_MAX_ITEMS_PER_TOPIC)
    rss_feeds = topics_to_rss_feeds(topics, max_items_per_topic)
    scrape_targets = config.get("scrape_targets") or []
    max_items_per_run = config.get("max_items_per_run", 15)
    summary_max_length = config.get("summary_max_length", 160)

    all_items: list[dict] = []
    all_items.extend(fetch_all_feeds(rss_feeds))
    all_items.extend(fetch_scrape_targets(scrape_targets))

    processed = process_items(
        all_items,
        summary_max_length=summary_max_length,
        max_items=max_items_per_run,
    )

    return send_to_slack(processed)


def main() -> None:
    """Entry point for CLI and GitHub Actions."""
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        config = load_config()
        topics = config.get("topics") or []
        max_items_per_topic = config.get("max_items_per_topic", DEFAULT_MAX_ITEMS_PER_TOPIC)
        rss_feeds = topics_to_rss_feeds(topics, max_items_per_topic)
        scrape_targets = config.get("scrape_targets") or []
        max_items_per_run = config.get("max_items_per_run", 15)
        summary_max_length = config.get("summary_max_length", 160)
        all_items: list[dict] = []
        all_items.extend(fetch_all_feeds(rss_feeds))
        all_items.extend(fetch_scrape_targets(scrape_targets))
        processed = process_items(
            all_items,
            summary_max_length=summary_max_length,
            max_items=max_items_per_run,
        )
        lines = [f"Fetched {len(all_items)} items, {len(processed)} after dedup/summarize."]
        for i, item in enumerate(processed, 1):
            lines.append(f"\n{i}. {item.get('title', '')}")
            lines.append(f"   {item.get('link', '')}")
            s = item.get("summary", "")
            lines.append(f"   {s[:80] + '...' if len(s) > 80 else s}")
        out = "\n".join(lines)
        print(out)
        out_path = Path(__file__).resolve().parent.parent / "dry_run_output.txt"
        out_path.write_text(out, encoding="utf-8")
        print(f"\n(Wrote {out_path})")
        sys.exit(0)
    ok = run()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
