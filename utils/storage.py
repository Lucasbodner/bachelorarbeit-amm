"""
utils/storage.py
----------------
Petit module utilitaire pour gérer l’historique des conversations en local.

Formats & fichiers :
- data/conversations.jsonl  (format JSONL, 1 objet par ligne)
- data/conversations.txt    (format texte simple, lisible à la main)

Fonctions exposées :
- save_message(prompt, response, latency_ms)
- load_last(n)
- all_messages()
- clear_history()
- export_jsonl()
"""

import os
import json
import io
from datetime import datetime
from typing import List, Dict, Optional

DATA_DIR = "data"
JSONL_PATH = os.path.join(DATA_DIR, "conversations.jsonl")
TXT_PATH   = os.path.join(DATA_DIR, "conversations.txt")


def _ensure_data_dir() -> None:
    """Crée le dossier data/ si besoin."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _now_iso_utc() -> str:
    """Retourne un timestamp ISO-8601 en UTC (suffixe 'Z')."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def save_message(prompt: str, response: str, latency_ms: Optional[int] = None) -> None:
    """
    Ajoute un enregistrement à l’historique local (JSONL + TXT).
    - prompt: texte de la question
    - response: réponse générée
    - latency_ms: latence de génération (en millisecondes), optionnelle
    """
    _ensure_data_dir()
    rec = {
        "ts": _now_iso_utc(),
        "prompt": prompt,
        "response": response,
        "latency_ms": latency_ms,
    }

    # Écrit en JSONL (1 objet JSON par ligne)
    with open(JSONL_PATH, "a", encoding="utf-8") as jf:
        jf.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Écrit en TXT (lisible rapidement à l’œil)
    with open(TXT_PATH, "a", encoding="utf-8") as tf:
        tf.write(f"[{rec['ts']}] Q: {prompt}\nA: {response}\nLatency: {latency_ms} ms\n---\n")


def load_last(n: int) -> List[Dict]:
    """
    Charge les N *derniers* enregistrements depuis le JSONL.
    Retourne une liste d’objets dict (vide si fichier absent).
    """
    if not os.path.isfile(JSONL_PATH):
        return []

    records: List[Dict] = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Ignore une ligne corrompue plutôt que planter l’app
                continue

    return records[-n:] if n > 0 else records


def all_messages() -> List[Dict]:
    """
    Charge *tout* l’historique depuis le JSONL (liste de dicts).
    """
    return load_last(10**9)  # grand n pour “tout” récupérer


def clear_history() -> None:
    """
    Supprime les fichiers d’historique (si présents).
    """
    for path in (JSONL_PATH, TXT_PATH):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            # Si ça rate (droits, etc.), on ignore pour ne pas casser l’UI
            pass


def export_jsonl() -> bytes:
    """
    Renvoie le contenu du JSONL au format bytes (UTF-8),
    pratique pour le st.download_button de Streamlit.
    """
    _ensure_data_dir()
    if not os.path.isfile(JSONL_PATH):
        # Si l’historique n’existe pas encore, retourne un flux vide
        return b""

    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # encode en bytes pour Streamlit
    return content.encode("utf-8")
