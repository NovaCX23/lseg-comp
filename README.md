# LSEG Diagram Generator

AI-powered web application that converts natural language descriptions into editable Mermaid.js diagrams. Inspired by Eraser.io and Azure AI Diagram Generator.

## Features

- **Natural Language Input**: Describe diagrams in English or Romanian
- **Typo Correction**: Automatically fixes typos and ambiguities
- **Live Preview**: See your diagram update in real-time
- **Editable Code**: Modify the Mermaid syntax directly
- **Conversation History**: Browse and restore previous diagrams
- **Technical Accuracy**: Ensures correct architectural patterns

## Tech Stack

- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **Diagram Rendering**: Mermaid.js + Monaco Editor
- **Backend**: FastAPI (Python)
- **AI**: Google Gemini 2.0 Flash
- **Database**: SQLite

## Project Structure

```
lseg-diagram/
├── backend/           # FastAPI backend
│   ├── agents/       # LLM agents (preprocessor, generator)
│   ├── api/          # API routes
│   ├── models/       # Pydantic schemas
│   └── main.py       # Application entry point
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── services/    # API client
│   │   └── App.tsx      # Main application
│   └── package.json
├── PLAN.md           # Project plan
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

## Usage

1. Enter a natural language description of your diagram in the input field
2. Click "Generate" to create the diagram
3. View the Mermaid code on the left and preview on the right
4. Edit the code directly to refine your diagram
5. Previous diagrams are saved in the history sidebar

### Example Prompts

- "3-tier architecture with React frontend, Node.js API, PostgreSQL database"
- "Microservices with API Gateway, Redis cache, and multiple databases"
- "AWS architecture with VPC, EC2, RDS, S3, CloudFront"
- "fe de react care vb cu un api pe node care salveaza intro bza de date postgre"

## API Endpoints

- `POST /api/generate` - Generate diagram from prompt
- `POST /api/history` - Get conversation history
- `GET /api/sessions` - List all sessions
- `GET /health` - Health check

## Team

- alex
- bianca
- victor
- chris
- edi
- XX_andrei_XX_YT_RO

## License

MIT
