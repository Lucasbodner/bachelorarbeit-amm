# 🧠 Bachelorarbeit – AMM Mobile App

This project is part of my Bachelor's thesis at **DFKI** and **HTW Saar**.  
It demonstrates a **privacy-preserving prototype** that integrates an **Artificial Mental Model (AMM)** for healthcare support, running fully **locally** with no internet connection.

---

## 📚 Table of Contents

- [Project Description](#-project-description)  
- [Project Structure](#-project-structure)  
- [About the AMM](#-about-the-amm)  
- [Privacy & Offline Functionality](#-privacy--offline-functionality)  
- [Installation & Usage](#-installation--usage)  
- [Model Parameters](#-model-parameters)  
- [Features](#-features)  
- [UI Pages](#-ui-pages)  
- [Current Status](#-current-status)  
- [Author](#-author)  
- [Timeline](#-timeline)  

---

## 📜 Project Description

The goal is to build a **local, lightweight prototype** of an AMM-powered app for healthcare professionals and patients.  
It uses **Streamlit** as a cross-platform interface (desktop & mobile web-friendly).  

Core objectives:
- Run **local inference** with a quantized `.gguf` model via `llama.cpp`.  
- Provide a **multi-page UI**: Overview, Health Profile, Patient Q/A, and Physio Dashboard.  
- Save **conversations locally** (JSONL format).  
- Ensure strict **privacy**: nothing leaves the device.  

---

## 📁 Project Structure

```
bachelorarbeit-amm/
├── app.py                   # Main Streamlit application (UI + llama.cpp integration)
├── requirements.txt         # Dependencies
├── README.md                # Project description & setup

├── model/                   # Quantized AMM model (.gguf)
│   └── Llama-3.2-1B-merged-lora-q4_k.gguf
├── bin/                     # llama-cli binary
│   └── llama-cli
├── utils/                   
│   └── storage.py           # Save/load/export conversations
├── data/                    
│   └── conversations.jsonl  # Conversation history (auto-created)
├── doc/                     # Notes, articles, diagrams, screenshots
├── assets/                  # Logos & images for UI
```

---

## 🧠 About the AMM

- **Artificial Mental Model (AMM):** a concept to capture patient expectations and support therapy decisions.  
- Based on **LLaMA in `.gguf` format**, executed with **llama.cpp** (`llama-cli`).  
- Fully **offline**, ensuring medical data privacy.  
- Provides **personalized, explainable answers** and **visual insights** into patient traits and progress.  

---

## 🔐 Privacy & Offline Functionality

- **All inference and storage happen locally**.  
- No API calls, no cloud servers, no data transmission.  
- History is stored in `data/conversations.jsonl`.  
- Future extension: add **optional encryption** for stored data.  

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

### 3. Place the model

Copy your quantized `.gguf` model into the `model/` folder:

```
model/Llama-3.2-1B-merged-lora-q4_k.gguf
```

### 4. Make sure the llama-cli binary is executable

```bash
chmod +x bin/llama-cli
```

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at [http://localhost:8501](http://localhost:8501).  
👉 Accessible via desktop browser and **mobile browser (same Wi-Fi/local network)**.

---

## 🔧 Model Parameters

Configurable in `app.py`:

```python
DEFAULT_MAX_TOKENS = "800"   # length of generation
DEFAULT_THREADS    = "6"     # number of CPU threads
DEFAULT_BATCH      = "1024"  # batch size
DEFAULT_NOWARMUP   = True    # skip warmup for faster start
```

Example command run internally:

```bash
llama-cli -m model/Llama-3.2-1B-merged-lora-q4_k.gguf   -p "How can AI support physiotherapy?"   -n 800 -t 6 -b 1024 --no-warmup
```

---

## ✨ Features

- **Local inference** via `llama.cpp` with `.gguf` models.  
- **Multi-page UI** (Overview, Health Profile, Patient Q/A, Physio Corner).  
- **Mobile-friendly design** (responsive Streamlit layout).  
- **Conversation history** saved locally (JSONL).  
- **Export & clear** conversation history.  
- **Charts & insights** (Altair/Streamlit).  
- **Robust error handling**:  
  - Missing model/binary → clear error message.  
  - Empty input → warning.  
  - Runtime logs viewable in debug expander.  

---

## 📱 UI Pages

1. **Overview** – Project context, AMM concept, privacy approach.  
2. **My Health Profile** – Patient demographics, health status, Big Five traits, exercise difficulty.  
3. **Patient Corner** – Q/A with the AMM, local chat history, export/clear options.  
4. **Physio Corner** – Patient profile summary, difficulty scores (chart), personality traits vs. norms (chart).  

---

## ✅ Current Status

- ✅ Local prototype fully functional.  
- ✅ Responsive UI tested on desktop and mobile browsers.  
- ✅ Conversation history with export/clear.  
- ✅ Charts (Altair with fallback).  
- 🟡 Documentation & screenshots in progress.  
- 🔒 Encryption planned as future work.  

---

## 👨‍💼 Author

**Lucas Bodner**  
Bachelor student at **HTW Saar** / Intern at **DFKI**  
📧 lucas.bodner@htwsaar.de  

---

## ⏳ Timeline

| Week | Task                                    | Status     |
|------|-----------------------------------------|------------|
| S1–S2 | Planning, literature review             | ✅ Done     |
| S3    | Project setup, base UI (FedWell)        | ✅ Done     |
| S4    | Model integration (llama.cpp)           | ✅ Done     |
| S5    | UI improvements & cleanup               | ✅ Done     |
| S6    | Local storage, export/clear functions   | ✅ Done     |
| S7    | Full testing, demo preparation          | ✅ Done     |
| S8    | Documentation, screenshots              | ✅ Done     |
| S9–S12 | Thesis writing & finalization          | 🟡 Ongoing  |
