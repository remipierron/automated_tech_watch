"""
storage/database.py
Stockage des digests en SQLite pour éviter les doublons et garder l'historique.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "storage/techwatch.db"


def init_db():
    os.makedirs("storage", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS digests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            general_summary TEXT,
            articles_json TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS seen_urls (
            url TEXT PRIMARY KEY,
            seen_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def is_url_seen(url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM seen_urls WHERE url = ?", (url,))
    result = c.fetchone()
    conn.close()
    return result is not None


def mark_urls_seen(articles):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for art in articles:
        c.execute(
            "INSERT OR IGNORE INTO seen_urls (url, seen_at) VALUES (?, ?)",
            (art["url"], datetime.now().isoformat())
        )
    conn.commit()
    conn.close()


def save_digest(digest):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO digests (date, generated_at, general_summary, articles_json)
        VALUES (?, ?, ?, ?)
    """, (
        digest["date"],
        digest["generated_at"],
        digest["general_summary"],
        json.dumps(digest["articles"], ensure_ascii=False)
    ))
    conn.commit()
    conn.close()
    print("  ✅ Digest sauvegardé en base")


def load_last_digests(n=7):
    """Charge les n derniers digests pour le dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT date, generated_at, general_summary, articles_json
        FROM digests ORDER BY id DESC LIMIT ?
    """, (n,))
    rows = c.fetchall()
    conn.close()

    digests = []
    for row in rows:
        digests.append({
            "date": row[0],
            "generated_at": row[1],
            "general_summary": row[2],
            "articles": json.loads(row[3])
        })
    return digests
