# app.py
"""
Mentalytics – Pilot Flow (Light theme + i18n + per-device local save)
"""

import os
import json
import uuid
import datetime
import base64, mimetypes
from typing import Optional, List, Dict, Any

import streamlit as st
import pandas as pd

# Optional chart dep
try:
    import altair as alt
    ALTAIR_AVAILABLE = True
except Exception:
    ALTAIR_AVAILABLE = False


# -----------------
#  APP-WIDE CONFIG
# -----------------
APP_NAME = "Mentalytics"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# -----------------
#  LIGHT THEME CSS
# -----------------
st.markdown("""
<style>
:root{
  --bg:#ffffff;
  --fg:#0f172a;            /* slate-900 */
  --muted:#475569;         /* slate-600 */
  --subtle:#64748b;        /* slate-500 */
  --brand:#2563eb;         /* blue-600 */
  --brand-ghost:#eff6ff;   /* blue-50 */
  --border:#e2e8f0;        /* slate-200 */
  --card:#ffffff;
  --shadow:0 6px 20px rgba(2, 6, 23, 0.06);
}
html, body, .block-container { background: var(--bg); color: var(--fg); }
.block-container { max-width: 820px; padding-top: 1.2rem; }

/* Headings */
h1.center{
  text-align: center;
  font-weight: 800;
  font-size: clamp(26px, 5vw, 38px);
  letter-spacing: -0.02em;
  margin: 6px 0 2px 0;
  color: var(--fg);
}
h2, h3 { color: var(--fg); }
p.center{ text-align:center; color: var(--subtle); }

/* Cards */
.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: var(--shadow);
}
.card h3{ margin: 0 0 6px 0; font-weight: 700; }

/* Buttons (primary) */
.stButton > button{
  background: var(--brand);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.8em 1.1em;
  font-weight: 700;
  letter-spacing: .2px;
  box-shadow: 0 6px 16px rgba(37, 99, 235, .25);
}
.stButton > button:hover{ filter: brightness(1.03); transform: translateY(-1px); }

/* Secondary ghost buttons */
.ghost button{
  background: var(--brand-ghost);
  color: var(--brand);
  border: 1px solid #dbeafe;
  box-shadow: none;
}

/* Language buttons row */
.lang-row { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
.lang-row .stButton > button{ min-width: 160px; }

/* Inputs */
label, .stSelectbox label, .stRadio > label{ color: var(--muted); font-weight: 600; }
div[data-baseweb="select"] > div { border-radius:12px; }
.stSelectbox, .stTextInput, .stNumberInput { margin-bottom: 6px; }

/* Force all form/question labels to solid dark (including MultiSelect) */
.stMultiSelect > label,
.stSelectbox > label,
.stRadio > label,
.stTextInput > label,
.stNumberInput > label,
.stSlider > label,
label {
  color: var(--fg) !important;
  opacity: 1 !important;
  font-weight: 600 !important;
}

/* (Optional) make BaseWeb select internals respect dark text */
div[data-baseweb="select"] label {
  color: var(--fg) !important;
  opacity: 1 !important;
}

/* Improve st.error() readability */
div.stAlert {                       /* the red box */
  background: #fee2e2 !important;   /* light red */
  border: 1px solid #fecaca !important;
}
div.stAlert,                        /* text inside the box */
div.stAlert p,
div.stAlert span,
div.stAlert div {
  color: #7f1d1d !important;        /* dark red text */
}

/* Single column form spacing */
.form-wrap > div{ margin-bottom: 8px; }

/* Footer */
.footer{ text-align:center; color:#94a3b8; font-size: 12px; margin-top: 28px; }

/* Hide default sidebar background */
[data-testid="stSidebar"] { background: var(--bg); border-right: 1px solid var(--border); }

/* Tiny helper badges */
.badge {
  display:inline-block; padding:4px 10px; font-size:12px;
  background:#eef2ff; color:#3730a3; border:1px solid #c7d2fe; border-radius:999px;
}
hr.soft{ border:none; height:1px; background:var(--border); margin:12px 0;}

div[data-testid="stCheckbox"] label {
  color: var(--fg) !important;
  opacity: 1 !important;
  font-weight: 500;
}
div[data-testid="stCheckbox"] label span,
div[data-testid="stCheckbox"] label div,
div[data-testid="stCheckbox"] label p {
  color: var(--fg) !important;
  opacity: 1 !important;
}
div[data-testid="stCheckbox"] div[role="checkbox"] + div {
  color: var(--fg) !important;
  opacity: 1 !important;
}
div[data-testid="stCheckbox"] { opacity: 1 !important; }

.stButton > button:disabled,
[data-testid="baseButton-primary"][disabled] {
  background: #e2e8f0 !important;
  color: #475569 !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: none !important;
  opacity: 1 !important;
  cursor: not-allowed !important;
}

.stDownloadButton > button {
  background: var(--brand-ghost) !important;
  color: var(--brand) !important;
  border: 1px solid #dbeafe !important;
  border-radius: 12px !important;
  padding: 0.8em 1.1em !important;
  font-weight: 700 !important;
  box-shadow: none !important;
}
.stDownloadButton > button:hover {
  filter: brightness(0.98);
  transform: translateY(-1px);
}

.stButton > button { color: #fff !important; }

/* === Radios : forcer le texte des réponses en noir === */
div[data-testid="stRadio"] div[role="radiogroup"] label,
div[data-testid="stRadio"] div[role="radiogroup"] span,
div[data-testid="stRadio"] div[role="radiogroup"] p {
  color: var(--fg) !important;
  opacity: 1 !important;
  font-weight: 500;
}

div[data-testid="stRadio"] > label {
  color: var(--muted) !important;
  font-weight: 600;
}

/* === Buttons hover */
.stButton > button:hover,
.stButton > button:focus {
  color: #fff !important;               /* garde le texte blanc visible */
  background: var(--brand) !important;  /* pas d'inversion de couleurs foireuse */
  filter: brightness(1.03);
}

/* === Online binary radios (Yes/No) */
div[data-testid="stRadio"] div[role="radiogroup"] {
  display: flex;
  gap: 16px;
  flex-wrap: nowrap;
}

/* If there are more than 2 options, we will go back to the select box on the Python side (see helper) */

/* Standardise font size for questions/options */
div[data-testid="stRadio"] > label,
.stSelectbox > label,
.stMultiSelect > label,
.stTextInput > label {
  font-size: 0.95rem !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label {
  font-size: 0.95rem !important;
}

/* Improves error readability (dark red on light background) */
div.stAlert, div.stAlert * { color:#7f1d1d !important; }

.header-logos{
  position: relative;
  height: 52px;            /* hauteur de la barre */
  margin-bottom: 8px;      /* espace sous les logos */
}
.header-logos img{
  height: 40px;            /* taille par défaut des logos */
  object-fit: contain;
}
.header-logos .left{ position:absolute; top:0; left:0; }
.header-logos .right{ position:absolute; top:0; right:0; }

@media (max-width: 600px){
  .header-logos{ height: 44px; }
  .header-logos img{ height: 32px; }  /* un peu plus petit sur mobile */
}

/* Radios binaires (<= 2 options) : une seule ligne */
div[data-testid="stRadio"] [role="radiogroup"]{
  display: flex !important;
  flex-direction: row !important;
  gap: 16px !important;
  flex-wrap: nowrap !important;     /* pas de retour à la ligne en desktop */
  align-items: center !important;
}

/* chaque option (wrapper) ne doit pas faire 100% de largeur */
div[data-testid="stRadio"] [role="radiogroup"] > div{
  display: flex !important;
  align-items: center !important;
  width: auto !important;
}

/* ne pas laisser le texte des options prendre toute la ligne */
div[data-testid="stRadio"] [role="radiogroup"] label{
  white-space: nowrap !important;
  margin: 0 !important;
}

/* le label de la question reste au-dessus, sobre */
div[data-testid="stRadio"] > label{
  margin-bottom: .4rem !important;
  font-weight: 600 !important;
}

/* Sur petits écrans, autoriser le wrap proprement */
@media (max-width: 420px){
  div[data-testid="stRadio"] [role="radiogroup"]{
    flex-wrap: wrap !important;   /* si ça ne rentre pas, retour à la ligne */
    row-gap: 8px !important;
  }
}

/* ==== Fix Streamlit Expander hover/contrast on light theme ==== */
div[data-testid="stExpander"] > details > summary {
  background: #f1f5f9 !important;          /* clair, lisible */
  color: var(--fg) !important;              /* texte foncé */
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}

/* état : ouvert */
div[data-testid="stExpander"] > details[open] > summary {
  background: #f8fafc !important;
  color: var(--fg) !important;
}

/* survol / focus : garder du contraste, pas de “noir” */
div[data-testid="stExpander"] > details > summary:hover,
div[data-testid="stExpander"] > details > summary:focus {
  background: var(--brand-ghost) !important;  /* bleu très clair */
  color: var(--fg) !important;
}

/* s'assurer que tout le contenu hérite bien de la couleur */
div[data-testid="stExpander"] > details > summary * {
  color: inherit !important;
}

/* contenu interne lisible (quand ouvert) */
div[data-testid="stExpander"] .stMarkdown, 
div[data-testid="stExpander"] p, 
div[data-testid="stExpander"] span {
  color: var(--fg) !important;
}

/* Normaliser la taille du texte PARTOUT (select, multiselect, checkbox) */
.stSelectbox > label,
.stMultiSelect > label,
div[data-testid="stCheckbox"] > label { font-size: 0.95rem !important; }

/* Valeur/placeholder affichés dans l'input select & multiselect */
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] { font-size: 0.95rem !important; }

/* Items du menu déroulant BaseWeb (portal) */
div[role="listbox"] div[role="option"] { font-size: 0.95rem !important; }

/* Texte à droite des cases à cocher */
div[data-testid="stCheckbox"] label { font-size: 0.95rem !important; }

/* Masquer la barre noire "Deploy" de Streamlit */
header[data-testid="stHeader"] {
    display: none;
}

/* --- Make all dropdown controls WHITE (mobile + desktop) --- */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
  background: #ffffff !important;              /* white control */
  color: var(--fg) !important;                 /* dark text */
  border: 1px solid var(--border) !important;  /* light border */
  border-radius: 12px !important;
}

/* caret/icon + placeholder text */
.stSelectbox div[data-baseweb="select"] svg,
.stMultiSelect div[data-baseweb="select"] svg {
  color: var(--muted) !important;
}
.stSelectbox div[data-baseweb="select"] input,
.stMultiSelect div[data-baseweb="select"] input {
  color: var(--fg) !important;
}

/* focus ring */
.stSelectbox div[data-baseweb="select"] > div:focus-within,
.stMultiSelect div[data-baseweb="select"] > div:focus-within {
  box-shadow: 0 0 0 3px rgba(37,99,235,.15) !important;
  border-color: #93c5fd !important;
}

/* The dropdown MENU (portal) */
div[role="listbox"] {
  background: #ffffff !important;              /* white menu */
  border: 1px solid var(--border) !important;
}
div[role="listbox"] div[role="option"] {
  color: var(--fg) !important;                 /* dark option text */
}

/* Selected “tags” in MultiSelect */
.stMultiSelect span[data-baseweb="tag"] {
  background: #e2e8f0 !important;              /* light gray pill */
  color: var(--fg) !important;
  border-color: #cbd5e1 !important;
}

</style>
""", unsafe_allow_html=True)



