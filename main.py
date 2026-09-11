"""
main.py — Point d'entrée de TechWatch
Lance le pipeline complet de veille informationnelle.
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

from collectors.rss_collector import fetch_rss_articles
from processing.filter import filter_and_rank
from processing.llm_processor import process_articles
from storage.database import init_db, save_digest, mark_urls_seen
from output.mailer import send_digest_email


def print_digest_console(digest):
    """Affiche le digest dans le terminal de façon lisible."""
    print("\n" + "━" * 60)
    print(f"📡 TechWatch — Digest du {digest['date']}")
    print("━" * 60)
    print("\n🌐 RÉSUMÉ GÉNÉRAL")
    print(digest["general_summary"])
    print("\n" + "━" * 60)
    print("🏆 TOP 5 DES ARTICLES DU JOUR\n")

    medals = ["①", "②", "③", "④", "⑤"]
    for i, art in enumerate(digest["articles"]):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        print(f"{medal} {art['title']}")
        print(f"   📰 {art['source']} | Score : {art.get('score', 0):.0f}/100")
        print(f"   {art.get('llm_summary', art.get('summary', ''))}")
        print(f"   🔗 {art['url']}")
        print()

    print("━" * 60)


def run():
    print("\n🚀 Démarrage de TechWatch...\n")

    # Init base de données
    init_db()

    # 1. Collecte RSS
    print("📥 Étape 1 — Collecte des articles RSS...")
    articles = fetch_rss_articles(max_age_hours=24)

    if not articles:
        print("❌ Aucun article collecté. Vérifie ta connexion ou les sources.")
        sys.exit(1)

    # 2. Filtrage & scoring
    print("\n🔍 Étape 2 — Filtrage par pertinence...")
    top_articles = filter_and_rank(articles)

    if not top_articles:
        print("❌ Aucun article pertinent trouvé. Ajuste les mots-clés dans config/profile.yaml")
        sys.exit(1)

    # 3. Traitement LLM
    print("\n🤖 Étape 3 — Résumés via LLM local (Ollama)...")
    digest = process_articles(top_articles)

    # 4. Sauvegarde
    print("\n💾 Étape 4 — Sauvegarde...")
    save_digest(digest)
    mark_urls_seen(top_articles)

    # Sauvegarde JSON locale (pour le dashboard)
    with open("storage/last_digest.json", "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)

    # 5. Affichage console
    print_digest_console(digest)

    # 6. Envoi e-mail (si configuré)
    print("📬 Étape 5 — Envoi e-mail...")
    send_digest_email(digest)

    print("\n✅ TechWatch terminé avec succès !\n")
    return digest


if __name__ == "__main__":
    run()
