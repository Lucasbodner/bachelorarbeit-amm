# 🧠 Bachelorarbeit – AMM Mobile App

This project is part of my Bachelor's thesis at **DFKI** and **HTW Saar**.  
It aims to develop a privacy-preserving mobile/web application that integrates an **🧠Artificial Mental Model (AMM)** to support healthcare professionals with local inference and offline functionality.

---

## 📚 Table of Contents

- [Project Description](#-project-description)
- [Project Structure](#-project-structure)
- [About the AMM](#-about-the-amm)
- [Privacy & Offline Functionality](#-privacy--offline-functionality)
- [Installation & Usage](#-installation--usage)
- [Current Status](#-current-status)
- [Author](#-author)
- [Timeline](#-timeline)

---

## 📜 Project Description

The goal is to create a local, lightweight mobile/web application that runs a quantized Artificial Mental Model directly on a user device (e.g. smartphone or tablet).  
The interface is built with **Streamlit** (as a web prototype) and will later be adapted to better fit mobile platforms.

---

## 📁 Project Structure

```
bachelorarbeit-amm/
├── app.py                   # Main Streamlit application
├── requirements.txt         # Dependencies
├── README.md                # Project description

├── model/                   # Quantized AMM model (.gguf)
│   └── Llama-3.2-1B-merged-lora-q4_k.gguf
├── bin/                     # llama-cli binary
│   └── llama-cli
├── utils/                   # Helper functions (e.g., inference logic)
├── data/                    # Saved conversations
│   └── conversations.txt
├── doc/                     # Notes, articles, diagrams, screenshots
```

---

## 🧠 About the AMM

This application uses a quantized **Artificial Mental Model (AMM)** based on a local large language model (LLM), stored as a `.gguf` file.  
The goal is to assist medical professionals with decision-making, especially in remote or privacy-sensitive scenarios.

- The model runs fully **offline**
- Built on **llama-cpp** and executed via a local `llama-cli` binary
- The interface allows users to input questions and receive generated responses
- Designed with a focus on healthcare-related use cases

---

## 🔐 Privacy & Offline Functionality

- All inference and data storage happens **locally** on the device
- No internet access is required
- All conversations are saved in `data/conversations.txt`
- Optional: Patient data will later be **encrypted** (e.g., via Fernet)

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

### 3. Make sure the llama-cli binary is available

The binary should be located in `bin/llama-cli` and be executable. If not, compile it or download from a release source.

### 4. Start the prototype

```bash
streamlit run app.py
```

The app will launch at `http://localhost:8501`.  
You can type in a question and get a response from the local `.gguf` model.

---

## ✅ Current Status

- ✅ Initial setup complete
- ✅ Streamlit prototype working locally with `.gguf` model
- ✅ Responses saved in `data/conversations.txt`
- 🛠️ Model fine-tuning & UI improvements in progress
- 🔒 Local encryption planned for August

---

## 👨‍💼 Author

**Lucas Bodner**  
Bachelor student at **HTW Saar** / Intern at **DFKI**  
📧 lucas.bodner@htwsaar.de

---

## ⏳ Timeline

| Week | Task                                    | Status     |
|------|-----------------------------------------|------------|
| W1–W2 | Model selection & integration           | ✅ Done     |
| W3   | Working local prototype (CLI + UI)      | ✅ Done     |
| W4   | Response filtering + data storage       | ✅ Done     |
| W5   | UI polish, README, folder cleanup       | 🟡 In Progress |
| W6+  | Add encryption, refine design, testing  | 🖒 Planned  |

