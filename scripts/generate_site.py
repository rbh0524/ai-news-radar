#!/usr/bin/env python3
"""
Static Site Generator
Reads news data and generates the static HTML page using Jinja2 templates.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dateutil import parser as dateparser

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "docs"


def format_date(iso_string: str) -> str:
    """Format ISO date string to readable display."""
    try:
        dt = dateparser.parse(iso_string)
        now = datetime.now(timezone.utc)
        diff = now - dt

        if diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} 分鐘前"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} 小時前"
        elif diff.days < 7:
            return f"{diff.days} 天前"
        else:
            return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return iso_string


def load_news() -> dict:
    """Load news data from JSON file."""
    news_file = DATA_DIR / "news.json"
    if not news_file.exists():
        print("⚠️  No news data found. Run fetch_news.py first.")
        return {"generated_at": datetime.now(timezone.utc).isoformat(), "articles": []}

    with open(news_file, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_site():
    """Generate the static HTML site."""
    print("🔨 Generating static site...\n")

    # Load data
    news_data = load_news()
    articles = news_data.get("articles", [])
    generated_at = news_data.get("generated_at", datetime.now(timezone.utc).isoformat())

    # Add display-formatted date to each article
    for article in articles:
        article["published_display"] = format_date(article["published"])

    # Compute template variables
    sources = sorted(set(a["source"] for a in articles))
    categories = sorted(set(a["category"] for a in articles))

    # Format generation time for display
    try:
        gen_dt = dateparser.parse(generated_at)
        generated_at_display = gen_dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        generated_at_display = generated_at

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("index.html")

    # Render
    html = template.render(
        articles=articles,
        sources=sources,
        categories=categories,
        generated_at=generated_at,
        generated_at_display=generated_at_display,
        now=datetime.now(timezone.utc),
    )

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Generated: {output_file}")
    print(f"   📰 {len(articles)} articles")
    print(f"   📡 {len(sources)} sources")
    print(f"   🏷️  {len(categories)} categories")
    print(f"   🕐 Generated at: {generated_at_display} UTC")

    # Also create a CNAME file if needed (uncomment and set your domain)
    # cname_file = OUTPUT_DIR / "CNAME"
    # cname_file.write_text("your-domain.com")

    # Create .nojekyll for GitHub Pages
    nojekyll = OUTPUT_DIR / ".nojekyll"
    nojekyll.touch()

    print("\n🎉 Site generation complete!")


if __name__ == "__main__":
    generate_site()
