"""Optional scraper for sites without RSS. One function per known site; every item must have a link."""

# Placeholder: no scrape targets in config by default.
# Add site-specific fetchers here when needed, e.g.:
#
# def fetch_example_blog(url: str, max_items: int = 5) -> list[dict[str, str]]:
#     ...  # use httpx + beautifulsoup4; return [{title, link, published, summary, source}]
#     return items


def fetch_scrape_targets(target_configs: list[dict]) -> list[dict[str, str]]:
    """
    Run configured scrape targets and return normalized items.
    Each item must have a valid 'link'. Target config format is TBD per site.
    """
    if not target_configs:
        return []
    # When scrape targets are added to config, dispatch to site-specific fetchers here.
    return []
