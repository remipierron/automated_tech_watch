"""
processing/filter.py
Score chaque article par pertinence selon le profil utilisateur.
"""

import math
import re
from datetime import datetime, timezone

import yaml


def load_profile(config_path="config/profile.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["profile"]


def _keyword_weight(keyword):
    """
    Les mots-clés multi-mots ("large language model") sont plus spécifiques
    qu'un terme générique isolé ("python", "algorithme") : ils indiquent une
    correspondance plus forte avec le profil, donc on les pondère davantage.
    """
    word_count = len(keyword.split())
    return min(1.0 + 0.35 * (word_count - 1), 2.0)


def _compile_keyword_patterns(keywords):
    """
    Pré-compile un pattern par mot-clé, délimité par des frontières de mots
    (\\b) pour éviter les faux positifs (ex : le sigle "IA" ne doit pas
    matcher à l'intérieur d'un mot comme "diagnostic").
    """
    patterns = []
    for kw in keywords:
        # \b en début pour éviter les faux positifs à l'intérieur d'un mot
        # ("IA" dans "diagnostic"), et un "s" optionnel avant le \b de fin
        # pour continuer à matcher les pluriels ("neural network(s)",
        # "algorithme(s)") comme le faisait l'ancien matching par substring.
        pattern = re.compile(r"\b" + re.escape(kw.lower()) + r"s?\b")
        patterns.append((kw, pattern, _keyword_weight(kw)))
    return patterns


def _recency_bonus(article, now=None):
    """
    Petit bonus pour les articles les plus frais : à pertinence égale, on
    préfère mettre en avant l'actualité la plus récente dans un digest
    quotidien plutôt qu'un article de plusieurs jours.
    """
    published = article.get("published")
    if not published:
        return 0.0

    try:
        published_dt = datetime.fromisoformat(published)
    except ValueError:
        return 0.0

    now = now or datetime.now(timezone.utc)
    age_hours = (now - published_dt).total_seconds() / 3600

    if age_hours <= 6:
        return 8.0
    if age_hours <= 12:
        return 5.0
    if age_hours <= 24:
        return 2.0
    return 0.0


def score_article(article, keyword_patterns, now=None):
    """
    Calcule un score de pertinence 0-100 pour un article.

    Le score combine :
    - la couverture en mots-clés (titre > résumé, mots-clés spécifiques
      pondérés plus fort), transformée par une courbe à rendement
      décroissant pour que 2-3 correspondances solides suffisent déjà à
      obtenir un bon score (plutôt qu'un total linéaire écrasé par le
      plafond à 100) ;
    - un ajustement lié au poids de la source (fiabilité/pertinence
      éditoriale définie dans sources.yaml), appliqué en modérateur plutôt
      qu'en multiplicateur brut ;
    - un petit bonus de fraîcheur.
    """
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()

    raw = 0.0
    for keyword, pattern, weight in keyword_patterns:
        title_hits = len(pattern.findall(title))
        if title_hits:
            raw += weight * 20 * min(title_hits, 2)
            continue
        summary_hits = len(pattern.findall(summary))
        if summary_hits:
            raw += weight * 8 * min(summary_hits, 2)

    # Rendement décroissant : chaque correspondance supplémentaire compte,
    # mais de moins en moins, ce qui évite les scores plafonnés/écrasés tout
    # en laissant les articles très ciblés monter nettement plus haut
    # qu'avec un simple total linéaire.
    relevance = 100 * (1 - math.exp(-raw / 40))

    # Le poids de la source module le score de ±15 % maximum : une source
    # secondaire (weight 0.6) ne doit pas écraser un article très pertinent,
    # une source de référence (weight 1.5) donne un léger coup de pouce.
    source_weight = article.get("weight", 1.0)
    relevance *= 0.85 + 0.15 * source_weight

    score = relevance + _recency_bonus(article, now)

    return min(round(score, 1), 100)


def filter_and_rank(articles, top_n=5):
    """
    Score, filtre et classe les articles par pertinence.
    Retourne les top_n meilleurs.
    """
    profile = load_profile()
    keywords = profile.get("keywords", [])
    max_articles = profile.get("max_articles", top_n)
    keyword_patterns = _compile_keyword_patterns(keywords)
    now = datetime.now(timezone.utc)

    print(f"  → Scoring de {len(articles)} articles...")

    scored = []
    for article in articles:
        s = score_article(article, keyword_patterns, now)
        if s >= 15:  # Seuil minimal de pertinence
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
