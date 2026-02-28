#!/usr/bin/env python3
"""
AI News Fetcher
Fetches latest AI news from multiple RSS feeds and returns structured data.
"""

import feedparser
import json
import hashlib
import ssl
import urllib.request
from datetime import datetime, timezone
from dateutil import parser as dateparser
from pathlib import Path

# Fix SSL certificate issues on macOS
try:
    import certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

# Install the SSL context as the default opener
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ssl_context)
)
urllib.request.install_opener(opener)

# AI News RSS Feed Sources
RSS_FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "icon": "🚀",
        "category": "Industry"
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "icon": "⚡",
        "category": "Technology"
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "icon": "🎓",
        "category": "Research"
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "icon": "🔬",
        "category": "Research"
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "icon": "🤖",
        "category": "Technology"
    },
    {
        "name": "Ars Technica AI",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "icon": "🔧",
        "category": "Technology"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "icon": "📊",
        "category": "Industry"
    },
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/newest?q=AI+OR+LLM+OR+GPT+OR+artificial+intelligence&count=15",
        "icon": "🧡",
        "category": "Community"
    },
]


def generate_id(title: str, link: str) -> str:
    """Generate a unique ID for a news article."""
    raw = f"{title}:{link}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def parse_date(entry) -> datetime:
    """Parse date from feed entry, return UTC datetime."""
    date_str = entry.get("published") or entry.get("updated") or ""
    if date_str:
        try:
            dt = dateparser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            pass
    return datetime.now(timezone.utc)


def clean_summary(summary: str, max_length: int = 280) -> str:
    """Clean and truncate summary text."""
    import re
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", summary)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove common feed artifacts
    text = re.sub(r"\[…\]|\[&#8230;\]|&hellip;|&#8230;", "…", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > max_length:
        text = text[: max_length - 1].rsplit(" ", 1)[0] + "…"
    return text


def fetch_feed(feed_config: dict) -> list[dict]:
    """Fetch and parse a single RSS feed."""
    import requests

    articles = []
    try:
        print(f"  📡 Fetching: {feed_config['name']}...")

        # Use requests to handle SSL properly, then parse with feedparser
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AI-News-Radar/1.0; +https://github.com)"
        }
        resp = requests.get(feed_config["url"], headers=headers, timeout=15, verify=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

        if feed.bozo and not feed.entries:
            print(f"  ⚠️  Failed to parse {feed_config['name']}: {feed.bozo_exception}")
            return []

        for entry in feed.entries[:10]:  # Max 10 per source
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", entry.get("description", ""))

            if not title or not link:
                continue

            # Filter: only keep AI-related articles for general feeds
            ai_keywords = [
                "ai", "artificial intelligence", "machine learning", "deep learning",
                "neural", "llm", "gpt", "claude", "gemini", "openai", "anthropic",
                "chatbot", "generative", "transformer", "diffusion", "copilot",
                "model", "training", "inference", "reasoning", "agent",
            ]
            title_lower = title.lower()
            summary_lower = (summary or "").lower()
            combined = f"{title_lower} {summary_lower}"

            # For AI-specific feeds, keep all; for general feeds, filter
            is_ai_feed = any(
                kw in feed_config["name"].lower()
                for kw in ["ai", "artificial", "openai", "google ai"]
            )
            if not is_ai_feed:
                if not any(kw in combined for kw in ai_keywords):
                    continue

            article = {
                "id": generate_id(title, link),
                "title": title,
                "link": link,
                "summary": clean_summary(summary) if summary else "",
                "published": parse_date(entry).isoformat(),
                "source": feed_config["name"],
                "source_icon": feed_config["icon"],
                "category": feed_config["category"],
            }
            articles.append(article)

    except Exception as e:
        print(f"  ❌ Error fetching {feed_config['name']}: {e}")

    print(f"  ✅ Got {len(articles)} articles from {feed_config['name']}")
    return articles


def fetch_all_news() -> list[dict]:
    """Fetch news from all configured RSS feeds."""
    print("🔄 Fetching AI news from RSS feeds...\n")

    all_articles = []
    seen_ids = set()

    for feed_config in RSS_FEEDS:
        articles = fetch_feed(feed_config)
        for article in articles:
            if article["id"] not in seen_ids:
                seen_ids.add(article["id"])
                all_articles.append(article)

    # Sort by date, newest first
    all_articles.sort(key=lambda x: x["published"], reverse=True)

    # Cap at 60 articles
    all_articles = all_articles[:60]

    print(f"\n📰 Total: {len(all_articles)} unique articles collected")
    return all_articles


def save_news(articles: list[dict], output_path: str = "data/news.json"):
    """Save articles to JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(articles),
        "articles": articles,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 Saved to {path}")
    return data


if __name__ == "__main__":
    articles = fetch_all_news()
    save_news(articles)
