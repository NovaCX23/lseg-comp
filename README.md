# LLMO — AI Diagram Architect

> Describe an architecture in plain language. Get a live Mermaid.js diagram in seconds.

Built at the **LSEG Hackathon 2025** in ~3 hours. Polished afterwards.

---

## What it does

LLMO takes a natural language description (English or Romanian) and generates a production-style architecture diagram using Mermaid.js. The LLM runs locally via Ollama — no API keys, no cloud dependency, no data leaving your machine.

Describe a microservices setup, a data pipeline, or an authentication flow. LLMO fills in the standard components you'd normally forget to draw, adds semantic colour-coding, and drops the result in an editable live preview.

## Features

- **Local LLM** — runs on `qwen2.5-coder:7b` via Ollama; no internet required after setup
- **Live editor** — generated Mermaid code appears in an editable textarea; edit and preview instantly
- **Auto-styling** — semantic node detection applies colour classes (user, API, database, queue, cache)
- **Session history** — every diagram is saved to a local SQLite database; pick up where you left off
- **Multiple themes** — dark, default, forest, neutral
- **Flowchart direction** — TD, LR, RL, BT
- **Download** — export any diagram as a `.mmd` file
- **Full-screen preview** — dedicated full-screen view for large diagrams

## Architecture

```
User input (Streamlit chat)
        ↓
System prompt + history → Ollama (qwen2.5-coder:7b)
        ↓
Raw LLM response
        ↓
Extract + sanitize Mermaid code
        ↓
Apply semantic auto-styles (optional)
        ↓
Render via Mermaid.js (inline HTML component)
        ↓
Persist to SQLite (session history)
```

## Setup

**Prerequisites:**
- Python 3.9+
- [Ollama](https://ollama.com) installed and running

```bash
# 1. Clone the repo
git clone https://github.com/your-username/lseg-comp.git
cd lseg-comp

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Pull the model
ollama pull qwen2.5-coder:7b

# 4. Start Ollama (if not already running)
ollama serve
```

## Run

```bash
streamlit run main.py
```

Open http://localhost:8501 in your browser.

## Usage

1. Type an architecture description in the chat — English or Romanian, typos allowed
2. Wait a few seconds for the LLM to generate the diagram
3. The Mermaid code appears in the right-hand editor — edit it manually if needed
4. Click **Full Screen** for a larger view
5. Previous sessions are listed in the sidebar — click any to reload

**Example prompts:**
- `e-commerce platform with microservices, kafka, redis, postgres`
- `OAuth2 authentication flow with JWT`
- `CI/CD pipeline with GitHub Actions, Docker, and Kubernetes`
- `arhitectura pentru o aplicatie de ride-sharing`

## Screenshots

*(See [screenshots/](screenshots/))*

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI | Streamlit |
| LLM runtime | Ollama |
| Model | qwen2.5-coder:7b |
| Diagram rendering | Mermaid.js 10.6 |
| Persistence | SQLite |
| Language | Python 3.9+ |

## Built at LSEG Hackathon 2025

This project was built in ~3 hours at the LSEG Hackathon 2025. The goal: prove that a locally-running LLM could generate useful, stylized architecture diagrams from plain text with zero external API dependencies.
