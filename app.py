"""
AMM Mobile App – Local Prototype (Streamlit)
--------------------------------------------
• Exécute un modèle .gguf local via le binaire `llama-cli` (llama.cpp)
• Rien ne sort de la machine : l’inférence et le stockage se font localement
• Historique enregistré en JSONL + lecture en UI

Fichiers/dirs attendus :
- bin/llama-cli                (binaire exécutable)
- model/<modele>.gguf          (modèle quantisé)
- utils/storage.py             (fonctions d’E/S locales)
"""

import os
import time
import subprocess
import streamlit as st

from utils.storage import save_message, load_last, clear_history, export_jsonl

# ------------- Page config -------------
st.set_page_config(page_title="AMM Mobile App – Local Prototype", page_icon="🧠", layout="centered")
st.title("🧠 AMM Mobile App – Local Prototype")
st.markdown(
    "Runs a local <code>.gguf</code> model via <code>llama-cli</code>. "
    "**Nothing leaves your machine.**",
    unsafe_allow_html=True,
)

# ------------- Paths & params -------------
# 👉 Si tu changes l’emplacement du binaire ou du modèle, modifie ces deux variables :
BIN_PATH = os.path.join("bin", "llama-cli")
MODEL_PATH = os.path.join("model", "Llama-3.2-1B-merged-lora-q4_k.gguf")

# Paramètres par défaut pour llama-cli (réglables si besoin)
DEFAULT_MAX_TOKENS = "800"     # longueur de génération
DEFAULT_THREADS    = "6"        # threads CPU
DEFAULT_BATCH      = "1024"     # batch size
DEFAULT_NOWARMUP   = True       # désactive le warmup pour aller plus vite (sur M2 souvent OK)

# ------------- Pré-vérifications -------------
def preflight_checks() -> bool:
    """
    Vérifie que le binaire et le modèle existent et que le binaire est exécutable.
    Retourne True si tout est OK, False sinon (avec messages d’erreur Streamlit).
    """
    ok = True

    if not os.path.isfile(BIN_PATH):
        st.error(f"❌ Missing binary: `{BIN_PATH}`.\n\n"
                 "Fix: put the compiled `llama-cli` in `bin/`.")
        ok = False
    elif not os.access(BIN_PATH, os.X_OK):
        st.error(f"❌ Binary not executable: `{BIN_PATH}`.\n\n"
                 "Fix:\n\n```bash\nchmod +x bin/llama-cli\n```")
        ok = False

    if not os.path.isfile(MODEL_PATH):
        st.error(f"❌ Missing model file: `{MODEL_PATH}`.\n\n"
                 "Fix: place your `.gguf` model in the `model/` folder.")
        ok = False

    return ok

# ------------- Génération via llama-cli -------------
def generate_response(
    prompt: str,
    max_tokens: str = DEFAULT_MAX_TOKENS,
    threads: str = DEFAULT_THREADS,
    batch: str = DEFAULT_BATCH,
    no_warmup: bool = DEFAULT_NOWARMUP,
):
    """
    Lance `llama-cli` synchronement avec les paramètres fournis et retourne :
        (texte_reponse, latence_ms, stderr)
    • Filtre les logs techniques provenant de llama.cpp pour n’afficher que la réponse.
    """
    # Construit la commande
    cmd = [
        BIN_PATH,
        "-m", MODEL_PATH,
        "-p", prompt,
        "-n", max_tokens,
        "-t", threads,
        "-b", batch,
    ]
    if no_warmup:
        cmd.append("--no-warmup")

    # Mesure la latence
    t0 = time.time()
    proc = subprocess.run(
        cmd,
        capture_output=True,  # capture stdout/stderr
        text=True,            # retourne des strings
    )
    latency_ms = int((time.time() - t0) * 1000)

    # stdout brut (peut contenir beaucoup de logs techniques)
    raw = proc.stdout or ""
    # Filtrage des lignes de logs pour ne garder que le texte du modèle
    filtered_lines = [
        ln for ln in raw.strip().splitlines()
        if not ln.startswith((
            "llama_", "ggml_", "build:", "main:", "load:", "print_info:",
            "sampler", "generate:", "llama_perf", "system_info:", "ggml_metal_"
        ))
    ]
    response = "\n".join(filtered_lines).strip() or "(empty output)"

    # stderr (utile pour le debug si besoin)
    stderr_txt = (proc.stderr or "").strip()

    return response, latency_ms, stderr_txt

# ------------- UI : zone input + actions -------------
with st.container():
    # Input utilisateur
    user_q = st.text_area("Your question", value="How can AI support physiotherapy?", height=120)

    # Deux colonnes d’actions (générer / export)
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        gen_clicked = st.button("Generate response", type="primary")
    with col2:
        # Export JSONL (historique complet)
        data = export_jsonl()
        st.download_button(
            "Download conversations.jsonl",
            data=data,
            file_name="conversations.jsonl",
            mime="application/json",
            key="dl-top",  # ⚠️ clé unique obligatoire (sinon Streamlit râle)
        )

# ------------- Action : génération -------------
if gen_clicked:
    if not user_q.strip():
        st.warning("Please enter a question first.")
    elif preflight_checks():
        with st.spinner("Generating..."):
            resp, latency_ms, stderr_txt = generate_response(user_q.strip())

        # Affichage markdown (mise en forme libre)
        st.markdown("### 💬 Response")
        st.markdown(resp)

        # Zone de copie simple (read-only)
        st.text_area("Copy from here (read-only)", value=resp, height=150)

        # Latence mesurée
        st.caption(f"⏱️ Latency: {latency_ms} ms")

        # Sauvegarde dans l’historique local (utils/storage.py)
        save_message(user_q.strip(), resp, latency_ms)

        # Détails d’exécution (stderr) pour debug
        if stderr_txt:
            with st.expander("Runtime details (stderr)"):
                st.code(stderr_txt)

st.markdown("---")

# ------------- Historique + clear + deuxième export -------------
st.subheader("Recent history")
history = list(reversed(load_last(10)))  # On affiche les 10 derniers, le plus récent d’abord

if not history:
    st.info("No history yet.")
else:
    for rec in history:
        title = f"Q: {rec.get('prompt','')[:60]}…"
        with st.expander(title):
            st.markdown(f"**Time:** {rec.get('ts','')}  \n**Latency:** {rec.get('latency_ms','–')} ms")
            st.markdown("**Answer:**")
            st.markdown(rec.get("response", ""))

colA, colB = st.columns([1,1])
with colA:
    if st.button("Clear history", help="Deletes local conversation files"):
        clear_history()
        st.success("History cleared. Reload the page.")
with colB:
    # Deuxième bouton d’export (clé différente)
    data2 = export_jsonl()
    st.download_button(
        "Download conversations.jsonl",
        data=data2,
        file_name="conversations.jsonl",
        mime="application/json",
        key="dl-bottom",  # ⚠️ clé unique différente du bouton du haut
    )
