# 📡 TechWatch — Veille Informationnelle Technologique Automatisée

> Application de veille automatisée propulsée par un LLM capable de parcourir internet pour sélectionner et résumer les articles les plus pertinents selon un profil Data Science / IA.

---

## 🎯 Objectif

TechWatch est un outil personnel de veille informationnelle qui tourne de manière automatisée. Chaque jour, il parcourt les dernières publications technologiques sur le web, sélectionne les **5 articles les plus pertinents** pour le profil de l'utilisateur, et produit un **résumé général** de l'actualité du moment.

L'outil est pensé comme un **digest quotidien intelligent**, sans intervention manuelle.

---

## ✨ Fonctionnalités

- 🔍 **Parcours automatique du web** — le LLM explore les dernières publications via des flux RSS, APIs et recherche web en temps réel
- 🏆 **Sélection des 5 meilleurs articles** — filtrés par pertinence selon un profil prédéfini (Data Science, IA, Deep Learning, Python…)
- 📝 **Résumé par article** — chaque article sélectionné est résumé en 3 à 5 lignes
- 🌐 **Résumé général** — synthèse globale de l'actualité tech du jour en quelques phrases
- ⏰ **Automatisation complète** — exécution planifiée sans intervention de l'utilisateur
- 📬 **Diffusion du digest** — envoi par e-mail et/ou affichage dans un dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SOURCES DE DONNÉES                    │
│  Flux RSS · APIs · Recherche web temps réel             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  COLLECTE (Python)                       │
│  feedparser · requests · BeautifulSoup                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│            FILTRAGE & SCORING PAR PERTINENCE            │
│  Correspondance profil · Déduplication · Classement     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│          TRAITEMENT LLM (Mistral AI, via API)              │
│  Résumé par article · Résumé général · Scoring final    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     DIFFUSION                           │
│  E-mail (SMTP) · Dashboard Streamlit · SQLite (logs)   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Technique

| Composant | Technologie |
|---|---|
| Langage principal | Python 3.11+ |
| Collecte RSS | `feedparser` |
| Scraping web | `requests`, `BeautifulSoup4` |
| LLM | API Mistral AI (`mistral-small-latest`) |
| Recherche web temps réel | Claude API + web search tool |
| Planification | `schedule` / `cron` |
| Envoi e-mail | `smtplib` |
| Dashboard | `Streamlit` |
| Stockage | `SQLite` |
| Versionnement | Git + GitHub |

---

## 📦 Structure du Projet

```
techwatch/
│
├── main.py                  # Point d'entrée principal
├── scheduler.py             # Planification de l'exécution
│
├── collectors/
│   ├── rss_collector.py     # Collecte via flux RSS
│   └── web_collector.py     # Recherche web temps réel
│
├── processing/
│   ├── filter.py            # Filtrage et scoring par pertinence
│   └── llm_processor.py    # Résumé et analyse via LLM
│
├── output/
│   ├── mailer.py            # Envoi du digest par e-mail
│   └── dashboard.py         # Interface Streamlit
│
├── storage/
│   └── database.py          # Gestion SQLite (logs, historique)
│
├── config/
│   ├── profile.yaml         # Profil utilisateur & mots-clés
│   └── sources.yaml         # Liste des sources RSS et domaines
│
├── .env                     # Variables d'environnement (clés API)
├── requirements.txt
└── README.md
```

---

## 📋 Format du Digest Quotidien

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 TechWatch — Digest du 21 mars 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 RÉSUMÉ GÉNÉRAL
Cette semaine en Data Science & IA : [synthèse en 3-4 phrases des tendances du jour]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 TOP 5 DES ARTICLES DU JOUR

① [Titre de l'article] — Source · Temps de lecture estimé
   Résumé en 3 à 5 lignes...
   🔗 https://...

② ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚀 Installation & Lancement

### Option A — Docker (recommandé, 100% automatisé)

Nécessite [Docker](https://www.docker.com/) et Docker Compose. Tout est orchestré par `docker-compose.yml` : le scheduler quotidien et le dashboard (les résumés sont générés via l'API Mistral, aucun modèle local à télécharger).

```bash
# Cloner le dépôt
git clone https://github.com/Remi-Pierron/techwatch.git
cd techwatch

# Configurer les variables d'environnement
cp .env.example .env
# → Renseigner MISTRAL_API_KEY, SMTP_PASSWORD, EMAIL_RECIPIENT, etc.

# Tout démarrer (build de l'image, démarrage du scheduler + du dashboard)
# — une seule commande
docker compose up -d
```

- Le **scheduler** tourne en continu et déclenche automatiquement la veille chaque jour à l'heure définie dans `config/profile.yaml` (une première veille est aussi lancée immédiatement au démarrage).
- Le **dashboard** est disponible sur [http://localhost:8501](http://localhost:8501).
- `storage/` et `config/` sont montés en volumes locaux : les digests et la base SQLite persistent entre redémarrages, et les fichiers de config peuvent être modifiés sans reconstruire l'image.
- `docker compose logs -f scheduler` pour suivre l'exécution ; `docker compose down` pour tout arrêter.

> **Sur Raspberry Pi (ou autre CPU sans GPU) :** l'écosystème (image Python, dépendances pip) est compatible `arm64`, donc `docker compose up -d` fonctionne tel quel. Les résumés étant générés via l'API Mistral (hébergée), aucune inférence locale n'est nécessaire.

### Option B — Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/Remi-Pierron/techwatch.git
cd techwatch

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# → Renseigner MISTRAL_API_KEY, SMTP_PASSWORD, etc.

# Lancer manuellement
python main.py

# Ou lancer le scheduler quotidien
python scheduler.py

# Lancer le dashboard
streamlit run output/dashboard.py
```

---


## 👨‍💻 Auteur

**Rémi Pierron** — Étudiant en BUT Science des Données (VCOD), IUT de Poitiers – site de Niort  
🔗 [LinkedIn](https://www.linkedin.com/in/rémi-pierron-54b8b1290/) · [Portfolio](https://remi-pierron.github.io/portfolio)

---

## 📄 Licence

Projet personnel — usage libre à des fins éducatives.