# -----------------
#  I18N STRINGS
# -----------------
STRINGS: Dict[str, Dict[str, Any]] = {
    # ---------- EN ----------
    "en": {
        "app_title": "Mentalytics: When AI Reads Your Mind",
        "welcome_intro": "Welcome to our study. Please choose your language to continue.",
        "lang_fr": "Français", "lang_de": "Deutsch", "lang_en": "English",
        "consent_title": "Informed Consent of Participation",
        "consent_intro": "Please review the information below. Tick both boxes to proceed.",
        "consent_checkbox": "I have read the study information and I agree to participate.",
        "consent_checkbox2": "I consent to the storage and local processing of my answers as described.",
        "continue": "Continue",
        "profile_title": "Quick Profile",
        "save_locally": "Save locally",
        "saved": "Saved locally.",
        "next": "Next",
        "back": "Back",
        "device": "Device",
        "age": "Age",
        "gender": "Gender",
        "employment": "Employment status",
        "emotion": "Current emotional state",
        "disability": "Physical disabilities",
        "activities": "Physical activities",
        "days_ex": "Days of exercise per week",
        "overall_health": "Overall health",
        "mobility": "Current mobility",
        "yes": "Yes", "no": "No",
        "required_note": "Please complete all fields to continue.",
        "anticipated": "Predicted Pain/Difficulty",
        "nrs": "Numeric Rating Scale (NRS)",
        "traits": "Personality Traits & Insights",
        "study_title": "Study Questions",
        "save_and_continue": "Save & Continue",
        "de_blurb": (
            "Mentalytics is an AI assistant for rehabilitation and training. "
            "It uses artificial mental models, takes expectations, fitness and mood into account – "
            "and predicts how strenuous an exercise will be and whether it will be successful. "
            "The AI assesses how you feel – before you start. You'll be surprised how well it knows you."
        ),
        "required_answers": "※ Please answer all questions before submitting.",
        "missing_fields": "Please complete the following required fields: ",
        "multi_hint": "(select multiple)",
        "amm_score": "AMM score",
        "agree_with_model": "I agree with the model’s prediction",
        "footer_text": "© 2025 DFKI FedWell",
        "pt_adherence_opts": ["Not at all","Rarely","Sometimes","Often","Always"],

        # --- Guidance page labels (EN) ---
        "participant_snapshot": "Participant Snapshot",
        "industry": "Industry",
        "stress": "Stress",
        "surgery": "Surgery",
        "pt": "Physiotherapy",
        "surgery_pt": "Surgery/physiotherapy",
        "difficulty_level": "difficulty level",
        "score_word": "Score",
        "level": "Level",
        "score_out_of_7": "Score (out of 7)",
        "group": "Group",
        "group_user": "User",
        "group_norm": "General Norm",

        # Exercises
        "ex_situps": "Sit-ups (30s)",
        "ex_toe_touch": "Toe Touch",
        "ex_squats": "Squats",
        "ex_calf_raises": "Calf Raises",

        # Big Five labels for charts
        "trait_ext": "Extroversion",
        "trait_agr": "Agreeableness",
        "trait_con": "Conscientiousness",
        "trait_emo": "Emotional Stability",
        "trait_ope": "Openness",

        # Difficulty labels
        "diff1": "1 - Not difficult",
        "diff2": "2 - Slightly difficult",
        "diff3": "3 - Moderately difficult",
        "diff4": "4 - Very difficult",
        "diff5": "5 - Extremely difficult",
        
        "likert7": [
            "Disagree strongly",
            "Disagree moderately",
            "Disagree slightly",
            "Neither agree nor disagree",
            "Agree slightly",
            "Agree moderately",
            "Agree strongly",
        ],

        
        # Consent (EN)
        "consent_info_header": "Study Information",
        "consent_check1": ("I understand the explanation provided to me. I understand and will follow the hygiene rules of the "
                           "institution. I understand that this declaration of consent is revocable at any time. I have been given "
                           "a copy of this form. I have had all my questions answered to my satisfaction, and I voluntarily agree to participate in this field study."),
        "consent_check2": ("I agree that the researchers will take notes during the field study. I understand that all data will be treated "
                           "confidentially and in compliance with the GDPR. I understand that the material will be anonymized and cannot be "
                           "associated with my name. I understand that full anonymity cannot be guaranteed and a breach of confidentiality is "
                           "always possible. From the consent of publication, I cannot derive any rights (such as any explicit acknowledgment, "
                           "financial benefit, or co-authorship). I understand that the material can be published worldwide and may be the subject "
                           "of a press release linked to social media or other promotional activities. Before publication, I can revoke my consent "
                           "at any time. Once the material has been committed to publication it will not be possible to revoke the consent."),
                           
        # ---- Consent localized strings (EN) ----
        "consent_info_header": "Study Information",
        "consent_check1": ("I understand the explanation provided to me. I understand and will follow the hygiene rules of the "
                           "institution. I understand that this declaration of consent is revocable at any time. I have been given "
                           "a copy of this form. I have had all my questions answered to my satisfaction, and I voluntarily agree to participate in this field study."),
        "consent_check2": ("I agree that the researchers will take notes during the field study. I understand that all data will be treated "
                           "confidentially and in compliance with the GDPR. I understand that the material will be anonymized and cannot be "
                           "associated with my name. I understand that full anonymity cannot be guaranteed and a breach of confidentiality is "
                           "always possible. From the consent of publication, I cannot derive any rights (such as any explicit acknowledgment, "
                           "financial benefit, or co-authorship). I understand that the material can be published worldwide and may be the subject "
                           "of a press release linked to social media or other promotional activities. Before publication, I can revoke my consent "
                           "at any time. Once the material has been committed to publication it will not be possible to revoke the consent."),
        "consent_md": r"""
        **Informed Consent of Participation**

        You are invited to participate in the field study **Mentalytics Field Study – Unity Day 2025** initiated and conducted
        by Prajvi Saxena. The research is supervised by Dr.-Ing. Sabine Janzen. This study is funded and financed by the
        research project BMFTR.

        Please note:
        - Your participation is entirely voluntary and can be withdrawn at any time.
        - The field study will last approximately **5–7 min**.
        - We will record personal demographics (age, gender, etc.).
        - All records and data will be subject to standard data use policies.
        - Repeated participation in the study is not permitted.

        The alternative to participation in this study is to choose not to participate. If you have any questions or complaints
        about the whole informed-consent process of this research study or your rights as a human research subject, please contact
        our ethical committee office (DFKI) and Dr.-Ing. Sabine Janzen (E-mail: **sabine.janzen@dfki.de**).
        You should carefully read the information below. Please take the time you need to read the consent form.

        ---

        ### 1. Purpose and Goal of this Research
        The purpose of this study is to test whether the Mentalytics system can accurately predict perceived exertion and task
        completion during a short, supervised exercise in a real-world festival setting. The goal is to evaluate the feasibility,
        safety, and reliability of on-device (edge) deployment for future use in digital health and rehabilitation support. Your
        participation will help us achieve this goal. The results of this research may be presented at scientific or professional
        meetings or published in scientific proceedings and journals.

        ### 2. Participation and Compensation
        Your participation in this field study is completely voluntary. You will be one of approximately 200 people being surveyed
        for this research. You will receive no compensation for your participation. You may withdraw and discontinue participation
        at any time without penalty. If you decline to participate or withdraw from the field study, no one on the campus will be
        told. You can still demand a certificate of participation.

        ### 3. Procedure
        After confirming the informed consent, the procedure is as follows:
        1. Participants complete a short safety triage with yes/no questions to rule out acute health risks.  
        2. Participants then enter basic demographic information (age group, sex, activity level) and rate their expected exertion on a 1–5 scale.  
        3. They perform the exercise under supervision, with staff ensuring safety and observing task completion.  
        4. Immediately afterwards, participants rate their actual exertion, indicate whether they completed the task, and answer short usability and trust questions.  
        5. In parallel, staff record an observed ground truth for task completion according to predefined rules.  
        6. Finally, all data are stored locally in anonymized, encrypted form on the booth computer, with no cloud services used.

        The complete procedure of this field study will last approximately **5–7 min**.

        ### 4. Risks and Benefits
        There are no risks associated with this field study. Discomforts or inconveniences will be minor and are not likely to happen.
        If any discomforts become a problem, you may discontinue your participation. In order to minimize any risk of infection,
        hygiene regulations of the DFKI apply and must be followed. Any violations of the hygiene regulations or house rules of this
        institution can mean immediate termination of the study. If you get injured as a direct result of participation in this
        research, please reach out to the principal investigator. Enrolled students are automatically insured against the consequences
        of accidents through statutory accident insurance and with private liability insurance in case of any damages. You will not
        directly benefit through participation in this field study. We hope that the information obtained from your participation may
        help to bring forward the research in this field. The confirmation of participation in this study can be obtained directly
        from the researchers.

        ### 5. Data Protection and Confidentiality
        We are planning to publish our results from this and other sessions in scientific articles or other media. These publications
        will neither include your name nor can be associated with your identity. Any demographic information will be published
        anonymized and in aggregated form. Contact details (such as e-mails) can be used to track potential infection chains or to
        send you further details about the research. Your contact details will not be passed on to other third parties.

        Any data or information obtained in this field study will be treated confidentially, will be saved encrypted, and cannot be
        viewed by anyone outside this research project unless we have you sign a separate permission form allowing us to use them.
        All data you provide in this field study will be subject to the General Data Protection Regulation (GDPR) of the European
        Union (EU) and treated in compliance with the GDPR. Faculty and administrators from the campus will not have access to raw
        data or transcripts. This precaution will prevent your individual comments from having any negative repercussions. During
        the study, we log experimental data, and take notes during the field study. Raw data and material will be retained securely
        and in compliance with the GDPR, for no longer than required by the funding organization (10 years) or if you contact
        the researchers to destroy or delete them immediately. As with any publication or online-related activity, the risk of a
        breach of confidentiality or anonymity is always possible. According to the GDPR, the researchers will inform the participant
        if a breach of confidential data was detected.

        ### 6. Identification of Investigators (Contact)
        - **Prajvi Saxena**, Student Researcher — prajvi.saxena@dfki.de  
        - **Dr.-Ing. Sabine Janzen**, Principal Investigator — Trippstadter Str. 122, 67663 Kaiserslautern, Germany — sabine.janzen@dfki.de  
        - **Prof. Dr.-Ing. Wolfgang Maaß**, Head of Department — Trippstadter Str. 122, 67663 Kaiserslautern, Germany

        ### 7. Informed Consent and Agreement
        This consent form will be retained securely and in compliance with the GDPR for no longer than necessary.
        """,
        
        # ---- Survey (EN) ----
        "survey": {
            "sec_demo": "Demographics",
            "gender_label": "Gender (Biological)",
            "gender_opts": ["Male", "Female"],
            "marital_q": "What is your marital status?",
            "marital_opts": ["Single","Married","Divorced","Widowed","Prefer not to answer"],
            "sec_health": "Health & Accessibility",
            "disability_q": "Disability Status",
            "yn_opts": ["Yes","No","Prefer not to answer"],
            "sleep_hours_q": "How many hours do you sleep per day on average?",
            "sleep_hours_opts": ["4–5 Hours","5–6 Hours","6–7 Hours","7–8 Hours","8–9 Hours","Less than 4 Hours","More than 9 Hours"],
            "sleep_problem_q": "Have you had any problems falling asleep or staying asleep lately?",
            "sec_employment": "Employment",
            "employment_q": "Employment status",
            "employment_opts": ["Employed","Unemployed","Student","Retired","Unable to work due to disability","Homemaker/caregiver"],
            "industry_q": "If employed, in which industry do you primarily work?",
            "industry_opts": ["Healthcare and social assistance","Education","Professional/business services","Retail trade",
                              "Manufacturing","Construction","Transportation/warehousing","Food service/accommodation",
                              "Government/public administration","Information technology","Finance/insurance","Other (please specify)"],
            "work_type_q": "Which best describes your primary work activities?",
            "work_type_opts": [
              "Office/desk work","Standing service work (retail, reception)",
              "Skilled manual work (trades, repair)","Physical labor (construction, warehouse)",
              "Driving/transportation","Public safety/emergency services",
              "Other (please specify)"
            ],
            "sec_psych": "Psychological Well-Being and Emotional State",
            "emotional_q": "What is your current emotional state?",
            "emotional_opts": ["Happy","Calm","Neutral","Anxious","Frustrated","Sad","Stressed"],
            "stress_q": "What do you think about your stress level in your daily life?",
            "stress_opts": ["Low","Moderate","High"],
            "sec_lifestyle": "Physical Activity and Lifestyle Habits",
            "activities_q": "What types of physical activities do you participate in?",
            "activities_opts": ["Cardio/Aerobic exercise","Strength/Resistance training","Flexibility/Stretching",
                                "Sports (team or individual)","Recreational activities","Dance/Movement",
                                "Outdoor activities","Water activities","I don't participate in physical activities","Other (please specify)"],
            "days_q": "How many days per week do you engage in physical activity or exercise?",
            "days_opts": ["1–2 Days","2–3 Days","3–4 Days","4–5 Days","5–6 Days","7 Days"],
            "session_len_q": "On average, how long is each physical activity session?",
            "session_len_opts": ["Under 30 minutes","30–60 minutes","1–2 hours","More than 2 hours"],
            "mood_link_q": "How do you associate your mental health with your exercise habits?",
            "mood_link_opts": ["I exercise more when I am happy","I exercise more when I am sad","My exercise habits are not significantly influenced by my mood."],
            "sec_status": "Health status & history",
            "overall_health_q": "How would you rate your overall health status?",
            "mobility_q": "How would you rate your current mobility?",
            "surgery_q": "Have you undergone any surgical procedure?",
            "recovery_q": "How long was your recovery period ?",
            "recovery_opts": ["Under 2 weeks","2–4 weeks","1–3 months","3–6 months","6–12 months","Over 1 year","Ongoing recovery"],
            "pt_after_q": "Did you undergo physical therapy after your surgery?",
            "pt_adherence_q": "Did you adhere to your prescribed physical therapy plan?",
            "sec_big5": "Core Personality Dimensions",
            "big5": {
                "extrav": "I see myself as Extraverted and Enthusiastic",
                "quarrel": "I see myself as critical and quarrelsome",
                "discipline": "I see myself as dependable and self-disciplined",
                "anxious": "I see myself as anxious and easily upset",
                "open": "I see myself as open to new experiences and complex",
                "quiet": "I see myself as reserved and quiet",
                "warm": "I see myself as sympathetic and warm",
                "careless": "I see myself as disorganized and careless",
                "stable": "I see myself as calm and emotionally stable",
                "uncreative": "I see myself as conventional, uncreative"
            },
            "video_exercise": "Video-guided exercise",
            "video_q": "Were you able to perform the exercise?"
        },
    },
    # ---------- DE ----------
    "de": {
        "app_title": "Mentalytics: Wenn die KI weiß, wie du dich fühlst",
        "welcome_intro": "Willkommen zu unserer Studie. Bitte wählen Sie eine Sprache aus, um fortzufahren.",
        "lang_fr": "Französisch", "lang_de": "Deutsch", "lang_en": "Englisch",
        "consent_title": "Einverständniserklärung",
        "consent_intro": "Bitte lesen Sie die Informationen unten. Kreuzen Sie beide Kästchen an, um fortzufahren.",
        "consent_checkbox": "Ich habe die Studieninformation gelesen und stimme der Teilnahme zu.",
        "consent_checkbox2": "Ich willige in die lokale Speicherung und Verarbeitung meiner Antworten ein.",
        "continue": "Weiter",
        "profile_title": "Kurzprofil",
        "save_locally": "Lokal speichern",
        "saved": "Lokal gespeichert.",
        "next": "Weiter",
        "back": "Zurück",
        "device": "Gerät",
        "age": "Alter",
        "gender": "Geschlecht",
        "employment": "Beschäftigungsstatus",
        "emotion": "Aktueller emotionaler Zustand",
        "disability": "Körperliche Einschränkungen",
        "activities": "Körperliche Aktivitäten",
        "days_ex": "Sporttage pro Woche",
        "overall_health": "Allgemeiner Gesundheitszustand",
        "mobility": "Aktuelle Mobilität",
        "yes": "Ja", "no": "Nein",
        "required_note": "Bitte fülle alle Felder aus, um fortzufahren.",
        "anticipated": "Erwartete Schmerzen/Schwierigkeit",
        "nrs": "Numerische Bewertungsskala (NRS)",
        "traits": "Persönlichkeitsmerkmale & Einblicke",
        "study_title": "Studienfragen",
        "save_and_continue": "Speichern & weiter",
        "de_blurb": (
            "Mentalytics ist ein KI-Assistent für Rehabilitation und Training. "
            "Er nutzt künstliche mentale Modelle, berücksichtigt Erwartungen, Fitness und Stimmung – "
            "und sagt voraus, wie anstrengend eine Übung erlebt wird und ob sie gelingt. "
            "Die KI schätzt dein Empfinden ein – bevor du loslegst. Du wirst überrascht sein, wie gut sie dich kennt."
        ),
        "required_answers": "※ Bitte beantworten Sie alle Fragen, bevor Sie das Formular absenden.",
        "missing_fields": "Bitte füllen Sie die folgenden Pflichtfelder aus: ",
        "multi_hint": "(Mehrfachauswahl)",
        "amm_score": "AMM-Score",
        "agree_with_model": "Ich stimme der Vorhersage des Modells zu",
        "footer_text": "© 2025 DFKI FedWell",
        "pt_adherence_opts": ["Gar nicht","Selten","Manchmal","Oft","Immer"],
        
        "participant_snapshot": "Teilnehmer-Snapshot",
        "industry": "Branche",
        "stress": "Stress",
        "surgery": "Operation",
        "pt": "Physiotherapie",
        "surgery_pt": "Operation/Physiotherapie",
        "difficulty_level": "Schwierigkeitsgrad",
        "score_word": "Wert",
        "level": "Stufe",
        "score_out_of_7": "Wert (von 7)",
        "group": "Gruppe",
        "group_user": "Nutzer",
        "group_norm": "Allgemeine Norm",

        "ex_situps": "Sit-ups (30s)",
        "ex_toe_touch": "Zehenspitzen berühren",
        "ex_squats": "Kniebeugen",
        "ex_calf_raises": "Wadenheben",

        "trait_ext": "Extraversion",
        "trait_agr": "Verträglichkeit",
        "trait_con": "Gewissenhaftigkeit",
        "trait_emo": "Emotionale Stabilität",
        "trait_ope": "Offenheit",

        "diff1": "1 - Nicht schwierig",
        "diff2": "2 - Leicht schwierig",
        "diff3": "3 - Mäßig schwierig",
        "diff4": "4 - Sehr schwierig",
        "diff5": "5 - Extrem schwierig",
        
        "likert7": [
            "Trifft überhaupt nicht zu",
            "Trifft größtenteils nicht zu",
            "Trifft eher nicht zu",
            "Weder zutreffend noch unzutreffend",
            "Trifft eher zu",
            "Trifft größtenteils zu",
            "Trifft voll und ganz zu",
        ],


        # Consent (DE)
                "consent_info_header": "Studieninformation",
        "consent_check1": ("Ich habe die Erläuterungen verstanden. Ich werde die Hygienevorschriften der Einrichtung einhalten. "
                           "Mir ist bewusst, dass ich diese Einwilligung jederzeit widerrufen kann. Ich habe eine Kopie dieses Formulars "
                           "erhalten. Meine Fragen wurden zu meiner Zufriedenheit beantwortet, und ich nehme freiwillig an dieser Feldstudie teil."),
        "consent_check2": ("Ich bin damit einverstanden, dass die Forschenden während der Feldstudie Notizen machen. Ich verstehe, dass alle Daten "
                           "vertraulich und gemäß DSGVO behandelt werden. Das Material wird anonymisiert und kann nicht mit meinem Namen verknüpft werden. "
                           "Vollständige Anonymität kann jedoch nicht garantiert werden, und ein Bruch der Vertraulichkeit ist nie vollständig auszuschließen. "
                           "Aus der Zustimmung zur Veröffentlichung erwachsen mir keine Rechte (z. B. ausdrückliche Anerkennung, finanzieller Vorteil oder "
                           "Mitautorenschaft). Das Material kann weltweit veröffentlicht und Gegenstand von Pressemitteilungen oder Social-Media-Aktivitäten sein. "
                           "Vor der Veröffentlichung kann ich meine Einwilligung jederzeit widerrufen. Nach verbindlicher Einreichung zur Veröffentlichung ist ein "
                           "Widerruf nicht mehr möglich."),
        "consent_md": r"""
        **Einverständniserklärung**

        Sie sind eingeladen, an der Feldstudie **Mentalytics Field Study – Unity Day 2025** teilzunehmen, initiiert und durchgeführt
        von Prajvi Saxena, betreut von Dr.-Ing. Sabine Janzen. Die Studie wird durch das Forschungsprojekt BMFTR gefördert.

        Bitte beachten:
        - Ihre Teilnahme ist freiwillig und kann jederzeit beendet werden.
        - Die Studie dauert ca. **5–7 Minuten**.
        - Es werden demografische Angaben (Alter, Geschlecht etc.) erfasst.
        - Alle Aufzeichnungen/Daten unterliegen den üblichen Nutzungsrichtlinien.
        - Mehrfache Teilnahmen sind nicht erlaubt.

        Anstelle der Teilnahme können Sie sich jederzeit dagegen entscheiden. Bei Fragen/Beschwerden zum Einwilligungsprozess oder
        zu Ihren Rechten wenden Sie sich an das Ethik-Büro des DFKI und Dr.-Ing. Sabine Janzen (E-Mail: **sabine.janzen@dfki.de**).
        Bitte lesen Sie die folgenden Informationen sorgfältig.

        ---

        ### 1. Zweck und Ziel der Forschung
        Untersucht wird, ob Mentalytics wahrgenommene Anstrengung und Aufgabenerfolg bei einer kurzen, betreuten Übung in einem
        realen Festivalkontext zuverlässig vorhersagen kann. Ziel ist die Bewertung von Machbarkeit, Sicherheit und Zuverlässigkeit
        eines On-Device-Einsatzes für zukünftige Anwendungen in Digital Health und Rehabilitation. Ihre Teilnahme unterstützt dieses Ziel.
        Ergebnisse können auf Tagungen präsentiert oder veröffentlicht werden.

        ### 2. Teilnahme und Aufwandsentschädigung
        Die Teilnahme ist freiwillig. Etwa 200 Personen werden befragt. Es gibt keine Vergütung. Ein Rücktritt ist jederzeit
        ohne Nachteile möglich. Bei Ablehnung/Rücktritt wird niemand auf dem Campus informiert. Eine Teilnahmebestätigung kann ausgestellt werden.

        ### 3. Ablauf
        Nach der Einwilligung:
        1. Kurzes Sicherheitsscreening (Ja/Nein).  
        2. Basisdaten + Bewertung der erwarteten Anstrengung (1–5).  
        3. Durchführung der Übung unter Aufsicht (Sicherheit + Beobachtung des Erfolgs).  
        4. Unmittelbar danach Bewertung der tatsächlichen Anstrengung, Angabe des Erfolgs, kurze Usability/Trust-Fragen.  
        5. Parallel dokumentiert das Team eine Ground-Truth nach vordefinierten Regeln.  
        6. Alle Daten werden lokal, anonymisiert und verschlüsselt gespeichert, ohne Cloud-Dienste.

        Gesamtdauer: **5–7 Minuten**.

        ### 4. Risiken und Nutzen
        Es sind keine nennenswerten Risiken zu erwarten. Bei Unwohlsein können Sie abbrechen. Es gelten die Hygienevorschriften des DFKI;
        Verstöße können zum Abbruch führen. Bei Verletzungen infolge der Teilnahme wenden Sie sich an die Studienleitung.
        Eingeschriebene Studierende sind gesetzlich unfall- und haftpflichtversichert. Ein direkter Nutzen ist nicht zu erwarten,
        die Ergebnisse können jedoch die Forschung voranbringen. Eine Teilnahmebestätigung ist möglich.

        ### 5. Datenschutz und Vertraulichkeit
        Veröffentlichte Ergebnisse enthalten keine personenbezogenen Daten. Demografische Angaben werden anonymisiert/aggregiert.
        Kontaktangaben (z. B. E-Mail) können zur Kontaktverfolgung oder für weiterführende Informationen genutzt, jedoch nicht an Dritte
        weitergegeben werden.

        Alle Daten werden vertraulich behandelt, verschlüsselt gespeichert und sind außerhalb des Projekts nicht einsehbar,
        sofern keine gesonderte Erlaubnis vorliegt. Die Verarbeitung erfolgt gemäß DSGVO. Verwaltung/Lehrende erhalten keinen
        Zugriff auf Rohdaten. Rohdaten/Material werden sicher und DSGVO-konform bis zur vom Förderer geforderten Dauer (10 Jahre)
        aufbewahrt oder auf Wunsch früher gelöscht. Wie bei allen Online-Aktivitäten bleibt ein Restrisiko für Datenschutzverletzungen.
        Im Falle eines Vorfalls werden Betroffene gemäß DSGVO informiert.

        ### 6. Kontakt
        - **Prajvi Saxena**, Studentische Forscherin — prajvi.saxena@dfki.de  
        - **Dr.-Ing. Sabine Janzen**, Studienleitung — Trippstadter Str. 122, 67663 Kaiserslautern — sabine.janzen@dfki.de  
        - **Prof. Dr.-Ing. Wolfgang Maaß**, Abteilungsleitung — Trippstadter Str. 122, 67663 Kaiserslautern

        ### 7. Einwilligung
        Dieses Formular wird sicher und DSGVO-konform nur so lange wie nötig aufbewahrt.
        """,
        # ---- Survey (DE) ----
        "survey": {
            "sec_demo": "Demografie",
            "gender_label": "Geschlecht (biologisch)",
            "gender_opts": ["Männlich","Weiblich"],
            "marital_q": "Wie ist dein Familienstand?",
            "marital_opts": ["Ledig","Verheiratet","Geschieden","Verwitwet","Keine Angabe"],
            "sec_health": "Gesundheit & Barrierefreiheit",
            "disability_q": "Beeinträchtigung",
            "yn_opts": ["Ja","Nein","Keine Angabe"],
            "sleep_hours_q": "Wie viele Stunden schläfst du durchschnittlich pro Tag?",
            "sleep_hours_opts": ["4–5 Stunden","5–6 Stunden","6–7 Stunden","7–8 Stunden","8–9 Stunden","Weniger als 4 Stunden","Mehr als 9 Stunden"],
            "sleep_problem_q": "Hattest du zuletzt Einschlaf- oder Durchschlafprobleme?",
            "sec_employment": "Beschäftigung",
            "employment_q": "Beschäftigungsstatus",
            "employment_opts": ["Beschäftigt","Arbeitslos","Student/in","Ruhestand","Arbeitsunfähig (Behinderung)","Haushalt/Pflege"],
            "industry_q": "Falls beschäftigt: In welcher Branche arbeitest du hauptsächlich?",
            "industry_opts": ["Gesundheits- & Sozialwesen","Bildung","Unternehmensnahe Dienste","Einzelhandel",
                              "Verarbeitendes Gewerbe","Baugewerbe","Transport/Logistik","Gastronomie/Beherbergung",
                              "Öffentliche Verwaltung","Informationstechnologie","Finanzen/Versicherungen","Andere (bitte angeben)"],
            "work_type_q": "Welche Tätigkeit beschreibt deine Arbeit am besten?",
            "work_type_opts": ["Büro/Schreibtischarbeit","Stehende Servicearbeit (z. B. Verkauf)","Qualifizierte Handarbeit (Handwerk, Reparatur)",
                               "Körperliche Arbeit (Bau, Lager)","Fahren/Transport","Sicherheits-/Rettungsdienst","Sonstiges (bitte angeben)"],
            "sec_psych": "Psychisches Wohlbefinden & Emotionen",
            "emotional_q": "Wie ist dein aktueller Gefühlszustand?",
            "emotional_opts": ["Glücklich","Gelassen","Neutral","Ängstlich","Frustriert","Traurig","Gestresst"],
            "stress_q": "Wie schätzt du dein Stressniveau im Alltag ein?",
            "stress_opts": ["Gering","Mittel","Hoch"],
            "sec_lifestyle": "Körperliche Aktivität & Lebensstil",
            "activities_q": "Welche Arten von körperlicher Aktivität machst du?",
            "activities_opts": ["Cardio/Ausdauer","Kraft/Resistance-Training","Beweglichkeit/Dehnen",
                                "Sport (Team/Einzeln)","Freizeitaktivitäten","Tanz/Bewegung",
                                "Outdoor-Aktivitäten","Wasseraktivitäten","Ich mache keine körperliche Aktivität","Andere (bitte angeben)"],
            "days_q": "An wie vielen Tagen pro Woche bist du körperlich aktiv?",
            "days_opts": ["1–2 Tage","2–3 Tage","3–4 Tage","4–5 Tage","5–6 Tage","7 Tage"],
            "session_len_q": "Wie lange dauert eine Einheit im Schnitt?",
            "session_len_opts": ["Unter 30 Minuten","30–60 Minuten","1–2 Stunden","Mehr als 2 Stunden"],
            "mood_link_q": "Wie beeinflusst deine Stimmung deinen Sport?",
            "mood_link_opts": ["Ich trainiere mehr, wenn ich glücklich bin","Ich trainiere mehr, wenn ich traurig bin","Meine Aktivität hängt kaum von der Stimmung ab."],
            "sec_status": "Gesundheitszustand & -historie",
            "overall_health_q": "Wie bewertest du deinen allgemeinen Gesundheitszustand?",
            "mobility_q": "Wie bewertest du deine aktuelle Mobilität?",
            "surgery_q": "Hattest du eine Operation?",
            "recovery_q": "Wie lange dauerte die Genesung?",
            "recovery_opts": ["Unter 2 Wochen","2–4 Wochen","1–3 Monate","3–6 Monate","6–12 Monate","Über 1 Jahr","Laufende Genesung"],
            "pt_after_q": "Hattest du danach Physiotherapie?",
            "pt_adherence_q": "Hast du deinen Physio-Plan eingehalten?",
            "sec_big5": "Kernpersönlichkeitsdimensionen",
            "big5": {
                "extrav": "Ich sehe mich selbst als extravertiert und enthusiastisch",
                "quarrel": "Ich sehe mich selbst als kritisch und streitlustig",
                "discipline": "Ich sehe mich selbst als zuverlässig und selbstdiszipliniert",
                "anxious": "Ich sehe mich selbst als ängstlich und leicht aufzuregen",
                "open": "Ich sehe mich selbst als offen für Neues und komplex",
                "quiet": "Ich sehe mich selbst als zurückhaltend und ruhig",
                "warm": "Ich sehe mich selbst als mitfühlend und warmherzig",
                "careless": "Ich sehe mich selbst als unorganisiert und nachlässig",
                "stable": "Ich sehe mich selbst als gelassen und emotional stabil",
                "uncreative": "Ich sehe mich selbst als konventionell, unkreativ"
            },
            "video_exercise": "Exercice guidé par vidéo",
            "video_q": "Avez-vous pu réaliser l'exercice ?"
        },
    },
    # ---------- FR ----------
    "fr": {
        "app_title": "Mentalytics : Quand l’IA lit dans vos pensées",
        "welcome_intro": "Bienvenue dans notre étude. Veuillez choisir votre langue pour continuer.",
        "lang_fr": "Français", "lang_de": "Allemand", "lang_en": "Anglais",
        "consent_title": "Consentement éclairé à participer",
        "consent_intro": "Veuillez lire les informations ci-dessous. Cochez les deux cases pour continuer.",
        "consent_checkbox": "J’ai lu les informations et j’accepte de participer.",
        "consent_checkbox2": "J’accepte l’enregistrement local et le traitement décrit de mes réponses.",
        "continue": "Continuer",
        "profile_title": "Profil rapide",
        "save_locally": "Enregistrer en local",
        "saved": "Enregistré en local.",
        "next": "Suivant",
        "back": "Retour",
        "device": "Appareil",
        "age": "Âge",
        "gender": "Genre",
        "employment": "Statut professionnel",
        "emotion": "État émotionnel actuel",
        "disability": "Handicaps physiques",
        "activities": "Activités physiques",
        "days_ex": "Jours d’exercice/semaine",
        "overall_health": "Santé globale",
        "mobility": "Mobilité actuelle",
        "yes": "Oui", "no": "Non",
        "required_note": "Veuillez compléter tous les champs pour continuer.",
        "anticipated": "Douleur / difficulté prédites",
        "nrs": "Échelle numérique (NRS)",
        "traits": "Traits de personnalité & aperçus",
        "study_title": "Questions d’étude",
        "save_and_continue": "Enregistrer et continuer",
        "de_blurb": (
            "Mentalytics est un assistant IA pour la rééducation et l’entraînement. "
            "Il s’appuie sur des modèles mentaux artificiels, prend en compte attentes, forme et humeur – "
            "et prédit l’effort perçu et la réussite d’un exercice avant de commencer."
        ),
        "required_answers": "※ Veuillez répondre à toutes les questions avant de soumettre le formulaire.",
        "missing_fields": "Veuillez remplir les champs obligatoires suivants : ",
        "multi_hint": "(sélection multiple)",
        "amm_score": "Score AMM",
        "agree_with_model": "Je suis d’accord avec la prédiction du modèle",
        "footer_text": "© 2025 DFKI FedWell",
        "pt_adherence_opts": ["Pas du tout","Rarement","Parfois","Souvent","Toujours"],

        "participant_snapshot": "Aperçu du participant",
        "industry": "Secteur",
        "stress": "Stress",
        "surgery": "Chirurgie",
        "pt": "Kinésithérapie",
        "surgery_pt": "Chirurgie/Kiné",
        "difficulty_level": "Niveau de difficulté",
        "score_word": "Score",
        "level": "Niveau",
        "score_out_of_7": "Score (sur 7)",
        "group": "Groupe",
        "group_user": "Utilisateur",
        "group_norm": "Norme générale",

        "ex_situps": "Sit-ups (30 s)",
        "ex_toe_touch": "Toucher des orteils",
        "ex_squats": "Squats",
        "ex_calf_raises": "Élévations mollets",

        "trait_ext": "Extraversion",
        "trait_agr": "Agréabilité",
        "trait_con": "Conscience",
        "trait_emo": "Stabilité émotionnelle",
        "trait_ope": "Ouverture",

        "diff1": "1 - Pas difficile",
        "diff2": "2 - Légèrement difficile",
        "diff3": "3 - Modérément difficile",
        "diff4": "4 - Très difficile",
        "diff5": "5 - Extrêmement difficile",
        
        "likert7": [
            "Pas du tout d’accord",
            "Plutôt pas d’accord",
            "Un peu en désaccord",
            "Ni d’accord ni pas d’accord",
            "Un peu d’accord",
            "Plutôt d’accord",
            "Tout à fait d’accord",
        ],

        # Consent (FR)
        "consent_info_header": "Informations d’étude",
        "consent_check1": ("J’ai compris l’explication qui m’a été fournie. Je respecterai les règles d’hygiène de l’institution. "
                           "Je comprends que ce consentement est révocable à tout moment. Une copie de ce formulaire m’a été remise. "
                           "Toutes mes questions ont reçu une réponse satisfaisante et j’accepte volontairement de participer à cette étude de terrain."),
        "consent_check2": ("J’accepte que les chercheurs prennent des notes pendant l’étude. Je comprends que toutes les données seront traitées "
                           "de manière confidentielle et conformément au RGPD. Le matériel sera anonymisé et ne pourra pas être associé à mon nom. "
                           "Je comprends qu’un anonymat total ne peut pas être garanti et qu’une violation de confidentialité reste possible. "
                           "Du simple fait du consentement à la publication, je ne peux tirer aucun droit (reconnaissance explicite, avantage financier ou co-signature). "
                           "Le matériel peut être publié dans le monde entier et faire l’objet d’un communiqué de presse sur les réseaux sociaux ou d’autres activités "
                           "promotionnelles. Avant publication, je peux révoquer mon consentement à tout moment. Une fois le matériel engagé pour publication, "
                           "il ne sera plus possible de révoquer le consentement."),
        "consent_md": r"""
        **Consentement éclairé à participer**

        Vous êtes invité(e) à participer à l’étude de terrain **Mentalytics Field Study – Unity Day 2025**, initiée et conduite
        par Prajvi Saxena, sous la supervision de la Dr-Ing. Sabine Janzen. Cette étude est financée par le projet de recherche BMFTR.

        À noter :
        - Votre participation est entièrement volontaire et peut être interrompue à tout moment.
        - La durée de l’étude est d’environ **5–7 minutes**.
        - Nous relevons des informations démographiques (âge, sexe, etc.).
        - Les enregistrements et données suivent les règles standard d’usage des données.
        - Les participations répétées ne sont pas autorisées.

        L’alternative à la participation est de ne pas participer. Pour toute question concernant la procédure de consentement
        ou vos droits en tant que participant(e), contactez le comité d’éthique (DFKI) et la Dr-Ing. Sabine Janzen (e-mail : **sabine.janzen@dfki.de**).
        Veuillez lire attentivement les informations ci-dessous et prendre le temps nécessaire.

        ---

        ### 1. Objet et but de la recherche
        L’étude vise à tester si le système Mentalytics peut prédire avec précision l’effort perçu et l’achèvement d’une tâche lors
        d’un court exercice supervisé dans un contexte réel (festival). L’objectif est d’évaluer la faisabilité, la sécurité et la
        fiabilité d’un déploiement sur l’appareil pour des usages futurs en e-santé et rééducation. Vos réponses contribueront à cet objectif.
        Les résultats pourront être présentés lors d’événements scientifiques ou publiés.

        ### 2. Participation et compensation
        Votre participation est volontaire. Environ 200 personnes seront interrogées. Aucune compensation n’est prévue.
        Vous pouvez vous retirer sans pénalité à tout moment. En cas de refus/retrait, personne sur le campus n’en sera informé.
        Vous pouvez demander une attestation de participation.

        ### 3. Déroulement
        Après le consentement :
        1. Triage rapide de sécurité (questions oui/non).  
        2. Données démographiques de base + évaluation de l’effort anticipé (échelle 1–5).  
        3. Exécution de l’exercice sous supervision (sécurité + observation de la réussite).  
        4. Évaluation de l’effort réel, réussite de la tâche, puis quelques questions d’utilisabilité et de confiance.  
        5. En parallèle, le personnel note la « vérité terrain » selon des règles prédéfinies.  
        6. Toutes les données sont stockées localement de façon anonymisée et chiffrée, sans services cloud.

        Durée totale : **5–7 minutes**.

        ### 4. Risques et bénéfices
        Les risques sont minimes. En cas d’inconfort, vous pouvez arrêter. Les règles d’hygiène du DFKI s’appliquent ; toute infraction
        peut mener à l’arrêt immédiat de l’étude. En cas de blessure directe liée à l’étude, contactez l’investigatrice principale.
        Les étudiant(e)s inscrit(e)s sont couvert(e)s par l’assurance accidents et responsabilité civile. Aucun bénéfice direct n’est attendu,
        mais vos réponses peuvent faire progresser la recherche. Une attestation de participation peut être fournie.

        ### 5. Protection des données et confidentialité
        Les résultats pourront être publiés sans aucune donnée permettant de vous identifier. Les informations démographiques
        seront anonymisées et agrégées. Les coordonnées (e-mail…) peuvent servir au traçage sanitaire ou à l’envoi d’informations
        complémentaires. Elles ne seront pas transmises à des tiers.

        Toutes les données seront traitées de manière confidentielle, chiffrées et non accessibles à des personnes extérieures
        au projet, sauf autorisation spécifique. Le traitement respecte le RGPD. Le personnel administratif du campus n’aura pas
        accès aux données brutes. Les données et matériels seront conservés en sécurité et conformément au RGPD pendant la durée
        requise par le financeur (10 ans) ou détruits plus tôt à votre demande. Comme pour toute activité en ligne, un risque
        résiduel de violation de la confidentialité ne peut être totalement exclu. Conformément au RGPD, toute violation détectée
        sera notifiée aux personnes concernées.

        ### 6. Contacts
        - **Prajvi Saxena**, étudiante-chercheuse — prajvi.saxena@dfki.de  
        - **Dr-Ing. Sabine Janzen**, investigatrice principale — Trippstadter Str. 122, 67663 Kaiserslautern, Allemagne — sabine.janzen@dfki.de  
        - **Prof. Dr-Ing. Wolfgang Maaß**, directeur du département — Trippstadter Str. 122, 67663 Kaiserslautern, Allemagne

        ### 7. Consentement
        Ce formulaire sera conservé de manière sécurisée et conforme au RGPD pour la durée nécessaire.
        """,
        # ---- Survey (FR) ----
        "survey": {
            "sec_demo": "Démographie",
            "gender_label": "Genre (biologique)",
            "gender_opts": ["Homme","Femme"],
            "marital_q": "Quel est votre statut marital ?",
            "marital_opts": ["Célibataire","Marié(e)","Divorcé(e)","Veuf/Veuve","Préférer ne pas répondre"],
            "sec_health": "Santé & Accessibilité",
            "disability_q": "Situation de handicap",
            "yn_opts": ["Oui","Non","Préférer ne pas répondre"],
            "sleep_hours_q": "Combien d’heures dormez-vous en moyenne par jour ?",
            "sleep_hours_opts": ["4–5 heures","5–6 heures","6–7 heures","7–8 heures","8–9 heures","Moins de 4 heures","Plus de 9 heures"],
            "sleep_problem_q": "Avez-vous récemment eu des difficultés d’endormissement ou de réveils nocturnes ?",
            "sec_employment": "Emploi",
            "employment_q": "Statut professionnel",
            "employment_opts": ["En emploi","Sans emploi","Étudiant(e)","Retraité(e)","Incapacité de travailler (handicap)","Au foyer/aidant"],
            "industry_q": "Si en emploi : dans quel secteur travaillez-vous principalement ?",
            "industry_opts": ["Santé et action sociale","Éducation","Services aux entreprises/professionnels","Commerce de détail",
                              "Industrie manufacturière","Construction","Transport/entreposage","Hôtellerie-restauration",
                              "Administration publique","Technologies de l’information","Finance/assurance","Autre (à préciser)"],
            "work_type_q": "Quelle description correspond le mieux à votre activité principale ?",
            "work_type_opts": ["Travail de bureau","Service debout (vente, accueil)","Travail manuel qualifié (métiers, réparation)",
                               "Travail physique (chantier, entrepôt)","Conduite/transport","Sécurité/services d’urgence","Autre (à préciser)"],
            "sec_psych": "Bien-être psychologique & émotions",
            "emotional_q": "Quel est votre état émotionnel actuel ?",
            "emotional_opts": ["Heureux(se)","Calme","Neutre","Anxieux(se)","Frustré(e)","Triste","Stressé(e)"],
            "stress_q": "Quel est votre niveau de stress au quotidien ?",
            "stress_opts": ["Faible","Modéré","Élevé"],
            "sec_lifestyle": "Activité physique & habitudes de vie",
            "activities_q": "À quels types d’activités physiques participez-vous ?",
            "activities_opts": ["Cardio/Endurance","Renforcement musculaire","Souplesse/Étirements",
                                "Sports (équipe ou individuel)","Activités de loisir","Danse/Mouvement",
                                "Activités de plein air","Activités aquatiques","Je ne pratique pas d’activité physique","Autre (à préciser)"],
            "days_q": "Combien de jours par semaine pratiquez-vous une activité physique ?",
            "days_opts": ["1–2 jours","2–3 jours","3–4 jours","4–5 jours","5–6 jours","7 jours"],
            "session_len_q": "En moyenne, quelle est la durée d’une séance ?",
            "session_len_opts": ["Moins de 30 minutes","30–60 minutes","1–2 heures","Plus de 2 heures"],
            "mood_link_q": "Comment votre santé mentale influence-t-elle vos habitudes sportives ?",
            "mood_link_opts": ["Je fais plus de sport quand je suis heureux(se)","Je fais plus de sport quand je suis triste","Mes habitudes sportives sont peu influencées par mon humeur."],
            "sec_status": "État de santé & antécédents",
            "overall_health_q": "Comment évaluez-vous votre état de santé global ?",
            "mobility_q": "Comment évaluez-vous votre mobilité actuelle ?",
            "surgery_q": "Avez-vous subi une intervention chirurgicale ?",
            "recovery_q": "Quelle a été la durée de votre convalescence ?",
            "recovery_opts": ["Moins de 2 semaines","2–4 semaines","1–3 mois","3–6 mois","6–12 mois","Plus d’un an","Convalescence en cours"],
            "pt_after_q": "Avez-vous suivi une rééducation/kinésithérapie après l’opération ?",
            "pt_adherence_q": "Avez-vous suivi votre plan de rééducation ?",
            "sec_big5": "Grands traits de personnalité",
            "big5": {
                "extrav": "Je me considère comme extraverti(e) et enthousiaste",
                "quarrel": "Je me considère comme critique et querelleur/querelleuse",
                "discipline": "Je me considère comme fiable et autodiscipliné(e)",
                "anxious": "Je me considère comme anxieux(se) et facilement contrarié(e)",
                "open": "Je me considère comme ouvert(e) aux nouvelles expériences et complexe",
                "quiet": "Je me considère comme réservé(e) et calme",
                "warm": "Je me considère comme sympathique et chaleureux(se)",
                "careless": "Je me considère comme désorganisé(e) et négligent(e)",
                "stable": "Je me considère comme calme et émotionnellement stable",
                "uncreative": "Je me considère comme conventionnel(le), peu créatif/ve",
            },
            "video_exercise": "Exercice guidé par vidéo",
            "video_q": "Avez-vous pu réaliser l'exercice ?"
        },
    },
}

