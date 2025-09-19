# 🧠 Bachelorarbeit – AMM Mobile App (Mentalytics Prototype)

This repository contains the **prototype application** developed as part of my **Bachelor’s Thesis** at **DFKI** and **HTW Saar**.  
It demonstrates a **privacy-preserving, offline-first mobile web app** that integrates an **Artificial Mental Model (AMM)** for healthcare support.

Built with **Streamlit**, the app is fully responsive (desktop & mobile), supports **multi-language UI (EN/DE/FR)**, and stores all data **locally on-device**.

---

## 📚 Table of Contents

- [Project Description](#-project-description)  
- [Key Features](#-key-features)  
- [Privacy & Offline Design](#-privacy--offline-design)  
- [User Flow](#-user-flow)  
- [UI Pages](#-ui-pages)  
- [Project Structure](#-project-structure)  
- [Installation & Usage](#-installation--usage)  
- [Future Work](#-future-work)  
- [Author](#-author)  
- [Timeline](#-timeline)  

---

## 📜 Project Description

The goal is to design and implement a **lightweight mobile web application** for pilot studies,  
integrating an **Artificial Mental Model (AMM)** as a digital companion for physiotherapy and rehabilitation.

The application:
- Runs on **any local device** (smartphones, tablets, laptops) via a browser.  
- Provides a **step-by-step flow** from language choice → consent → study survey → patient profile → physio dashboard.  
- Ensures strict **data privacy** by storing all participant data **locally only**.  
- Uses **Streamlit** for UI and **Altair** for visual analytics.  

---

## ✨ Key Features

- 🌐 **Multi-language UI** (English, German, French).  
- 📝 **Consent page** with full **Informed Consent form** integrated.  
- 📊 **Survey questions** (demographics, health, lifestyle, personality traits).  
- 📱 **Mobile-first layout** (single-column, responsive, large buttons).  
- 💾 **Local storage per device** (unique device IDs, JSON files).  
- 📤 **Data export**: bundle consent + survey + profile into a downloadable JSON.  
- 📈 **Charts & Insights**:  
  - Anticipated difficulty ratings (bar charts).  
  - Personality traits vs. norms (Big Five radar-style comparison).  
- 🔒 **Privacy-first**: no cloud, no tracking, no internet required.  

---

## 🔐 Privacy & Offline Design

- All data (consent forms, survey answers, profiles) are stored **locally** in the `data/` folder, separated per device ID.  
- No internet connection required: everything works **offline**.  
- Exports are provided as `.json` bundles for local analysis.  
- Designed for **pilot studies** at festivals, workshops, or clinics with multiple mobile devices.  

---

## 🚀 User Flow

1. **Welcome** → User selects language (EN/DE/FR).  
2. **Consent** → Full informed consent form + two required checkboxes.  
3. **Intro** → Short explanation of the study, German explainer text + images.  
4. **Survey** → Multi-section questionnaire: demographics, health, habits, emotions, Big Five traits.  
5. **Guidance Dashboard** →  
   - Snapshot of participant profile.  
   - Charts: anticipated difficulty + personality traits comparison.  
   - Export button for local data.  

---

## 📱 UI Pages

1. **Welcome Page**  
   - Title, intro text, and 3 language buttons.  

2. **Consent Page**  
   - Integrated **full informed consent** text.  
   - Two checkboxes required before continuing.  
   - Export data option.  

3. **Intro Page**  
   - Short explainer.  
   - Embedded German description (for booth visitors).  
   - Images illustrating physiotherapy context.  
   - "Start the Study" button.  

4. **Survey Page (Study Questions)**  
   - Compact, mobile-friendly forms.  
   - Sections: demographics, health & lifestyle, psychological state, Big Five.  
   - One **Save & Continue** button at the bottom.  

5. **Guidance Page (Dashboard)**  
   - Participant snapshot.  
   - **Charts**:  
     - Exercise difficulty ratings (NRS).  
     - Big Five traits vs. population norms.  
   - Local export.  

---

## 📁 Project Structure

```
bachelorarbeit-amm/
├── app.py                   # Main Streamlit app (UI + flow)
├── requirements.txt         # Python dependencies
├── README.md                # Documentation
├── data/                    # Local storage (per device, auto-created)
├── assets/                  # Images, logos
├── doc/                     # Notes, screenshots, thesis materials
```

---

## ⚙️ Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/lucasbodner/bachelorarbeit-amm.git
cd bachelorarbeit-amm
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in a browser.  
👉 Works on both desktop and mobile devices (same Wi-Fi/local network).

---

## 🔮 Future Work

- Integration with **llama.cpp** for local AMM inference.  
- Embedding **short exercise videos** on the intro page.  
- Extended **charting and visualization** (time-series, longitudinal data).  
- Optional **data encryption** for export files.  
- Improved **survey logic** (conditional questions).  

---

## 👨‍💼 Author

**Lucas Bodner**  
Bachelor Student – **HTW Saar**  
Intern – **DFKI Smart Services**  
📧 lucas.bodner@htwsaar.de  

---

## ⏳ Timeline

| Week | Task                                    | Status     |
|------|-----------------------------------------|------------|
| S1–S2 | Planning, literature review             | ✅ Done     |
| S3    | Initial Streamlit setup (multi-lang)    | ✅ Done     |
| S4    | Consent form integration                | ✅ Done     |
| S5    | Full survey implementation              | ✅ Done     |
| S6    | Local storage & export                  | ✅ Done     |
| S7    | Guidance dashboard + charts             | ✅ Done     |
| S8    | Testing & UI refinements                | ✅ Done     |
| S9–S10 | Documentation & screenshots            | ✅ Done     |
| S11–S12 | Thesis writing & final submission      | 🟡 Ongoing  |
