"""
output/dashboard.py — Dashboard Streamlit TechWatch
Lance avec : streamlit run output/dashboard.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import streamlit as st
from datetime import datetime
from storage.database import load_last_digests

# ─── Config page ───────────────────────────────────────────
st.set_page_config(
    page_title="TechWatch",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS custom ────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

    .main { background: #0a0f1e; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .header-block {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        border: 1px solid #1d4ed8;
        border-radius: 12px;
        padding: 28px 32px;
        margin-bottom: 24px;
    }
    .header-title {
        font-family: 'Space Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: #60a5fa;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-sub {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 4px;
    }
    .summary-box {
        background: #0f172a;
        border: 1px solid #1d4ed8;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 28px;
        color: #cbd5e1;
        line-height: 1.8;
        font-size: 15px;
    }
    .article-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
        transition: border-color 0.2s;
    }
    .article-card:hover { border-color: #3b82f6; }
    .article-rank {
        font-family: 'Space Mono', monospace;
        font-size: 22px;
        color: #3b82f6;
        float: left;
        margin-right: 12px;
        line-height: 1.2;
    }
    .article-title {
        font-size: 17px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 6px;
    }
    .article-meta {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 10px;
    }
    .article-summary {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.7;
        margin-bottom: 12px;
    }
    .score-bar-container {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
    }
    .score-label { font-size: 12px; color: #64748b; }
    .tag {
        display: inline-block;
        background: #1e3a5f;
        color: #60a5fa;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 20px;
        margin-right: 4px;
    }
    .stButton > button {
        background: #1d4ed8;
        color: white;
        border: none;
        border-radius: 6px;
        font-family: 'Space Mono', monospace;
        font-size: 13px;
    }
    .stButton > button:hover { background: #2563eb; }
    .sidebar-label {
        font-family: 'Space Mono', monospace;
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-label">Navigation</p>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "",
        ["📡 Digest du jour", "📚 Historique", "⚙️ Configuration"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown('<p class="sidebar-label">Actions</p>', unsafe_allow_html=True)

    if st.button("🔄 Lancer une nouvelle veille", use_container_width=True):
        with st.spinner("Pipeline en cours..."):
            try:
                import subprocess
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                result = subprocess.run(
                    ["python", "main.py"],
                    capture_output=True, text=True, cwd=project_root
                )
                if result.returncode == 0:
                    st.success("✅ Veille terminée !")
                    st.rerun()
                else:
                    st.error(f"Erreur : {result.stderr[:300]}")
            except Exception as e:
                st.error(f"Erreur : {e}")


# ─── Chargement des données ─────────────────────────────────
def load_digest():
    json_path = "storage/last_digest.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


MEDALS = ["①", "②", "③", "④", "⑤"]


# ─── Page : Digest du jour ──────────────────────────────────
if page == "📡 Digest du jour":
    digest = load_digest()

    if not digest:
        st.markdown("""
        <div class="header-block">
            <p class="header-title">📡 TechWatch</p>
            <p class="header-sub">Aucun digest disponible — Lance une veille depuis le panneau latéral</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        gen_time = digest.get("generated_at", "")[:16].replace("T", " à ")

        st.markdown(f"""
        <div class="header-block">
            <p class="header-title">📡 TechWatch — {digest['date']}</p>
            <p class="header-sub">Généré le {gen_time} · {len(digest['articles'])} articles sélectionnés</p>
        </div>
        """, unsafe_allow_html=True)

        # Résumé général
        st.markdown("### 🌐 Résumé général")
        st.markdown(f'<div class="summary-box">{digest["general_summary"]}</div>', unsafe_allow_html=True)

        # Articles
        st.markdown(f"### 🏆 Top {len(digest['articles'])} articles")

        for i, art in enumerate(digest["articles"]):
            medal = MEDALS[i] if i < len(MEDALS) else str(i + 1)
            score = art.get("score", 0)
            score_pct = int(score)

            with st.container():
                st.markdown(f"""
                <div class="article-card">
                    <span class="article-rank">{medal}</span>
                    <div class="article-title">{art['title']}</div>
                    <div class="article-meta">
                        📰 {art['source']} &nbsp;|&nbsp;
                        Score pertinence : {score:.0f}/100
                    </div>
                    <div class="article-summary">{art.get('llm_summary', art.get('summary', ''))}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"[🔗 Lire l'article]({art['url']})")
                st.markdown("---")


# ─── Page : Historique ──────────────────────────────────────
elif page == "📚 Historique":
    st.markdown("""
    <div class="header-block">
        <p class="header-title">📚 Historique des digests</p>
        <p class="header-sub">7 derniers digests sauvegardés</p>
    </div>
    """, unsafe_allow_html=True)

    digests = load_last_digests(n=7)

    if not digests:
        st.info("Aucun historique disponible. Lance ta première veille !")
    else:
        for d in digests:
            with st.expander(f"📅 {d['date']} — {len(d['articles'])} articles"):
                st.markdown(f"**Résumé général :** {d['general_summary']}")
                st.markdown("**Articles :**")
                for art in d["articles"]:
                    st.markdown(f"- [{art['title']}]({art['url']}) *(Score : {art.get('score', 0):.0f})*")


# ─── Page : Configuration ───────────────────────────────────
elif page == "⚙️ Configuration":
    st.markdown("""
    <div class="header-block">
        <p class="header-title">⚙️ Configuration</p>
        <p class="header-sub">Profil & préférences TechWatch</p>
    </div>
    """, unsafe_allow_html=True)

    import yaml
    try:
        with open("config/profile.yaml", "r") as f:
            profile = yaml.safe_load(f)

        st.markdown("**Mots-clés de veille actuels :**")
        keywords = profile["profile"]["keywords"]
        cols = st.columns(3)
        for i, kw in enumerate(keywords):
            cols[i % 3].markdown(f'<span class="tag">{kw}</span>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"**Heure de déclenchement :** `{profile['profile'].get('schedule_time', '08:00')}`")
        st.markdown(f"**Articles par digest :** `{profile['profile'].get('max_articles', 5)}`")
        st.markdown(f"**E-mail :** `{profile['profile'].get('email', 'non configuré')}`")
        st.info("Pour modifier ces paramètres, édite directement `config/profile.yaml`")

    except FileNotFoundError:
        st.error("Fichier config/profile.yaml introuvable.")
