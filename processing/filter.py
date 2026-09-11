"""
processing/filter.py
Score chaque article par pertinence selon le profil utilisateur.
"""

import yaml


def load_profile(config_path="config/profile.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["profile"]


def score_article(article, keywords):
    """
    Calcule un score de pertinence 0-100 pour un article.
    Basé sur la présence des mots-clés dans le titre et le résumé.
    Le titre pèse plus lourd que le résumé.
    """
    score = 0
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    # Nettoyer les accents et caractères spéciaux pour le matching
    full_text = title + " " + summary

    for keyword in keywords:
        kw = keyword.lower()
        # Matching simple par inclusion (robuste aux accents et tirets)
        if kw in title:
            score += 15
        elif kw in summary:
            score += 5

    # Bonus source (weight définie dans sources.yaml)
    score *= article.get("weight", 1.0)

    # Plafonner à 100
    return min(round(score, 2), 100)


def filter_and_rank(articles, top_n=5):
    """
    Score, filtre et classe les articles par pertinence.
    Retourne les top_n meilleurs.
    """
    profile = load_profile()
    keywords = profile.get("keywords", [])
    max_articles = profile.get("max_articles", top_n)

    print(f"  → Scoring de {len(articles)} articles...")

    scored = []
    for article in articles:
        s = score_article(article, keywords)
        if s >= 5:  # Seuil minimal de pertinence
            article["score"] = s
            scored.append(article)

    # Tri décroissant par score
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Déduplication par titre similaire
    seen_titles = set()
    deduplicated = []
    for art in scored:
        title_key = art["title"][:50].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            deduplicated.append(art)

    top = deduplicated[:max_articles]
    print(f"  ✅ {len(top)} articles sélectionnés")
    return top
