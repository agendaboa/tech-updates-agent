"""Build Slack Block Kit payload and POST to Incoming Webhook."""

import os
from datetime import date
from typing import Any

import requests


def _build_blocks(items: list[dict[str, str]], header_title: str | None = None) -> list[dict[str, Any]]:
    """Build Slack Block Kit blocks: header + one section per item (title as link, summary, link)."""
    blocks: list[dict[str, Any]] = []

    title = header_title or f"Tech updates for {date.today().isoformat()}"
    blocks.append({
        "type": "header",
        "text": {"type": "plain_text", "text": title, "emoji": True},
    })
    blocks.append({"type": "divider"})

    for item in items:
        title_text = (item.get("title") or "No title").strip()
        link = (item.get("link") or "").strip()
        summary = (item.get("summary") or "").strip()

        if not link or not link.startswith(("http://", "https://")):
            continue

        section: dict[str, Any] = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{link}|{title_text}>*\n{summary}\n<{link}|Read more>",
            },
        }
        blocks.append(section)

    return blocks


def send_to_slack(
    items: list[dict[str, str]],
    webhook_url: str | None = None,
    header_title: str | None = None,
) -> bool:
    """
    Send items to Slack via Incoming Webhook.
    webhook_url defaults to env SLACK_WEBHOOK_URL.
    Returns True on success, False otherwise.
    """
    url = (webhook_url or os.environ.get("SLACK_WEBHOOK_URL") or "").strip()
    if not url or not url.startswith("https://"):
        return False

    if not items:
        return True

    blocks = _build_blocks(items, header_title=header_title)
    payload = {"blocks": blocks}

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return True
    except Exception:
        return False
