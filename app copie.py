# app.py
"""
Mentalytics – Pilot Flow (Light theme + i18n + per-device local save)
"""

import os
import json
import uuid
import datetime
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

/* ===== Checkboxes bien noirs ===== */
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

/* --- Boutons désactivés visibles --- */
.stButton > button:disabled,
[data-testid="baseButton-primary"][disabled] {
  background: #e2e8f0 !important;
  color: #475569 !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: none !important;
  opacity: 1 !important;
  cursor: not-allowed !important;
}

/* --- st.download_button lisible (ghost) --- */
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

/* Forcer le texte des boutons primaires en blanc */
.stButton > button { color: #fff !important; }

/* === Radios : forcer le texte des réponses en noir === */
div[data-testid="stRadio"] div[role="radiogroup"] label,
div[data-testid="stRadio"] div[role="radiogroup"] span,
div[data-testid="stRadio"] div[role="radiogroup"] p {
  color: var(--fg) !important;   /* noir (fg) */
  opacity: 1 !important;
  font-weight: 500;
}

/* Le label principal (ex : "Gender (Biological)") peut rester gris */
div[data-testid="stRadio"] > label {
  color: var(--muted) !important;
  font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# -----------------
#  I18N STRINGS
# -----------------
STRINGS: Dict[str, Dict[str, Any]] = {
    "en": {
        "app_title": "Mentalytics: When AI Reads Your Mind",
        "welcome_intro": "Welcome to our pilot study. Please choose your language to continue.",
        "lang_fr": "Français", "lang_de": "Deutsch", "lang_en": "English",
        "consent_title": "Informed Consent of Participation",
        "consent_intro": "Please review the information below. Tick both boxes to proceed.",
        "consent_checkbox": "I have read the study information and I agree to participate.",
        "consent_checkbox2": "I consent to the storage and local processing of my answers as described.",
        "continue": "Continue",
        "intro_title": "Before we begin",
        "intro_body": "This pilot will ask a few questions about you and your health. It should take about 5–7 minutes.",
        "start_study": "Start the study",
        "profile_title": "Quick Profile",
        "save_locally": "Save locally",
        "saved": "Saved locally.",
        "next": "Next",
        "back": "Back",
        "guidance_title": "Guidance",
        "device": "Device",
        "export": "Export data",
        # Profile fields
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
        # Chart area
        "anticipated": "Patient Anticipated Pain/Difficulty",
        "nrs": "Numeric Rating Scale (NRS)",
        "traits": "Patient Personality Traits & Insights",
        # Study survey page
        "study_title": "Study Questions",
        "save_and_continue": "Save & Continue",
        # German explainer
        "de_blurb_title": "Mentalytics: Wenn die KI weiß, wie du dich fühlst",
        "de_blurb": (
            "KI zum Anfassen: Mentalytics ist ein KI-Assistent für Rehabilitation und Training. "
            "Er nutzt künstliche mentale Modelle, berücksichtigt Erwartungen, Fitness und Stimmung – "
            "und sagt voraus, wie anstrengend eine Übung erlebt wird und ob sie gelingt. "
            "Die KI schätzt dein Empfinden ein – **bevor** du loslegst. Du wirst überrascht sein, wie gut sie dich kennt."
        ),
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
2. Participants then enter basic demographic information (age group, sex, activity level) and rate their expected exertion on a **1–5 scale**.  
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
and in compliance with the GDPR, for no longer than required by the funding organization (**10 years**) or if you contact
the researchers to destroy or delete them immediately. As with any publication or online-related activity, the risk of a
breach of confidentiality or anonymity is always possible. According to the GDPR, the researchers will inform the participant
if a breach of confidential data was detected.

### 6. Identification of Investigators (Contact)
- **Prajvi Saxena**, Student Researcher — prajvi.saxena@dfki.de  
- **Dr.-Ing. Sabine Janzen**, Principal Investigator — Trippstadter Str. 122, 67663 Kaiserslautern, Germany — sabine.janzen@dfki.de  
- **Prof. Dr.-Ing. Wolfgang Maaß**, Head of Department — Trippstadter Str. 122, 67663 Kaiserslautern, Germany

### 7. Informed Consent and Agreement
This consent form will be retained securely and in compliance with the GDPR for no longer than necessary.
"""
    },
    "de": {
        "app_title": "Mentalytics: Wenn die KI weiß, wie du dich fühlst",
        "welcome_intro": "Willkommen zu unserer Pilotstudie. Bitte wähle deine Sprache aus, um fortzufahren.",
        "lang_fr": "Französisch", "lang_de": "Deutsch", "lang_en": "Englisch",
        "consent_title": "Einverständniserklärung",
        "consent_intro": "Bitte lies die Infos unten. Kreuze beide Kästchen an, um fortzufahren.",
        "consent_checkbox": "Ich habe die Studieninformation gelesen und stimme der Teilnahme zu.",
        "consent_checkbox2": "Ich willige in die lokale Speicherung und Verarbeitung meiner Antworten ein.",
        "continue": "Weiter",
        "intro_title": "Bevor wir starten",
        "intro_body": "Dieses Pilot fragt ein paar Dinge zu dir und deiner Gesundheit (ca. 5–7 Minuten).",
        "start_study": "Studie starten",
        "profile_title": "Kurzprofil",
        "save_locally": "Lokal speichern",
        "saved": "Lokal gespeichert.",
        "next": "Weiter",
        "back": "Zurück",
        "guidance_title": "Leitfaden",
        "device": "Gerät",
        "export": "Daten exportieren",
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
        "de_blurb_title": "Mentalytics: Wenn die KI weiß, wie du dich fühlst",
        "de_blurb": (
            "KI zum Anfassen: Mentalytics ist ein KI-Assistent für Rehabilitation und Training. "
            "Er nutzt künstliche mentale Modelle, berücksichtigt Erwartungen, Fitness und Stimmung – "
            "und sagt voraus, wie anstrengend eine Übung erlebt wird und ob sie gelingt. "
            "Die KI schätzt dein Empfinden ein – **bevor** du loslegst. Du wirst überrascht sein, wie gut sie dich kennt."
        ),
        # ---- Consent localized strings (DE) ----
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
eines **On-Device**-Einsatzes für zukünftige Anwendungen in Digital Health und Rehabilitation. Ihre Teilnahme unterstützt dieses Ziel.
Ergebnisse können auf Tagungen präsentiert oder veröffentlicht werden.

### 2. Teilnahme und Aufwandsentschädigung
Die Teilnahme ist **freiwillig**. Etwa 200 Personen werden befragt. Es gibt **keine Vergütung**. Ein Rücktritt ist jederzeit
**ohne Nachteile** möglich. Bei Ablehnung/Rücktritt wird niemand auf dem Campus informiert. Eine Teilnahmebestätigung kann ausgestellt werden.

### 3. Ablauf
Nach der Einwilligung:
1. Kurzes Sicherheitsscreening (Ja/Nein).  
2. Basisdaten + Bewertung der **erwarteten** Anstrengung (**1–5**).  
3. Durchführung der Übung unter Aufsicht (Sicherheit + Beobachtung des Erfolgs).  
4. Unmittelbar danach Bewertung der **tatsächlichen** Anstrengung, Angabe des Erfolgs, kurze Usability/Trust-Fragen.  
5. Parallel dokumentiert das Team eine Ground-Truth nach vordefinierten Regeln.  
6. Alle Daten werden **lokal**, anonymisiert und verschlüsselt gespeichert, **ohne** Cloud-Dienste.

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

Alle Daten werden vertraulich behandelt, **verschlüsselt** gespeichert und sind außerhalb des Projekts nicht einsehbar,
sofern keine gesonderte Erlaubnis vorliegt. Die Verarbeitung erfolgt gemäß **DSGVO**. Verwaltung/Lehrende erhalten keinen
Zugriff auf Rohdaten. Rohdaten/Material werden sicher und DSGVO-konform bis zur vom Förderer geforderten Dauer (**10 Jahre**)
aufbewahrt oder auf Wunsch früher gelöscht. Wie bei allen Online-Aktivitäten bleibt ein Restrisiko für Datenschutzverletzungen.
Im Falle eines Vorfalls werden Betroffene gemäß DSGVO informiert.

### 6. Kontakt
- **Prajvi Saxena**, Studentische Forscherin — prajvi.saxena@dfki.de  
- **Dr.-Ing. Sabine Janzen**, Studienleitung — Trippstadter Str. 122, 67663 Kaiserslautern — sabine.janzen@dfki.de  
- **Prof. Dr.-Ing. Wolfgang Maaß**, Abteilungsleitung — Trippstadter Str. 122, 67663 Kaiserslautern

### 7. Einwilligung
Dieses Formular wird sicher und DSGVO-konform nur so lange wie nötig aufbewahrt.
"""
    },
    "fr": {
        "app_title": "Mentalytics : Quand l’IA lit dans vos pensées",
        "welcome_intro": "Bienvenue dans notre étude pilote. Veuillez choisir votre langue pour continuer.",
        "lang_fr": "Français", "lang_de": "Allemand", "lang_en": "Anglais",
        "consent_title": "Consentement éclairé à participer",
        "consent_intro": "Veuillez lire les informations ci-dessous. Cochez les deux cases pour continuer.",
        "consent_checkbox": "J’ai lu les informations et j’accepte de participer.",
        "consent_checkbox2": "J’accepte l’enregistrement local et le traitement décrit de mes réponses.",
        "continue": "Continuer",
        "intro_title": "Avant de commencer",
        "intro_body": "Ce pilote pose quelques questions sur vous et votre santé (environ 5–7 minutes).",
        "start_study": "Commencer l’étude",
        "profile_title": "Profil rapide",
        "save_locally": "Enregistrer en local",
        "saved": "Enregistré en local.",
        "next": "Suivant",
        "back": "Retour",
        "guidance_title": "Conseils",
        "device": "Appareil",
        "export": "Exporter les données",
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
        "anticipated": "Douleur / difficulté anticipée",
        "nrs": "Échelle numérique (NRS)",
        "traits": "Traits de personnalité & insights",
        "study_title": "Questions d’étude",
        "save_and_continue": "Enregistrer et continuer",
        "de_blurb_title": "Mentalytics : Quand l’IA lit dans vos pensées",
        "de_blurb": (
            "KI zum Anfassen : Mentalytics est un assistant IA pour la rééducation et l’entraînement. "
            "Il s’appuie sur des modèles mentaux artificiels, prend en compte attentes, forme et humeur – "
            "et prédit l’effort perçu et la réussite d’un exercice **avant** de commencer."
        ),
        # ---- Consent localized strings (FR) ----
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

L’alternative à la participation est de **ne pas** participer. Pour toute question concernant la procédure de consentement
ou vos droits en tant que participant(e), contactez le comité d’éthique (DFKI) et la Dr-Ing. Sabine Janzen (e-mail : **sabine.janzen@dfki.de**).
Veuillez lire attentivement les informations ci-dessous et prendre le temps nécessaire.

---

### 1. Objet et but de la recherche
L’étude vise à tester si le système Mentalytics peut prédire avec précision l’effort perçu et l’achèvement d’une tâche lors
d’un court exercice supervisé dans un contexte réel (festival). L’objectif est d’évaluer la faisabilité, la sécurité et la
fiabilité d’un déploiement **sur l’appareil** pour des usages futurs en e-santé et rééducation. Vos réponses contribueront à cet objectif.
Les résultats pourront être présentés lors d’événements scientifiques ou publiés.

### 2. Participation et compensation
Votre participation est **volontaire**. Environ 200 personnes seront interrogées. Aucune compensation n’est prévue.
Vous pouvez vous retirer **sans pénalité** à tout moment. En cas de refus/retrait, personne sur le campus n’en sera informé.
Vous pouvez demander une attestation de participation.

### 3. Déroulement
Après le consentement :
1. Triage rapide de sécurité (questions oui/non).  
2. Données démographiques de base + évaluation de l’effort **anticipé** (échelle 1–5).  
3. Exécution de l’exercice sous supervision (sécurité + observation de la réussite).  
4. Évaluation de l’effort **réel**, réussite de la tâche, puis quelques questions d’utilisabilité et de confiance.  
5. En parallèle, le personnel note la « vérité terrain » selon des règles prédéfinies.  
6. Toutes les données sont stockées **localement** de façon anonymisée et chiffrée, **sans** services cloud.

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

Toutes les données seront traitées de manière confidentielle, **chiffrées** et **non accessibles** à des personnes extérieures
au projet, sauf autorisation spécifique. Le traitement respecte le **RGPD**. Le personnel administratif du campus n’aura pas
accès aux données brutes. Les données et matériels seront conservés en sécurité et conformément au RGPD pendant la durée
requise par le financeur (**10 ans**) ou détruits plus tôt à votre demande. Comme pour toute activité en ligne, un risque
résiduel de violation de la confidentialité ne peut être totalement exclu. Conformément au RGPD, toute violation détectée
sera notifiée aux personnes concernées.

### 6. Contacts
- **Prajvi Saxena**, étudiante-chercheuse — prajvi.saxena@dfki.de  
- **Dr-Ing. Sabine Janzen**, investigatrice principale — Trippstadter Str. 122, 67663 Kaiserslautern, Allemagne — sabine.janzen@dfki.de  
- **Prof. Dr-Ing. Wolfgang Maaß**, directeur du département — Trippstadter Str. 122, 67663 Kaiserslautern, Allemagne

### 7. Consentement
Ce formulaire sera conservé de manière sécurisée et conforme au RGPD pour la durée nécessaire.
"""
    },
}

# Default language (until user chooses)
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Step machine: welcome → consent → intro → survey → guidance
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

def save_json(device_id: str, name: str, payload: dict):
    d = device_dir(device_id)
    path = os.path.join(d, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def load_json(device_id: str, name: str) -> dict:
    path = os.path.join(device_dir(device_id), f"{name}.json")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def export_device_zip_notice():
    # Export as combined JSON for simplicity
    consent = load_json(DEVICE_ID, "consent")
    survey = load_json(DEVICE_ID, "survey")
    profile = load_json(DEVICE_ID, "profile")
    bundle = {"device_id": DEVICE_ID, "consent": consent, "survey": survey, "profile": profile}
    data = json.dumps(bundle, ensure_ascii=False, indent=2)
    st.download_button(key="export_btn", label=t("export"), data=data,
                       file_name=f"{DEVICE_ID}_data.json", mime="application/json")

# -----------------
#  ASSETS
# -----------------
def find_asset(*candidates: str) -> Optional[str]:
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


# -----------------
#  UTIL / I18N
# -----------------
def t(key: str) -> str:
    lang = st.session_state.lang
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)

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
    st.markdown(f"<h1 class='center'>{t('app_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='center'>{t('welcome_intro')}</p>", unsafe_allow_html=True)
    st.write("")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"🇫🇷 {t('lang_fr')}", use_container_width=True):
            st.session_state.lang = "fr"
            st.session_state.step = "consent"
            st.rerun()
    with c2:
        if st.button(f"🇩🇪 {t('lang_de')}", use_container_width=True):
            st.session_state.lang = "de"
            st.session_state.step = "consent"
            st.rerun()
    with c3:
        if st.button(f"🇬🇧 {t('lang_en')}", use_container_width=True):
            st.session_state.lang = "en"
            st.session_state.step = "consent"
            st.rerun()

    st.markdown("<div class='footer'>DFKI – FedWell</div>", unsafe_allow_html=True)


def page_consent():
    header("consent_title")
    st.write(t("consent_intro"))

    # --- Localized expander + markdown ---
    with st.expander(t("consent_info_header"), expanded=False):
        st.markdown(t("consent_md"))

    # --- Two required localized checkboxes ---
    agree_info = st.checkbox(t("consent_check1"))
    agree_data = st.checkbox(t("consent_check2"))

    can_continue = agree_info and agree_data

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button(t("continue"), disabled=not can_continue, use_container_width=True):
            payload = {
                "agreed_info": bool(agree_info),
                "agreed_data": bool(agree_data),
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                "lang": st.session_state.lang,
            }
            save_json(DEVICE_ID, "consent", payload)
            st.session_state.step = "intro"
            st.rerun()
    with col2:
        export_device_zip_notice()

    st.markdown("<div class='footer'>DFKI – FedWell</div>", unsafe_allow_html=True)


def page_intro():
    header("intro_title")
    st.write(t("intro_body"))

    # German explainer + photos
    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
    st.subheader(t("de_blurb_title"))
    st.write(t("de_blurb"))

    img1 = find_asset(
        "assets/physio1.jpg", "assets/physio1.jpg",
        "/mnt/data/6e2d1f05-aecb-4ab1-b170-33132d9ed6cb.png"
    )
    img2 = find_asset(
        "assets/physio2.jpg", "assets/physio2.jpg",
        "/mnt/data/f0a2cd48-3600-4f18-a262-6e64ccd42b1b.png"
    )
    c1, c2 = st.columns(2)
    with c1:
        if img1: st.image(img1, use_container_width=True)
    with c2:
        if img2: st.image(img2, use_container_width=True)

    st.caption("Note: a short exercise video will be embedded here (Prajvi to provide).")

    st.write("")
    if st.button(t("start_study"), use_container_width=True):
        st.session_state.step = "survey"
        st.rerun()
    st.markdown("<div class='footer'>DFKI – FedWell</div>", unsafe_allow_html=True)


# ------- STUDY QUESTIONS (Google Form content, compact for mobile) -------
def page_study_questions():
    header("study_title")

    with st.form("study_form"):
        st.markdown("### Demographics")
        age = st.selectbox(t("age"), [str(i) for i in range(1, 101)])
        gender = st.radio("Gender (Biological)", ["Male", "Female"])
        marital = st.radio("What is your marital status?",
                           ["Single","Married","Divorced","Widowed","Prefer not to answer"])

        st.markdown("### Health & Accessibility")
        disability = st.radio("Disability Status", ["Yes","No","Prefer not to answer"])
        sleep_hours = st.radio("How many hours do you sleep per day on average?",
                               ["4–5 Hours","5–6 Hours","6–7 Hours","7–8 Hours","8–9 Hours","Less than 4 Hours","More than 9 Hours"])
        sleep_problem = st.radio("Have you had any problems falling asleep or staying asleep lately?", ["Yes","No"])

        st.markdown("### Employment")
        employment = st.radio("Employment status",
                              ["Employed","Unemployed","Student","Retired","Unable to work due to disability","Homemaker/caregiver"])
        industry = st.selectbox("If employed, in which industry do you primarily work?",
                                ["Healthcare and social assistance","Education","Professional/business services","Retail trade",
                                 "Manufacturing","Construction","Transportation/warehousing","Food service/accommodation",
                                 "Government/public administration","Information technology","Finance/insurance","Other (please specify)"])
        work_type = st.selectbox("Which best describes your primary work activities?",
                                 ["Office/desk work","Standing service work (retail, reception)","Skilled manual work (trades, repair)",
                                  "Physical labor (construction, warehouse)","Driving/transportation","Public safety/emergency services","Other"])

        st.markdown("### Psychological Well-Being and Emotional State")
        emotional = st.radio("What is your current emotional state?",
                             ["Happy","Calm","Neutral","Anxious","Frustrated","Sad","Stressed"])
        stress = st.selectbox("What do you think about your stress level in your daily life?",
                              ["Low","Moderate","High"])

        st.markdown("### Physical Activity and Lifestyle Habits")
        activities = st.multiselect("What types of physical activities do you participate in?",
                                    ["Cardio/Aerobic exercise","Strength/Resistance training","Flexibility/Stretching",
                                     "Sports (team or individual)","Recreational activities","Dance/Movement",
                                     "Outdoor activities","Water activities","I don't participate in physical activities","Other (please specify)"])
        days = st.radio("How many days per week do you engage in physical activity or exercise?",
                        ["1–2 Days","2–3 Days","3–4 Days","4–5 Days","5–6 Days","7 Days"])
        session_len = st.radio("On average, how long is each physical activity session?",
                               ["Under 30 minutes","30–60 minutes","1–2 hours","More than 2 hours"])
        mood_link = st.radio("How do you associate your mental health with your exercise habits?",
                             ["I exercise more when I am happy","I exercise more when I am sad",
                              "My exercise habits are not significantly influenced by my mood."])

        st.markdown("### Health status & history")
        overall_health = st.radio("How would you rate your overall health status?", ["1","2","3","4","5"])
        mobility = st.radio("How would you rate your current mobility?", ["1","2","3","4","5"])
        surgery = st.radio("Have you undergone any surgical procedure?", ["Yes","No"])
        recovery = st.radio("How long was your recovery period ?",
                            ["Under 2 weeks","2–4 weeks","1–3 months","3–6 months","6–12 months","Over 1 year","Ongoing recovery"])
        pt_after = st.radio("Did you undergo physical therapy after your surgery?", ["Yes","No"])
        pt_adherence = st.radio("Did you adhere to your prescribed physical therapy plan?", ["1","2","3","4","5"])

        st.markdown("### Core Personality Dimensions (1–7)")
        scale7 = ["1","2","3","4","5","6","7"]
        big5 = {}
        big5["extrav"] = st.radio("I see myself as Extraverted and Enthusiastic", scale7, horizontal=True)
        big5["quarrel"] = st.radio("I see myself as critical and quarrelsome", scale7, horizontal=True)
        big5["discipline"] = st.radio("I see myself as dependable and self-disciplined", scale7, horizontal=True)
        big5["anxious"] = st.radio("I see myself as anxious and easily upset", scale7, horizontal=True)
        big5["open"] = st.radio("I see myself as open to new experiences and complex", scale7, horizontal=True)
        big5["quiet"] = st.radio("I see myself as reserved and quiet", scale7, horizontal=True)
        big5["warm"] = st.radio("I see myself as sympathetic and warm", scale7, horizontal=True)
        big5["careless"] = st.radio("I see myself as disorganized and careless", scale7, horizontal=True)
        big5["stable"] = st.radio("I see myself as calm and emotionally stable", scale7, horizontal=True)
        big5["uncreative"] = st.radio("I see myself as conventional, uncreative", scale7, horizontal=True)

        submitted = st.form_submit_button(t("save_and_continue"))
        if submitted:
            survey = {
                "lang": st.session_state.lang,
                "device_id": DEVICE_ID,
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                "age": age, "gender_bio": gender, "marital": marital,
                "disability": disability, "sleep_hours": sleep_hours, "sleep_problem": sleep_problem,
                "employment": employment, "industry": industry, "work_type": work_type,
                "emotional": emotional, "stress": stress,
                "activities": activities, "days_per_week": days, "session_length": session_len, "mood_link": mood_link,
                "overall_health": overall_health, "mobility": mobility, "surgery": surgery,
                "recovery": recovery, "pt_after": pt_after, "pt_adherence": pt_adherence,
                "big5": big5,
            }
            save_json(DEVICE_ID, "survey", survey)
            st.success(t("saved"))
            st.session_state.step = "guidance"
            st.rerun()


def page_guidance():
    header("guidance_title")

    ud = load_json(DEVICE_ID, "survey")
    if not ud:
        st.info("No study answers found yet. Please complete the questions first.")
        if st.button(t("back")):
            st.session_state.step = "survey"; st.rerun()
        return

    st.subheader("Participant Snapshot")
    cols = st.columns(2)
    with cols[0]:
        st.write(f"**{t('age')}**: {ud.get('age','—')}")
        st.write(f"**Gender**: {ud.get('gender_bio','—')}")
        st.write(f"**Employment**: {ud.get('employment','—')}")
        st.write(f"**Industry**: {ud.get('industry','—')}")
        st.write(f"**Activities**: {', '.join(ud.get('activities', [])) or '—'}")
    with cols[1]:
        st.write(f"**Emotion**: {ud.get('emotional','—')}")
        st.write(f"**Stress**: {ud.get('stress','—')}")
        st.write(f"**Overall health**: {ud.get('overall_health','—')}/5")
        st.write(f"**Mobility**: {ud.get('mobility','—')}/5")
        st.write(f"**Surgery/PT**: {ud.get('surgery','—')} / PT: {ud.get('pt_after','—')}")

    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader(t("anticipated"))
        df_diff = pd.DataFrame({
            "Exercise": ["Sit-ups (30s)", "Toe Touch", "Squats", "Calf Raises"],
            "NumericScore": [3, 3, 3, 3],  # placeholder
        })
        if ALTAIR_AVAILABLE:
            score_map = {1:"1 - Not difficult",2:"2 - Slightly difficult",3:"3 - Moderately difficult",
                         4:"4 - Very difficult",5:"5 - Extremely difficult"}
            df = df_diff.copy()
            df["ScoreLabel"] = df["NumericScore"].map(score_map)
            chart = (
                alt.Chart(df)
                .mark_bar(size=32)
                .encode(
                    x=alt.X("Exercise:O", sort=None, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("NumericScore:Q", title=t("nrs")),
                    color=alt.Color("ScoreLabel:N", legend=alt.Legend(title="Difficulty Level"),
                                    sort=list(score_map.values()))
                ).properties(height=260)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.bar_chart(df_diff.set_index("Exercise")["NumericScore"])
    with c_right:
        st.subheader(t("traits"))
        fake_ud = {
            "Extroversion": int(ud.get("big5", {}).get("extrav", "4")),
            "Agreeableness": int(ud.get("big5", {}).get("warm", "5")),
            "Conscientiousness": int(ud.get("big5", {}).get("discipline", "5")),
            "Emotional_Stability": int(ud.get("big5", {}).get("stable", "4")),
            "Openness": int(ud.get("big5", {}).get("open", "5")),
        }
        # mini chart
        data = []
        norms = {"Extroversion":4.4, "Agreeableness":5.2, "Conscientiousness":5.4, "Emotional_Stability":4.8, "Openness":5.4}
        for k,v in fake_ud.items():
            data += [{"Trait":k,"Group":"User","Score":v},{"Trait":k,"Group":"Norm","Score":norms[k]}]
        df = pd.DataFrame(data)
        if ALTAIR_AVAILABLE:
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(x=alt.X("Trait:N", axis=alt.Axis(labelAngle=0), title=None),
                        y=alt.Y("Score:Q", scale=alt.Scale(domain=[0,7]), title="Score (out of 7)"),
                        xOffset="Group:N", color="Group:N")
                .properties(height=300)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.bar_chart(df.pivot(index="Trait", columns="Group", values="Score"))

    st.markdown("<div class='footer'>DFKI – FedWell</div>", unsafe_allow_html=True)


# -----------------
#  MAIN ROUTER
# -----------------
def main():
    step = st.session_state.step

    if step == "welcome":
        page_welcome()
    elif step == "consent":
        page_consent()
    elif step == "intro":
        page_intro()
    elif step == "survey":
        page_study_questions()
    elif step == "guidance":
        page_guidance()
    else:
        st.session_state.step = "welcome"
        st.rerun()


if __name__ == "__main__":
    main()
