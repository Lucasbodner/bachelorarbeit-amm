"""
AMM Mobile App – Combined UI (FedWell + Local .gguf)
----------------------------------------------------
• FedWell-style pages (Overview / Health Profile / Patient / Physio)
• 100% on-device inference via `llama-cli` (llama.cpp) and a local `.gguf` model
• Local JSONL history (save/export/clear) via utils/storage.py
• No Transformers / Torch / HF token required
"""

import os
import time
import subprocess
import datetime
import multiprocessing
import streamlit as st
import pandas as pd
from typing import Optional

# Altair is optional (we fall back to st.bar_chart if it's not available)
try:
    import altair as alt
    ALTAIR_AVAILABLE = True
except Exception:
    ALTAIR_AVAILABLE = False

# Local storage helpers (your existing utils)
from utils.storage import save_message, load_last, clear_history, export_jsonl

# =========================
#  PAGE CONFIG & GLOBAL CSS
# =========================
st.set_page_config(
    page_title="AMM Mobile App – Local Prototype",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Chat-like styling + mobile tweaks
st.markdown("""
<style>
/* Container width for desktop + full-bleed on mobile */
.main { max-width: 900px; margin: auto; padding: 0 12px; }

/* Basic look & feel */
body { background-color: #f9f9f9; }
.message-card {
    border: 1px solid #ddd; border-radius: 12px; padding: 12px;
    margin-bottom: 12px; background-color: #fdfdfd;
}
.user-msg { color: #1A5276; font-weight: 600; }
.amm-msg  { color: #117A65; }

/* Chat bubbles (used by st.chat_message) */
.chat-bubble { border-radius: 14px; padding: 12px 14px; margin: 8px 0; line-height: 1.5; }
.user      { background: #eef3ff; border: 1px solid #d8e4ff; }
.assistant { background: #f6fffa; border: 1px solid #d7f1e3; }

/* Sticky composer on mobile */
@media (max-width: 640px) {
  .block-container { padding-top: 0.5rem; }
  .composer { position: sticky; bottom: 0; background: white; padding: 10px 8px 14px; border-top: 1px solid #eee; }
}

/* Buttons */
.stButton button {
    background-color: #2E86C1; color: white; border-radius: 12px;
    padding: 0.8em 1.1em; font-weight: 600;
}

/* Headers */
h1.center { text-align:center; color:#2E86C1; }
p.center  { text-align:center; color:#475467; }
.footer { text-align: center; color: #98A2B3; font-size: 0.9em; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# =========================
#    COMPAT HELPERS (width)
# =========================
def st_responsive_altair(chart):
    """Render an Altair chart full-width in a way that works across Streamlit versions."""
    try:
        return st.altair_chart(chart, width="stretch")
    except TypeError:
        return st.altair_chart(chart, use_container_width=True)

def st_responsive_image(*args, **kwargs):
    """Render an image full-width (or fallback) across Streamlit versions."""
    try:
        return st.image(*args, width="stretch", **{k: v for k, v in kwargs.items() if k != "use_container_width"})
    except TypeError:
        return st.image(*args, use_container_width=True, **{k: v for k, v in kwargs.items() if k != "width"})

# =========================
#    CONSTANTS & DEFAULTS
# =========================
DEFAULT_BIN_PATH   = os.path.join("bin", "llama-cli")
DEFAULT_MODEL_PATH = os.path.join("model", "Llama-3.2-1B-merged-lora-q4_k.gguf")

DEFAULT_MAX_TOKENS = 800
DEFAULT_THREADS    = max(1, multiprocessing.cpu_count() // 2)
DEFAULT_BATCH      = 1024
DEFAULT_NOWARMUP   = True
DEFAULT_TEMPERATURE = 0.7   # optional, works with llama-cli
DEFAULT_TOP_P       = 0.9   # optional, works with llama-cli

# =========================
#     SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []    # chat timeline for Patient Corner
if "user_data" not in st.session_state:
    st.session_state.user_data = {}   # health profile / Big Five / scores

# =========================
#       UI UTILITIES
# =========================
def file_exists(path: str) -> bool:
    try:
        return os.path.isfile(path)
    except Exception:
        return False

def find_asset(*candidates: str) -> Optional[str]:
    """Return the first existing asset path among provided candidates."""
    for c in candidates:
        if file_exists(c):
            return c
    return None

def header_with_logos(title: str):
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        logo_fw = find_asset("assets/fedwell_logo.png", "assets/assets/fedwell_logo.png")
        if logo_fw:
            st.image(logo_fw, width=120)  # fixed size is fine for logos
    with col2:
        st.markdown(f"<h1 class='center'>{title}</h1>", unsafe_allow_html=True)
    with col3:
        logo_dfki = find_asset("assets/dfki_logo2.png", "assets/assets/dfki_logo2.png")
        if logo_dfki:
            st.image(logo_dfki, width=70)  # fixed size is fine for logos

def preflight_checks(bin_path: str, model_path: str) -> bool:
    ok = True
    if not os.path.isfile(bin_path):
        st.error(f"❌ Missing binary: `{bin_path}`.\n\nPlace the compiled `llama-cli` in `bin/`.")
        ok = False
    elif not os.access(bin_path, os.X_OK):
        st.error(f"❌ Binary not executable: `{bin_path}`.\n\nRun:\n```bash\nchmod +x {bin_path}\n```")
        ok = False
    if not os.path.isfile(model_path):
        st.error(f"❌ Missing model: `{model_path}`.\n\nPlace your `.gguf` model in `model/`.")
        ok = False
    return ok

# =========================
#       MODEL INVOCATION
# =========================
def generate_response(
    prompt: str,
    bin_path: str,
    model_path: str,
    max_tokens: int,
    threads: int,
    batch: int,
    no_warmup: bool,
    temperature: float,
    top_p: float,
):
    """
    Execute `llama-cli` and return (filtered_response, latency_ms, stderr_text).
    Notes:
    - Minimal instruction template that models follow well.
    - No stop tokens (those can trigger immediate stops).
    - If the first try returns empty, retry once with the raw prompt.
    """
    # 1) Minimal formatting to guide the model
    formatted_prompt = (
        "You are a helpful physiotherapy assistant. "
        "Respond in clear Markdown with these sections: **Summary**, **Steps**, **Cautions**. "
        "Use short bullet points. Avoid repeating the prompt.\n\n"
        f"{prompt.strip()}\n\n"
        "Answer:"
    )

    def _run(llm_prompt: str):
        cmd = [
            bin_path, "-m", model_path,
            "-p", llm_prompt,
            "-n", str(max_tokens),
            "-t", str(threads),
            "-b", str(batch),
            "--temp", str(temperature),
            "--top-p", str(top_p),
        ]
        if no_warmup:
            cmd.append("--no-warmup")

        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        latency_ms_local = int((time.time() - t0) * 1000)

        raw = proc.stdout or ""
        # Keep only non-llama.cpp log lines
        filtered_lines = [
            ln for ln in raw.strip().splitlines()
            if not ln.startswith((
                "llama_", "ggml_", "build:", "main:", "load:", "print_info:",
                "sampler", "generate:", "llama_perf", "system_info:", "ggml_metal_"
            ))
        ]
        response_text = "\n".join(filtered_lines).strip()
        return response_text, latency_ms_local, (proc.stderr or "").strip()

    # 2) First attempt
    response, latency_ms, stderr_txt = _run(formatted_prompt)

    # 3) Fallback if empty
    if not response:
        response, latency_ms, stderr_txt = _run(prompt.strip())

    if not response:
        response = "(no tokens generated — try a shorter question or fewer max tokens)"
    return response, latency_ms, stderr_txt

def _postprocess_text(text: str) -> str:
    """Clean output and shape into readable Markdown."""
    if not text:
        return "(no tokens generated — try a shorter question)"
    # Remove empty lines & deduplicate consecutive identical lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    deduped = []
    last = None
    for l in lines:
        if l != last:
            deduped.append(l)
        last = l
    text = "\n".join(deduped)
    # If it's one long paragraph, convert to bullets for readability
    if "\n\n" not in text and len(text) > 400:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        bullets = "\n".join(f"- {s}" for s in sentences if s)
        text = f"**Summary:**\n\n{bullets}"
    return text

def format_ts(ts=None):
    return (ts or datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

# =========================
#         PAGES
# =========================
def page_overview():
    header_with_logos("MENTALYTICS")
    st.subheader("Description")
    st.write("""
Effective medical rehabilitation depends on good patient–therapist collaboration. Cognitive or psychological barriers can hinder communication and self-assessment.
Artificial Mental Models (AMMs) can capture patient expectations and support clearer, more personalized decisions.
This prototype demonstrates an on-device AMM for rehabilitation (privacy-preserving, offline).
""")

    hero = find_asset("assets/csm_Project_1669_413615496a.png", "assets/assets/csm_Project_1669_413615496a.png")
    if hero:
        st_responsive_image(hero)

    st.subheader("Approach")
    st.write("""
We integrate a quantized AMM (Llama *.gguf*) executed locally via **llama-cli**.
The app offers a simple UI for Q/A and a **local** conversation history (export/clear).
No data ever leaves the device.
""")

def page_health_profile():
    header_with_logos("My Health Profile")

    ud = st.session_state.user_data

    st.subheader("Demographics & Health")
    c1, c2, c3 = st.columns(3)
    with c1:
        ud["Age"]   = st.number_input("Age", min_value=1, max_value=120, value=int(ud.get("Age", 30)))
        ud["Gender"] = st.selectbox("Gender", ["Male", "Female", "Other"],
                                    index=["Male","Female","Other"].index(ud.get("Gender", "Male")))
        ud["Employment_status"] = st.selectbox(
            "Employment Status",
            ["Employed","Self-Employed","Student","Unemployed","Retired","Other"],
            index=max(0, ["Employed","Self-Employed","Student","Unemployed","Retired","Other"]
                      .index(ud.get("Employment_status", "Employed")))
        )
    with c2:
        ud["Current_emotional_state"] = st.text_input("Current emotional state", ud.get("Current_emotional_state", "Calm"))
        ud["Have_any_physical_disabilities"] = st.selectbox(
            "Physical disabilities?", ["No", "Yes"],
            index=["No","Yes"].index(ud.get("Have_any_physical_disabilities", "No"))
        )
        ud["Type_of_physical_activities"] = st.text_input(
            "Physical activities (e.g., Jogging)", ud.get("Type_of_physical_activities", "Jogging")
        )
    with c3:
        ud["How_many_days_do_you_do_exercise"] = st.slider(
            "Days of exercise/week", 0, 7, int(ud.get("How_many_days_do_you_do_exercise", 3))
        )
        ud["Overall_health_status"] = st.selectbox(
            "Overall health", ["Poor","Fair","Good","Very Good","Excellent"],
            index=max(0, ["Poor","Fair","Good","Very Good","Excellent"]
                      .index(ud.get("Overall_health_status","Good")))
        )
        ud["Current_mobility"] = st.selectbox(
            "Current mobility", ["Poor","Fair","Good","Very Good","Excellent"],
            index=max(0, ["Poor","Fair","Good","Very Good","Excellent"]
                      .index(ud.get("Current_mobility","Good")))
        )

    st.subheader("Big Five (Short)")
    cc1, cc2 = st.columns(2)
    with cc1:
        ud["Q21"] = st.number_input("“Extraverted and enthusiastic” (1–7)", 1.0, 7.0, float(ud.get("Q21", 4.0)), 1.0)
        ud["Q26"] = st.number_input("“Reserved and quiet” (1–7)",           1.0, 7.0, float(ud.get("Q26", 4.0)), 1.0)
        ud["Extroversion"] = (ud["Q21"] + ud["Q26"]) / 2

        ud["Q22"] = st.number_input("“Critical and quarrelsome” (1–7)",     1.0, 7.0, float(ud.get("Q22", 4.0)), 1.0)
        ud["Q27"] = st.number_input("“Sympathetic and warm” (1–7)",         1.0, 7.0, float(ud.get("Q27", 4.0)), 1.0)
        ud["Agreeableness"] = (ud["Q22"] + ud["Q27"]) / 2
    with cc2:
        ud["Q28"] = st.number_input("“Disorganized and careless” (1–7)",    1.0, 7.0, float(ud.get("Q28", 4.0)), 1.0)
        ud["Q23"] = st.number_input("“Dependable and self-disciplined” (1–7)", 1.0, 7.0, float(ud.get("Q23", 4.0)), 1.0)
        ud["Conscientiousness"] = (ud["Q28"] + ud["Q23"]) / 2

        ud["Q24"] = st.number_input("“Anxious and easily upset” (1–7)",     1.0, 7.0, float(ud.get("Q24", 4.0)), 1.0)
        ud["Q29"] = st.number_input("“Calm and emotionally stable” (1–7)",  1.0, 7.0, float(ud.get("Q29", 4.0)), 1.0)
        ud["Emotional_Stability"] = (ud["Q24"] + ud["Q29"]) / 2

    ud["Q30"] = st.number_input("“Conventional, uncreative” (1–7)", 1.0, 7.0, float(ud.get("Q30", 4.0)), 1.0)
    ud["Q25"] = st.number_input("“Open to new experiences” (1–7)",  1.0, 7.0, float(ud.get("Q25", 4.0)), 1.0)
    ud["Openness"] = (ud["Q30"] + ud["Q25"]) / 2

    st.subheader("Exercise Difficulty (1–5)")
    e1, e2, e3, e4 = st.columns(4)
    with e1: ud["question_answer_string"]  = st.number_input("10 Squats",             1.0, 5.0, float(ud.get("question_answer_string", 3.0)), 1.0)
    with e2: ud["question_answer_string2"] = st.number_input("10 Calf Raises",        1.0, 5.0, float(ud.get("question_answer_string2", 3.0)), 1.0)
    with e3: ud["question_answer_string3"] = st.number_input("10 Standing Toe Touch", 1.0, 5.0, float(ud.get("question_answer_string3", 3.0)), 1.0)
    with e4: ud["question_answer_string4"] = st.number_input("10 Toe Touch Stretch",  1.0, 5.0, float(ud.get("question_answer_string4", 3.0)), 1.0)

    st.success("Health profile saved locally (session state).")

def page_patient_corner(
    bin_path: str,
    model_path: str,
    max_tokens: int,
    threads: int,
    batch: int,
    no_warmup: bool,
    temperature: float,
    top_p: float,
):
    header_with_logos("Patient Corner")

    # Show "history cleared" message after rerun if needed
    if st.session_state.get("just_cleared"):
        st.session_state.pop("just_cleared", None)
        st.toast("History cleared", icon="🧹")
        st.success("History cleared.")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    # Composer (sticky on mobile)
    with st.container():
        st.markdown('<div class="composer">', unsafe_allow_html=True)
        user_q = st.chat_input("Type your message…")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col2:
            data = export_jsonl()
            st.download_button("Export history", data=data, file_name="conversations.jsonl",
                               mime="application/json", key="dl-chat")
        with col3:
            if st.button("Clear"):
                clear_history()
                st.session_state.messages = []
                st.session_state.just_cleared = True
                try:
                    st.rerun()
                except Exception:
                    # Fallback for older Streamlit versions
                    st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if user_q is None:
        return

    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)

    # Checks + build prompt with light context
    if not preflight_checks(bin_path, model_path):
        return

    ud = st.session_state.get("user_data", {})
    context = (
        "Patient context (may be partial): "
        f"Age={ud.get('Age','?')}, Gender={ud.get('Gender','?')}, "
        f"Health={ud.get('Overall_health_status','?')}, Mobility={ud.get('Current_mobility','?')}.\n\n"
    )
    full_prompt = context + f"Question: {user_q}\n\n"

    # Call model
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            resp, latency_ms, stderr_txt = generate_response(
                prompt=full_prompt,
                bin_path=bin_path,
                model_path=model_path,
                max_tokens=max_tokens,
                threads=threads,
                batch=batch,
                no_warmup=no_warmup,
                temperature=temperature,
                top_p=top_p,
            )
        resp = _postprocess_text(resp)
        st.markdown(resp)
        st.caption(f"⏱ {latency_ms} ms")

        # Persist
        save_message(user_q.strip(), resp, latency_ms)
        st.session_state.messages.append({"role": "assistant", "content": resp})

        if stderr_txt:
            with st.expander("Runtime details"):
                st.code(stderr_txt)

def _difficulty_chart(df: pd.DataFrame, title: str):
    if ALTAIR_AVAILABLE:
        score_map = {
            1: "1 - Not difficult",
            2: "2 - Slightly difficult",
            3: "3 - Moderately difficult",
            4: "4 - Very difficult",
            5: "5 - Extremely difficult"
        }
        df = df.copy()
        df["ScoreLabel"] = df["NumericScore"].map(score_map)

        chart = (
            alt.Chart(df)
            .mark_bar(size=30)
            .encode(
                x=alt.X("Exercise:O", sort=None, axis=alt.Axis(labelAngle=0, labelOverlap=False)),
                y=alt.Y("NumericScore:Q", title=title),
                color=alt.Color("ScoreLabel:N", legend=alt.Legend(title="Difficulty Level"),
                                sort=list(score_map.values()))
            )
            .properties(width=500)
        )
        st_responsive_altair(chart)
    else:
        st.bar_chart(df.set_index("Exercise")["NumericScore"])

def _bigfive_chart(user_data: dict):
    traits = ["Extroversion","Agreeableness","Conscientiousness","Emotional Stability","Openness"]
    norms  = {"Extroversion":4.44,"Agreeableness":5.23,"Conscientiousness":5.4,"Emotional Stability":4.83,"Openness":5.38}

    user_scores = [
        user_data.get("Extroversion",0),
        user_data.get("Agreeableness",0),
        user_data.get("Conscientiousness",0),
        user_data.get("Emotional_Stability",0),
        user_data.get("Openness",0)
    ]
    data = []
    for t, s in zip(traits, user_scores):
        data.append({"Trait":t, "Group":"User", "Score":s})
        data.append({"Trait":t, "Group":"General Norm", "Score":norms[t]})
    df = pd.DataFrame(data)

    if ALTAIR_AVAILABLE:
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("Trait:N", axis=alt.Axis(labelAngle=0), title=None),
                y=alt.Y("Score:Q", title="Score (out of 7)", scale=alt.Scale(domain=[0,7])),
                xOffset=alt.XOffset("Group:N", sort=["User","General Norm"]),
                color=alt.Color("Group:N", legend=alt.Legend(title="Legend")),
                tooltip=["Trait","Group","Score"]
            )
            .properties(width=alt.Step(60), height=300)
        )
        st_responsive_altair(chart)
    else:
        pivot = df.pivot(index="Trait", columns="Group", values="Score")
        st.bar_chart(pivot)

def page_physio_corner():
    header_with_logos("Physio Corner")

    st.subheader("Patient Information & Overall Health Status")
    ud = st.session_state.get("user_data", {})

    c1, c2, c3 = st.columns(3)
    with c1:
        st.write(f"**Age**: {ud.get('Age','N/A')}")
        st.write(f"**Gender**: {ud.get('Gender','N/A')}")
        st.write(f"**Employment Status**: {ud.get('Employment_status','N/A')}")
    with c2:
        st.write(f"**Physical Disabilities**: {ud.get('Have_any_physical_disabilities','N/A')}")
        st.write(f"**Physical Activities**: {ud.get('Type_of_physical_activities','N/A')}")
        st.write(f"**Days of Exercise/Week**: {ud.get('How_many_days_do_you_do_exercise','N/A')}")
    with c3:
        st.write(f"**Overall Health Status**: {ud.get('Overall_health_status','N/A')}")
        st.write(f"**Current Mobility**: {ud.get('Current_mobility','N/A')}")
        st.write(f"**Current Emotional State**: {ud.get('Current_emotional_state','N/A')}")

    st.write(" ")

    # Exercise difficulty chart
    df_diff = pd.DataFrame({
        "Exercise": ["Squats","Calf Raises","Toe Touch","Toe Touch Stretch"],
        "NumericScore": [
            ud.get("question_answer_string", 0),
            ud.get("question_answer_string2",0),
            ud.get("question_answer_string3",0),
            ud.get("question_answer_string4",0),
        ]
    })

    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("Patient Anticipated Pain/Difficulty")
        _difficulty_chart(df_diff, "Numeric Rating Scale (NRS)")

    with c_right:
        st.subheader("Patient Personality Traits & Insights")
        _bigfive_chart(ud)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**Model reasoning (example):**  
Based on age, activity level, and absence of major disabilities, squats are likely manageable.
Toe-touch stretch may feel harder due to flexibility constraints.
        """)
    with col2:
        st.markdown("""
**Trait glossary (quick):**  
- **Extroversion**: Sociability and energy  
- **Agreeableness**: Cooperation and empathy  
- **Conscientiousness**: Discipline and reliability  
- **Emotional Stability**: Calmness and resilience  
- **Openness**: Curiosity and novelty seeking  
        """)

# =========================
#          MAIN
# =========================
def main():
    # Sidebar: navigation + settings
    pages = ["Mentalytics Overview", "My Health Profile", "Patient Corner", "Physio Corner"]
    choice = st.sidebar.radio("Navigation", pages)

    with st.sidebar.expander("⚙️ Settings", expanded=False):
        bin_path = st.text_input("llama-cli path", value=DEFAULT_BIN_PATH)
        model_path = st.text_input(".gguf model path", value=DEFAULT_MODEL_PATH)
        max_tokens = st.slider("Max tokens", min_value=64, max_value=2048, value=DEFAULT_MAX_TOKENS, step=64)
        threads    = st.slider("Threads", min_value=1, max_value=max(1, multiprocessing.cpu_count()), value=DEFAULT_THREADS, step=1)
        batch      = st.slider("Batch size", min_value=16, max_value=4096, value=DEFAULT_BATCH, step=16)
        no_warmup  = st.checkbox("Disable warmup (faster start)", value=DEFAULT_NOWARMUP)
        temperature = st.slider("Temperature", 0.0, 1.5, DEFAULT_TEMPERATURE, 0.05)
        top_p       = st.slider("Top-p", 0.1, 1.0, DEFAULT_TOP_P, 0.05)

    # Global banner
    st.markdown("<h1 class='center'>🧠 AMM Mobile App</h1>", unsafe_allow_html=True)
    st.markdown("<p class='center'>Local prototype – nothing leaves your machine</p>", unsafe_allow_html=True)

    if choice == "Mentalytics Overview":
        page_overview()
    elif choice == "My Health Profile":
        page_health_profile()
    elif choice == "Patient Corner":
        page_patient_corner(
            bin_path=bin_path,
            model_path=model_path,
            max_tokens=max_tokens,
            threads=threads,
            batch=batch,
            no_warmup=no_warmup,
            temperature=temperature,
            top_p=top_p,
        )
    elif choice == "Physio Corner":
        page_physio_corner()

    st.markdown("<div class='footer'>DFKI – FedWell</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
