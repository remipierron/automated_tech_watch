"""
collectors/rss_collector.py
Collecte les articles depuis les flux RSS définis dans config/sources.yaml
"""

import feedparser
import requests
import yaml
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup


def load_sources(config_path="config/sources.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]["rss"]


def fetch_rss_articles(max_age_hours=168):
    """
    Parcourt tous les flux RSS et retourne les articles des dernières max_age_hours heures.
    Chaque article est un dict : {title, url, source, summary, published, weight}
    """
    sources = load_sources()
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    for source in sources:
        print(f"  → Collecte : {source['name']}")
        try:
            feed = feedparser.parse(
                source["url"],
                agent="TechWatch/1.0 (veille automatisée étudiante; contact: remi.pierron01@etu.univ-poitiers.fr)"
            )
            for entry in feed.entries[:15]:  # max 15 articles par source
                # Date de publication
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                # Filtrer les articles trop vieux (garder si date absente)
                if published is not None and published < cutoff:
                    continue

                # Résumé brut
                summary = ""
                if hasattr(entry, "summary"):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    summary = soup.get_text(separator=" ").strip()[:500]

                articles.append({
                    "title": entry.get("title", "Sans titre").strip(),
                    "url": entry.get("link", ""),
                    "source": source["name"],
                    "summary": summary,
                    "published": published.isoformat() if published else None,
                    "weight": source.get("weight", 1.0),
                    "language": source.get("language", "en"),
                })

        except Exception as e:
            print(f"    ⚠️  Erreur sur {source['name']} : {e}")

    print(f"  ✅ {len(articles)} articles collectés au total")
    return articles
