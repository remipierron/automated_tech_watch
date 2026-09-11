"""
processing/llm_processor.py
Utilise un modèle local via Ollama pour résumer les articles
et produire un résumé général de l'actualité tech.
"""

import os
import requests
import yaml
from datetime import datetime


def load_profile(config_path="config/profile.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["profile"]


def get_client():
    return {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        "timeout": int(os.getenv("OLLAMA_TIMEOUT", "120")),
    }


def ollama_chat(client, prompt):
    payload = {
        "model": client["model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    response = requests.post(
        f"{client['base_url']}/api/chat",
        json=payload,
        timeout=client["timeout"],
    )
    response.raise_for_status()
    data = response.json()

    content = data.get("message", {}).get("content")
    if not isinstance(content, str):
        raise ValueError("Réponse Ollama invalide: champ 'message.content' manquant")

    return content.strip()


def summarize_article(client, article):
    """
    Demande au LLM de résumer un article en 3-5 lignes
    en utilisant Google Search pour accéder au contenu réel.
    """
    prompt = f"""Tu es un assistant de veille technologique pour un étudiant en Data Science.

Voici un article à résumer :
- Titre : {article['title']}
- Source : {article['source']}
- URL : {article['url']}
- Extrait disponible : {article.get('summary', "Pas d'extrait disponible")}

Utilise ta capacité de recherche web pour accéder au contenu complet de cet article si possible.

Produis un résumé en français en 3 à 5 phrases maximum. Sois concis, informatif et mets en avant :
1. Le sujet principal
2. Les résultats ou conclusions clés
3. La pertinence pour un profil Data Science / IA

Ne commence pas par "Cet article" ou "L'article". Va droit au but."""

    try:
        return ollama_chat(client, prompt)
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
        return ollama_chat(client, prompt)
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
