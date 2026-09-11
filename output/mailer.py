"""
output/mailer.py
Envoie le digest quotidien par e-mail au format HTML.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


MEDALS = ["🥇", "🥈", "🥉", "④", "⑤"]


def digest_to_html(digest):
    articles_html = ""
    for i, art in enumerate(digest["articles"]):
        medal = MEDALS[i] if i < len(MEDALS) else f"{i+1}."
        score_bar = "█" * int(art.get("score", 0) / 10) + "░" * (10 - int(art.get("score", 0) / 10))
        articles_html += f"""
        <div style="margin-bottom:24px; padding:16px; background:#f8f9fa; border-left:4px solid #2563eb; border-radius:4px;">
            <div style="font-size:18px; font-weight:bold; margin-bottom:4px;">{medal} {art['title']}</div>
            <div style="font-size:12px; color:#6b7280; margin-bottom:8px;">
                📰 {art['source']} &nbsp;|&nbsp; Score : {score_bar} ({art.get('score', 0):.0f}/100)
            </div>
            <p style="margin:0 0 8px; color:#374151; line-height:1.6;">{art.get('llm_summary', art.get('summary', ''))}</p>
            <a href="{art['url']}" style="color:#2563eb; font-size:13px;">🔗 Lire l'article complet</a>
        </div>
        """

    return f"""
    <html><body style="font-family: 'Segoe UI', Arial, sans-serif; max-width:700px; margin:0 auto; color:#1f2937;">
        <div style="background:#1e3a5f; color:white; padding:24px; border-radius:8px 8px 0 0;">
            <h1 style="margin:0; font-size:22px;">📡 TechWatch — Digest du {digest['date']}</h1>
            <p style="margin:4px 0 0; opacity:0.8;">Votre veille Data Science & IA quotidienne</p>
        </div>

        <div style="padding:20px; background:#eff6ff; border-left:4px solid #3b82f6;">
            <h2 style="margin:0 0 8px; font-size:15px; color:#1e40af;">🌐 Résumé général</h2>
            <p style="margin:0; line-height:1.7; color:#1f2937;">{digest['general_summary']}</p>
        </div>

        <div style="padding:20px;">
            <h2 style="font-size:16px; color:#1e3a5f; border-bottom:2px solid #e5e7eb; padding-bottom:8px;">
                🏆 Top {len(digest['articles'])} articles du jour
            </h2>
            {articles_html}
        </div>

        <div style="background:#f3f4f6; padding:16px; text-align:center; font-size:12px; color:#9ca3af; border-radius:0 0 8px 8px;">
            Généré automatiquement par TechWatch · {digest['generated_at'][:10]}
        </div>
    </body></html>
    """


def send_digest_email(digest):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    if not all([smtp_user, smtp_password, recipient]):
        print("  ⚠️  Variables SMTP manquantes, envoi e-mail ignoré.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📡 TechWatch — {digest['date']}"
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.attach(MIMEText(digest_to_html(digest), "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, msg.as_string())
        print(f"  ✅ E-mail envoyé à {recipient}")
    except Exception as e:
        print(f"  ❌ Erreur envoi e-mail : {e}")
