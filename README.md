# LSEG_LMAO

AI-powered diagram generator that converts natural language descriptions into Mermaid.js diagrams.

## Tech Stack

- **UI**: Streamlit
- **LLM**: Ollama (qwen2.5-coder:7b)
- **Database**: SQLite
- **Rendering**: Mermaid.js

## Setup

```bash
pip install streamlit ollama
ollama pull qwen2.5-coder:7b
```

## Run

```bash
streamlit run main.py
```

Open http://localhost:8501 in your browser.

## Usage

1. Enter a diagram description in natural language (Romanian or English)
2. The AI generates a Mermaid.js diagram
3. Edit the code directly in the editor
4. Previous diagrams are saved in the sidebar

## Features

- Natural language input (EN/RO)
- Live preview with auto-styling
- Session history
- Download as .mmd file
- Multiple themes (dark/default/forest/neutral)