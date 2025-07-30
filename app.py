import streamlit as st
import subprocess
import os
import re

# --- Configuration de la page ---
st.set_page_config(page_title="AMM Mobile App – Local CLI", page_icon="🧠")
st.title("🧠 AMM Mobile App – Streamlit Prototype")
st.markdown("Ask your local `.gguf` model powered by llama-cli")

# --- Zone de texte utilisateur ---
user_input = st.text_area("Your question:", value="How can AI support physiotherapy?", height=100)

# --- Fonction de génération de réponse ---
def generate_response(prompt):
    try:
        result = subprocess.run(
            [
                "./bin/llama-cli",
                "-m", "model/Llama-3.2-1B-merged-lora-q4_k.gguf",
                "-p", prompt,
                "-n", "200"
            ],
            capture_output=True,
            text=True
        )

        # Découpage ligne par ligne
        output_lines = result.stdout.strip().split("\n")

        # Filtrage pour enlever les logs techniques
        filtered_lines = [
            line for line in output_lines
            if not line.startswith(("llama_", "ggml_", "build:", "main:", "load:", "print_info:",
                                    "sampler", "generate:", "llama_perf", "system_info:", "ggml_metal_"))
        ]

        # Join et nettoyage texte
        raw_response = "\n".join(filtered_lines).strip()

        # Nettoyage : suppression du prompt répété au début
        cleaned_response = re.sub(rf"^{re.escape(prompt)}[\s:]*", "", raw_response, flags=re.IGNORECASE)

        # Nettoyage optionnel : suppression des phrases génériques inutiles
        cleaned_response = re.sub(r"(?i)^As (a|part).*?\. ?", "", cleaned_response).strip()

        return cleaned_response if cleaned_response else "⚠️ No response generated."

    except Exception as e:
        return f"❌ Error during model execution:\n{e}"

# --- Bouton de génération ---
if st.button("Generate response"):
    if user_input.strip():
        with st.spinner("Generating response..."):
            response = generate_response(user_input)

            # Affichage de la réponse
            st.success("Response generated!")
            st.markdown("### 💬 Response:")
            st.write(response)

            # Sauvegarde dans un fichier texte
            os.makedirs("data", exist_ok=True)
            with open("data/conversations.txt", "a") as f:
                f.write(f"Q: {user_input.strip()}\nA: {response}\n---\n")

    else:
        st.warning("Please enter a question first.")
