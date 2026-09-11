"""
scheduler.py
Lance automatiquement la veille chaque jour à l'heure définie dans le profil.
Usage : python scheduler.py
"""

import schedule
import time
import yaml
from main import run


def load_schedule_time():
    with open("config/profile.yaml", "r") as f:
        profile = yaml.safe_load(f)
    return profile["profile"].get("schedule_time", "08:00")


def job():
    print("⏰ Déclenchement automatique de la veille...")
    try:
        run()
    except Exception as e:
        print(f"❌ Erreur pendant la veille : {e}")


if __name__ == "__main__":
    schedule_time = load_schedule_time()
    print(f"📅 Scheduler TechWatch démarré — veille planifiée à {schedule_time} chaque jour")
    print("   (Ctrl+C pour arrêter)\n")

    schedule.every().day.at(schedule_time).do(job)

    # Lancer une première veille immédiatement au démarrage
    print("🚀 Première veille lancée au démarrage...")
    job()

    while True:
        schedule.run_pending()
        time.sleep(60)
