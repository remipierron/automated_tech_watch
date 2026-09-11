"""
processing/llm_processor.py
Utilise l'API Mistral (mode hébergé, via api.mistral.ai) pour résumer les
articles et produire un résumé général de l'actualité tech.
"""

import os
import requests
import yaml
from datetime import datetime

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


def load_profile(config_path="config/profile.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["profile"]


def get_client():
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MISTRAL_API_KEY manquant : définis-le dans le fichier .env"
        )
    return {
        "api_key": api_key,
        "model": os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        "timeout": int(os.getenv("MISTRAL_TIMEOUT", "120")),
    }


def mistral_chat(client, prompt):
    headers = {
        "Authorization": f"Bearer {client['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": client["model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    response = requests.post(
        MISTRAL_API_URL,
        headers=headers,
        json=payload,
        timeout=client["timeout"],
    )
    response.raise_for_status()
    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        content = None

    if not isinstance(content, str):
        raise ValueError("Réponse Mistral invalide: champ 'choices[0].message.content' manquant")

    return content.strip()


def summarize_article(client, article):
    """
    Demande au LLM de résumer un article en 3-5 lignes.
    """
    prompt = f"""Tu es un assistant de veille technologique pour un étudiant en Data Science.

Voici un article à résumer :
- Titre : {article['title']}
- Source : {article['source']}
- URL : {article['url']}
- Extrait disponible : {article.get('summary', "Pas d'extrait disponible")}

Produis un résumé en français en 3 à 5 phrases maximum. Sois concis, informatif et mets en avant :
1. Le sujet principal
2. Les résultats ou conclusions clés
3. La pertinence pour un profil Data Science / IA

Ne commence pas par "Cet article" ou "L'article". Va droit au but."""

    try:
        return mistral_chat(client, prompt)
    except Exception as e:
        print(f"    ⚠️  Erreur LLM pour '{article['title']}' : {e}")
        return article.get("summary", "Résumé non disponible.")


def generate_general_summary(client, articles):
    """
    Génère un résumé global de l'actualité tech du jour
    à partir des 5 articles sélectionnés.
    """
    articles_text = "\n".join([
        f"- [{art['source']}] {art['title']}" for art in articles
    ])

    prompt = f"""Tu es un assistant de veille technologique pour un étudiant en Data Science & IA.

Voici les 5 articles tech les plus importants du jour :
{articles_text}

En te basant sur ces articles et sur ta connaissance de l'actualité récente en Data Science et IA,
rédige un résumé général de l'actualité tech du jour en 4 à 6 phrases en français.

Ce résumé doit :
- Identifier les grandes tendances du moment
- Être rédigé de façon synthétique et engageante
- Être utile pour un étudiant en Data Science qui veut rester informé

Commence directement par le résumé, sans titre ni introduction."""

    try:
        return mistral_chat(client, prompt)
    except Exception as e:
        print(f"    ⚠️  Erreur LLM résumé général : {e}")
        return "Résumé général non disponible."


def process_articles(articles):
    """
    Pipeline complet : résume chaque article + génère le résumé global.
    Retourne le digest complet sous forme de dict.
    """
    profile = load_profile()
    client = get_client()

    print(f"  → Traitement LLM de {len(articles)} articles...")

    # Résumé de chaque article
    for i, article in enumerate(articles, 1):
        print(f"    [{i}/{len(articles)}] {article['title'][:60]}...")
        article["llm_summary"] = summarize_article(client, article)

    # Résumé général
    print("  → Génération du résumé général...")
    general_summary = generate_general_summary(client, articles)

    digest = {
        "date": datetime.now().strftime("%d %B %Y"),
        "generated_at": datetime.now().isoformat(),
        "general_summary": general_summary,
        "articles": articles,
        "profile_name": profile.get("name", "Utilisateur"),
    }

    print("  ✅ Traitement LLM terminé")
    return digest