# Default language (until user chooses)
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Step machine: welcome → consent → survey → guidance
if "step" not in st.session_state:
    st.session_state.step = "welcome"


# -----------------
#  DEVICE ID (per phone)
# -----------------
def _short_id() -> str:
    return uuid.uuid4().hex[:6].upper()

def get_or_create_device_id() -> str:
    qp = st.query_params
    if "device" in qp and qp["device"]:
        device = qp["device"]
    else:
        device = _short_id()
        st.query_params.update({"device": device})
    st.session_state.device_id = device
    return device

DEVICE_ID = get_or_create_device_id()

def device_dir(device_id: str) -> str:
    d = os.path.join("data", device_id)
    os.makedirs(d, exist_ok=True)
    return d
    
# ---- JSONL append helpers (1 line = 1 JSON object) ----
def append_jsonl(device_id: str, name: str, payload: dict):
    d = device_dir(device_id)
    path = os.path.join(d, f"{name}.jsonl")
    # adds a run_id + timestamp to track runs
    payload = {
        **payload,
        "run_id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def load_latest_jsonl(device_id: str, name: str) -> dict:
    path = os.path.join(device_dir(device_id), f"{name}.jsonl")
    if not os.path.isfile(path):
        return {}
    last = ""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line
    try:
        return json.loads(last) if last else {}
    except Exception:
        return {}

# -----------------
#  ASSETS
# -----------------
def find_asset(*candidates: str) -> Optional[str]:
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None
    
def data_uri(path: str) -> str:
    if not path or not os.path.isfile(path):
        return ""
    mime, _ = mimetypes.guess_type(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# -----------------
#  UTIL / I18N
# -----------------
def t(key: str) -> str:
    lang = st.session_state.lang
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)

def qs(key: str):
    """survey helper"""
    lang = st.session_state.lang
    return STRINGS.get(lang, STRINGS["en"]).get("survey", {}).get(key)

def header(title_key: str):
    st.markdown(f"<h1 class='center'>{t(title_key)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='center'><span class='badge'>{t('device')}:</span> <strong>{DEVICE_ID}</strong></p>",
                unsafe_allow_html=True)

def is_all_filled(d: dict) -> bool:
    return all(v not in (None, "", []) for v in d.values())


# -----------------
#  PAGES
# -----------------
def page_welcome():
        
    dfki_src = data_uri("assets/dfki_logo.svg")
    fedwell_src = data_uri("assets/fedwell_logo.png")

    st.markdown(
        f"""
        <div class="header-logos">
            {f'<img class="left"  src="{dfki_src}" alt="DFKI logo"/>' if dfki_src else ""}
            {f'<img class="right" src="{fedwell_src}" alt="FedWell logo"/>' if fedwell_src else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
                    
    st.markdown(f"<h1 class='center'>{t('app_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='center'>{t('welcome_intro')}</p>", unsafe_allow_html=True)
    st.write("")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"🇩🇪 {t('lang_de')}", use_container_width=True):
            st.session_state.lang = "de"
            st.session_state.step = "consent"
            st.rerun()
        
    with c2:
        if st.button(f"🇬🇧 {t('lang_en')}", use_container_width=True):
            st.session_state.lang = "en"
            st.session_state.step = "consent"
            st.rerun()
    with c3:
        if st.button(f"🇫🇷 {t('lang_fr')}", use_container_width=True):
            st.session_state.lang = "fr"
            st.session_state.step = "consent"
            st.rerun()

    img = find_asset(
        "assets/physio2.jpg",
    )
    if img:
        st.image(img, use_container_width=True)

        
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.write(t("de_blurb"))

    footer()


def page_consent():
    header("consent_title")
    st.write(t("consent_intro"))

    with st.expander(t("consent_info_header"), expanded=False):
        st.markdown(t("consent_md"))

    agree_info = st.checkbox(t("consent_check1"))
    agree_data = st.checkbox(t("consent_check2"))

    can_continue = agree_info and agree_data

    if st.button(t("continue"), disabled=not can_continue, use_container_width=True):
        payload = {
            "agreed_info": bool(agree_info),
            "agreed_data": bool(agree_data),
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "lang": st.session_state.lang,
        }
        append_jsonl(DEVICE_ID, "consent", payload)
        st.session_state.step = "survey"
        st.rerun()

    footer()

def choice_input(label: str, options: List[str], key: str):
    """
    - <=2 options  -> radio (1 line via CSS)
    - >2 options   -> select box
    Returns the selected value.
    """
    if len(options) <= 2:
        return st.radio(label, options, key=key)
    return st.selectbox(label, options, key=key)

def with_other_specify(label: str, options: List[str], key: str):
    value = choice_input(label, options, key=key)
    other_text = ""
    if is_other(value):
        other_text = st.text_input(f"{label} — {specify_label()}", key=f"{key}__other")
    return value, other_text

    
def _other_tokens():
    return ("Other", "Other (please specify)", "Andere", "Andere (bitte angeben)", "Autre", "Autre (à préciser)")

def is_other(value: str) -> bool:
    return any(tok.lower() in str(value).lower() for tok in _other_tokens())

def specify_label():
    return "Please specify" if st.session_state.lang=="en" \
        else "Bitte angeben" if st.session_state.lang=="de" \
        else "Veuillez préciser"

def multiselect_with_other_specify(label: str, options: List[str], key: str):
    """Multiselect avec 'Other (…)' qui révèle un champ texte uniquement si sélectionné."""
    vals = st.multiselect(label, options, key=key)
    other_txt = ""
    if any(is_other(v) for v in vals):
        other_txt = st.text_input(f"{label} — {specify_label()}", key=f"{key}__other")
    return vals, other_txt


def footer():
    st.markdown(f"<div class='footer'>{t('footer_text')}</div>", unsafe_allow_html=True)


# ------- STUDY QUESTIONS -------
def page_study_questions():
    header("study_title")

    st.markdown(f"### {qs('sec_demo')}")
    age = st.selectbox(t("age"), [str(i) for i in range(1, 101)], key="age")
    gender = choice_input(qs("gender_label"), qs("gender_opts"), key="gender")
    marital = choice_input(qs("marital_q"), qs("marital_opts"), key="marital")

    st.markdown(f"### {qs('sec_health')}")
    disability = choice_input(qs("disability_q"), qs("yn_opts")[:2], key="disability")
    sleep_hours = choice_input(qs("sleep_hours_q"), qs("sleep_hours_opts"), key="sleep_hours")
    sleep_problem = choice_input(qs("sleep_problem_q"), qs("yn_opts")[:2], key="sleep_problem")

    st.markdown(f"### {qs('sec_employment')}")
    employment = choice_input(qs("employment_q"), qs("employment_opts"), key="employment")
    industry, industry_other = with_other_specify(
        qs("industry_q"),
        qs("industry_opts"),
        key="industry"
    )
    work_type, work_type_other = with_other_specify(
        qs("work_type_q"),
        qs("work_type_opts"),
        key="work_type"
    )

    st.markdown(f"### {qs('sec_psych')}")
    emotional = choice_input(qs("emotional_q"), qs("emotional_opts"), key="emotional")
    stress = choice_input(qs("stress_q"), qs("stress_opts"), key="stress")

    st.markdown(f"### {qs('sec_lifestyle')}")
    activities_label = f"{qs('activities_q')} {t('multi_hint')}"
    activities, activities_other = multiselect_with_other_specify(
        activities_label, qs("activities_opts"), key="activities"
    )
    days = choice_input(qs("days_q"), qs("days_opts"), key="days")
    session_len = choice_input(qs("session_len_q"), qs("session_len_opts"), key="session_len")
    mood_link = choice_input(qs("mood_link_q"), qs("mood_link_opts"), key="mood_link")

    st.markdown(f"### {qs('sec_status')}")
    overall_health = choice_input(qs("overall_health_q"), ["1","2","3","4","5"], key="overall_health")
    mobility = choice_input(qs("mobility_q"), ["1","2","3","4","5"], key="mobility")
    surgery = choice_input(qs("surgery_q"), qs("yn_opts")[:2], key="surgery")
    recovery = pt_after = pt_adherence = None
    if surgery == qs("yn_opts")[:2][0]:  # si OUI
        recovery = choice_input(qs("recovery_q"), qs("recovery_opts"), key="recovery")
        pt_after = choice_input(qs("pt_after_q"), qs("yn_opts")[:2], key="pt_after")
        pt_adherence = choice_input(
            qs("pt_adherence_q"),
            t("pt_adherence_opts"),
            key="pt_adherence"
        )
    else:
        pass

    st.markdown(f"### {qs('video_exercise')}")

    st.video("https://www.youtube.com/embed/PzCTwkJVhWg?start=38&controls=1")
    video_done = st.radio(
        qs("video_q"),
        options=[t("yes"), t("no")],
        horizontal=True,
    )
    
    # --- BIG FIVE (Likert words, no numbers) ---
    st.markdown(f"### {qs('sec_big5')}")

    scale_words = qs("likert7") or [
        "Disagree strongly",
        "Disagree moderately",
        "Disagree slightly",
        "Neither agree nor disagree",
        "Agree slightly",
        "Agree moderately",
        "Agree strongly",
    ]

    b5_labels = STRINGS[st.session_state.lang]["survey"]["big5"]

    def big5_select(field_key: str, label: str, default_idx: int = 3) -> str:
        """Selectbox en mots, pas de chiffres. default_idx=3 -> 'Neutral'."""
        return st.selectbox(label, scale_words, index=default_idx, key=f"b5_{field_key}")

    big5 = {
        "extrav":     big5_select("extrav",     b5_labels["extrav"],     default_idx=3),
        "quarrel":    big5_select("quarrel",    b5_labels["quarrel"],    default_idx=2),
        "discipline": big5_select("discipline", b5_labels["discipline"], default_idx=4),
        "anxious":    big5_select("anxious",    b5_labels["anxious"],    default_idx=2),
        "open":       big5_select("open",       b5_labels["open"],       default_idx=4),
        "quiet":      big5_select("quiet",      b5_labels["quiet"],      default_idx=3),
        "warm":       big5_select("warm",       b5_labels["warm"],       default_idx=4),
        "careless":   big5_select("careless",   b5_labels["careless"],   default_idx=2),
        "stable":     big5_select("stable",     b5_labels["stable"],     default_idx=3),
        "uncreative": big5_select("uncreative", b5_labels["uncreative"], default_idx=2),
    }

    st.caption(t("required_answers"))

    clicked = st.button(t("save_and_continue"), type="primary", use_container_width=True)
    if clicked:
        missing = []
        if not activities:
            missing.append(qs("activities_q"))
        if any(is_other(v) for v in activities) and not activities_other:
            missing.append(f"{qs('activities_q')} — {specify_label()}")

        if is_other(industry) and not industry_other:
            missing.append(f"{qs('industry_q')} — {specify_label()}")

        if is_other(work_type) and not work_type_other:
            missing.append(f"{qs('work_type_q')} — {specify_label()}")

        if missing:
            st.error(t("missing_fields") + ", ".join(missing))
            st.stop()

        survey = {
            "lang": st.session_state.lang,
            "device_id": DEVICE_ID,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "age": age, "gender_bio": gender, "marital": marital,
            "disability": disability, "sleep_hours": sleep_hours, "sleep_problem": sleep_problem,
            "employment": employment,
            "industry": industry, "industry_other": industry_other,
            "work_type": work_type, "work_type_other": work_type_other,
            "emotional": emotional, "stress": stress,
            "activities": activities,
            "activities_other": activities_other,
            "days_per_week": days,
            "session_length": session_len,
            "mood_link": mood_link,
            "overall_health": overall_health, "mobility": mobility, "surgery": surgery,
            "recovery": recovery, "pt_after": pt_after, "pt_adherence": pt_adherence,
            "big5": big5,
            "video_done": video_done,
        }

        append_jsonl(DEVICE_ID, "survey", survey)   # <- append, not overwrite
        st.success(t("saved"))
        st.session_state.step = "guidance"
        st.rerun()

    footer()
    
def _likert_scale_words():
    return qs("likert7") or [
        "Disagree strongly",
        "Disagree moderately",
        "Disagree slightly",
        "Neither agree nor disagree",
        "Agree slightly",
        "Agree moderately",
        "Agree strongly",
    ]

def likert_word_to_num(value: str) -> int:
    """Mappe un libellé Likert (toute langue) vers 1..7. Fallback=4 (Neutral)."""
    scale = _likert_scale_words()
    norm = str(value).strip().lower()
    for i, w in enumerate(scale, start=1):
        if norm == str(w).strip().lower():
            return i
    return 4


def page_guidance():

    st.markdown("### Assessment & AMM Prediction")

    ud = load_latest_jsonl(DEVICE_ID, "survey")
    if not ud:
        st.info("No study answers found yet. Please complete the questions first.")
        if st.button(t("back")):
            st.session_state.step = "survey"; st.rerun()
        return


    c_left, c_right = st.columns(2)

    # ---- Chart 1 : Predicted pain/difficulty ----
    with c_left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(t("anticipated"))

        df_diff = pd.DataFrame({
            "Exercise": [t("ex_situps")],
            #t("ex_toe_touch"), t("ex_squats"), t("ex_calf_raises")],
            "NumericScore": [3],
        })
        score_map = {1: t("diff1"), 2: t("diff2"), 3: t("diff3"), 4: t("diff4"), 5: t("diff5")}

        if ALTAIR_AVAILABLE:
            df = df_diff.copy()
            df["ScoreLabel"] = df["NumericScore"].map(score_map)

            base = alt.Chart(df).properties(height=280)

            bars = (
                base.mark_bar(size=30, cornerRadiusTopLeft=6, cornerRadiusBottomLeft=6, opacity=0.95)
                .encode(
                    y=alt.Y("Exercise:O", sort=None, axis=alt.Axis(title=None)),
                    x=alt.X("NumericScore:Q",
                            title=t("nrs"),
                            scale=alt.Scale(domain=[0, 5], nice=False, zero=True),
                            axis=alt.Axis(tickMinStep=1)),
                    color=alt.value("#2563eb"),
                    tooltip=[alt.Tooltip("Exercise:N"),
                             alt.Tooltip("NumericScore:Q", title=t("score_word"))],
                )
            )

            labels = (
                base.mark_text(dx=6, fontSize=12, align="left")
                .encode(
                    y=alt.Y("Exercise:O", sort=None),
                    x=alt.X("NumericScore:Q"),
                    text=alt.Text("ScoreLabel:N"),
                )
            )

            chart = (
                alt.layer(bars, labels)
                  .properties(padding={"left": 10, "right": 10, "top": 10, "bottom": 10})
                  .configure(background="white")
                  .configure_view(stroke=None)
                  .configure_axis(grid=True, gridColor="#e2e8f0",
                                  labelColor="#0f172a", titleColor="#0f172a")
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.bar_chart(df_diff.set_index("Exercise").T)

        st.markdown("</div>", unsafe_allow_html=True)



    # ---- Chart 2 : Traits ----
    with c_right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(t("traits"))

        b5_ud = ud.get("big5", {}) or {}
        fake_ud = {
            "Extroversion":         likert_word_to_num(b5_ud.get("extrav", "Neutral")),
            "Agreeableness":        likert_word_to_num(b5_ud.get("warm", "Agree")),
            "Conscientiousness":    likert_word_to_num(b5_ud.get("discipline", "Agree")),
            "Emotional_Stability":  likert_word_to_num(b5_ud.get("stable", "Neutral")),
            "Openness":             likert_word_to_num(b5_ud.get("open", "Agree")),
        }
        norms = {
            "Extroversion": 4.4, "Agreeableness": 5.2, "Conscientiousness": 5.4,
            "Emotional_Stability": 4.8, "Openness": 5.4
        }

        # Localized labels for the X-axis
        trait_labels = {
            "Extroversion": t("trait_ext"),
            "Agreeableness": t("trait_agr"),
            "Conscientiousness": t("trait_con"),
            "Emotional_Stability": t("trait_emo"),
            "Openness": t("trait_ope"),
        }

        # >>> fixed order of the 5 lines to ensure that they are all displayed
        order_traits = [
            t("trait_ext"),
            t("trait_agr"),
            t("trait_con"),
            t("trait_emo"),
            t("trait_ope"),
        ]

        # Data (norms vs. user)
        data = []
        for k, v in fake_ud.items():
            tl = trait_labels[k]
            data += [
                {"Trait": tl, "Group": t("group_norm"), "Score": norms[k]},
                {"Trait": tl, "Group": t("group_user"), "Score": v},
            ]
        df = pd.DataFrame(data)

        if ALTAIR_AVAILABLE:
            base = alt.Chart(df).properties(
                height=300,
                padding={"left": 10, "right": 10, "top": 10, "bottom": 10},
            )

            chart = (
                base.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                .encode(
                    # enforce the order and keep the 5 labels
                    x=alt.X(
                        "Trait:N",
                        sort=order_traits,
                        axis=alt.Axis(
                            labelAngle=0,
                            labelFontSize=6,
                            title=None,
                            labelColor="#0f172a",
                            labelLimit=140
                        ),
                    ),
                    y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 7]), title=t("amm_score")),
                    xOffset=alt.X("Group:N", sort=[t("group_norm"), t("group_user")]),
                    color=alt.Color(
                        "Group:N",
                        sort=[t("group_norm"), t("group_user")],
                        # ► visible legend + dark captions
                        legend=alt.Legend(
                            title=t("group"),
                            orient="bottom",
                            columns=2,
                            labelColor="#0f172a",
                            titleColor="#0f172a",
                        ),
                        scale=alt.Scale(range=["#9ca3af", "#2563eb"]),  # Norms = gray, User = blue
                    ),
                    tooltip=["Trait:N", "Group:N", "Score:Q"],
                )
            ).configure(background="white") \
             .configure_view(stroke=None) \
             .configure_axis(grid=True, gridColor="#e2e8f0",
                             labelColor="#0f172a", titleColor="#0f172a")

            st.altair_chart(chart, use_container_width=True)
        else:
            st.bar_chart(df.pivot(index="Trait", columns="Group", values="Score"))
        
        agree = st.checkbox(t("agree_with_model"), key="agree_model")
        # Save user's agreement feedback to JSONL
        if st.button(t("save_locally"), key="save_agree_btn", use_container_width=True):
            append_jsonl(
                DEVICE_ID,
                "agreement",   # -> data/<DEVICE_ID>/agreement.jsonl
                {
                    "device_id": DEVICE_ID,
                    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                    "lang": st.session_state.lang,
                    "agree_with_model": bool(agree),
                },
            )
            st.success(t("saved"))

        st.markdown("</div>", unsafe_allow_html=True)



# -----------------
#  MAIN ROUTER
# -----------------
def main():
    step = st.session_state.step

    if step == "welcome":
        page_welcome()
    elif step == "consent":
        page_consent()
    elif step == "survey":
        page_study_questions()
    elif step == "guidance":
        page_guidance()
    else:
        st.session_state.step = "welcome"
        st.rerun()


if __name__ == "__main__":
    main()
