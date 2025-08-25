# 🧠 Bachelorarbeit – AMM Mobile App

This project is part of my Bachelor's thesis at **DFKI** and **HTW Saar**.  
It aims to develop a privacy-preserving mobile/web application that integrates an **🧠 Artificial Mental Model (AMM)** to support healthcare professionals with **local inference** and **offline functionality**.

---

## 📚 Table of Contents

- [Project Description](#-project-description)  
- [Project Structure](#-project-structure)  
- [About the AMM](#-about-the-amm)  
- [Privacy & Offline Functionality](#-privacy--offline-functionality)  
- [Installation & Usage](#-installation--usage)  
- [Model Parameters](#-model-parameters)  
- [Features](#-features)  
- [Current Status](#-current-status)  
- [Author](#-author)  
- [Timeline](#-timeline)  

---

## 📜 Project Description

The goal is to create a **local, lightweight prototype** that runs a quantized Artificial Mental Model directly on a user device (e.g., laptop, smartphone, tablet).  
The interface is built with **Streamlit** (as a web prototype) and will later be adapted to better fit mobile platforms.  

Main objectives:
- Demonstrate **local inference** with a `.gguf` model (Llama).  
- Provide a **simple UI** for asking questions and saving responses.  
- Ensure **privacy-preserving** execution (everything stays on device).  
- Prepare the ground for **healthcare-related use cases**.  

---

## 📁 Project Structure

```
bachelorarbeit-amm/
├── app.py                   # Main Streamlit application
├── requirements.txt         # Dependencies
├── README.md                # Project description & setup

├── model/                   # Quantized AMM model (.gguf)
│   └── Llama-3.2-1B-merged-lora-q4_k.gguf
├── bin/                     # llama-cli binary
│   └── llama-cli
├── utils/                   
│   └── storage.py           # Save/load/export conversations
├── data/                    
│   └── conversations.jsonl  # Conversation history
├── doc/                     # Notes, articles, diagrams, screenshots
```

---

## 🧠 About the AMM

This application integrates a quantized **Artificial Mental Model (AMM)** based on a local LLaMA model in `.gguf` format.  

- Fully **offline** execution (no internet required).  
- Based on **llama.cpp** via the local `llama-cli` binary.  
- UI for asking questions and viewing responses.  
- Conversation history stored locally (`JSONL` format).  

The AMM is designed as a proof-of-concept to **assist healthcare professionals** with decision support in **remote or privacy-sensitive environments**.  

---

## 🔐 Privacy & Offline Functionality

- All inference and storage happens **locally**.  
- No data is sent over the internet.  
- Conversations are stored in `data/conversations.jsonl`.  
- Future extension: **encryption** of saved data.  

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

Put your quantized `.gguf` model inside the `model/` folder, e.g.:

```
model/Llama-3.2-1B-merged-lora-q4_k.gguf
```

### 4. Make sure the llama-cli binary is executable

Check that `bin/llama-cli` exists and is executable:

```bash
chmod +x bin/llama-cli
```

### 5. Run the prototype

```bash
streamlit run app.py
```

The app will launch at `http://localhost:8501`.

---

## 🔧 Model Parameters

In `app.py`, generation is controlled with:

```bash
-n   # max tokens (e.g. 800–1200 for concise answers)
-t   # threads (6–8 recommended on CPU)
-b   # batch size (512–2048 depending on hardware)
--no-warmup   # skip warmup for faster start
```

👉 Example:

```python
cmd = [
    BIN_PATH, "-m", MODEL_PATH,
    "-p", prompt,
    "-n", "800",
    "-t", "6",
    "-b", "1024",
    "--no-warmup"
]
```

---

## ✨ Features

- **Local inference** with `.gguf` model via `llama-cli`.  
- **Simple UI** to ask questions and get responses.  
- **Response history** with timestamp, latency, question & answer.  
- **Export to JSONL** → download all conversations.  
- **Clear history** → reset conversations.  
- **Error handling**:  
  - Missing model → clear error message.  
  - Missing binary → instructions shown.  
  - Empty question → warning instead of crash.  

---

## ✅ Current Status

- ✅ Local prototype running with `.gguf` model.  
- ✅ UI with Streamlit.  
- ✅ History stored & exportable (JSONL).  
- ✅ Error handling implemented.  
- ✅ Functional tests passed (S7).  
- 🛠️ Documentation + screenshots in progress (S8).  
- 🔒 Encryption planned for later.  

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
| S3    | Project setup, UI base                  | ✅ Done     |
| S4    | Model integration, inference tests      | ✅ Done     |
| S5    | UI adjustments, repo cleanup            | ✅ Done     |
| S6    | Storage system, error cases             | ✅ Done     |
| S7    | Full testing, optimizations, demo       | ✅ Done     |
| S8    | Screenshots, documentation, bug fixes   | 🟡 Ongoing |
| S9–S12 | Thesis writing & finalization          | ⏳ Planned |
