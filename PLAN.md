# LSEG Diagram Generator - Project Plan

## Overview
Build an AI-powered web application that converts natural language descriptions into editable Mermaid.js diagrams. Inspired by Eraser.io and Azure AI Diagram Generator.

## Tech Stack
- **Frontend**: React + Vite + TypeScript
- **Diagram Rendering**: Mermaid.js + React Flow (for editability)
- **AI/LLM**: OpenAI GPT-4o / Anthropic Claude / Gemini
- **Backend**: FastAPI (Python) or Next.js API routes
- **Database**: SQLite (hackathon) / Supabase (production)
- **Styling**: Tailwind CSS

## Core Features

### Phase 1: MVP (Core Functionality)
1. **Natural Language Input**
   - Chat interface for entering diagram descriptions
   - Support for Romanian and English
   - Typo/grammar correction preprocessing

2. **LLM Integration**
   - Multi-agent pipeline:
     - **Preprocessing Agent**: Fix typos, clarify ambiguities
     - **Generation Agent**: Produce Mermaid.js syntax
   - Strict system prompts for technical accuracy

3. **Diagram Rendering**
   - Mermaid.js for rendering
   - Split-pane view: text editor + visual preview
   - Real-time sync between code and preview

4. **Editability**
   - Edit Mermaid code directly
   - Manual node/edge manipulation (React Flow integration)
   - Bidirectional sync: code ↔ visual

5. **Conversation History**
   - Store previous diagram generations
   - Navigate between versions
   - Continue editing from history

### Phase 2: Enhancement (Bonus Points)
1. **Voice Input** - Speech-to-text API
2. **Export** - PNG/PDF/SVG download
3. **Code Generation** - Terraform/CloudFormation from diagrams
4. **Multiple Diagram Types** - Flowcharts, sequence, ER, Gantt

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│     LLM     │
│  Frontend   │◀────│   Backend   │◀────│   (GPT-4)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │                   ▼
       │            ┌─────────────┐
       │            │   SQLite    │
       │            │  Database   │
       │            └─────────────┘
       ▼
┌─────────────────┐
│   Mermaid.js    │
│   + React Flow  │
└─────────────────┘
```

## Multi-Agent Pipeline

```
User Input (Natural Language)
         │
         ▼
┌─────────────────────────┐
│  Preprocessing Agent    │
│  - Fix typos            │
│  - Resolve ambiguities  │
│  - Clarify intent       │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Generation Agent      │
│  - Select diagram type  │
│  - Generate Mermaid     │
│  - Ensure accuracy      │
└─────────────────────────┘
         │
         ▼
    Mermaid Code
```

## Project Structure

```
lseg-diagram/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInput.tsx
│   │   │   ├── DiagramEditor.tsx
│   │   │   ├── DiagramPreview.tsx
│   │   │   ├── HistorySidebar.tsx
│   │   │   └── Toolbar.tsx
│   │   ├── hooks/
│   │   │   ├── useDiagram.ts
│   │   │   └── useHistory.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── preprocessor.py
│   │   └── generator.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── models/
│   │   └── schema.py
│   ├── main.py
│   └── requirements.txt
│
├── PLAN.md
└── README.md
```

## Implementation Steps

### Step 1: Project Setup (Day 1)
- [ ] Initialize React + Vite frontend
- [ ] Set up FastAPI backend
- [ ] Configure Tailwind CSS
- [ ] Create basic project structure

### Step 2: Backend - LLM Integration (Day 1-2)
- [ ] Set up OpenAI/Anthropic API client
- [ ] Implement Preprocessing Agent prompt
- [ ] Implement Generation Agent prompt
- [ ] Create API endpoints
- [ ] Test with sample inputs

### Step 3: Frontend - Basic UI (Day 2)
- [ ] Build chat input component
- [ ] Create Mermaid preview component
- [ ] Add code editor (Monaco/CodeMirror)
- [ ] Implement split-pane layout

### Step 4: Editability (Day 2-3)
- [ ] Integrate React Flow
- [ ] Parse Mermaid → React Flow nodes/edges
- [ ] Sync React Flow → Mermaid code
- [ ] Handle node drag/drop/resize

### Step 5: History & Database (Day 3)
- [ ] Set up SQLite database
- [ ] Create conversation history table
- [ ] Build history sidebar UI
- [ ] Implement version navigation

### Step 6: Polish & Bonus (Day 3-4)
- [ ] Error handling & loading states
- [ ] Voice input (if time permits)
- [ ] Export functionality
- [ ] UI/UX improvements

## Critical Success Factors

### 1. Technical Accuracy
System prompt must enforce:
- Databases not behind load balancers
- Firewalls protect internal networks
- Correct AWS/Azure/GCP service placement
- Standard architectural patterns

### 2. Handling Imperfect Input
- Typos: "fe de react" → React Frontend
- Ambiguities: Auto-detect and ask clarifying questions
- Grammar: Fix automatically, don't fail

### 3. User Experience
- Instant preview (< 3 seconds to first render)
- Clear error messages
- Intuitive editing controls
- Responsive design

## Sample System Prompts

### Preprocessing Agent
```
You are a technical text normalizer. Fix typos, clarify ambiguities, and 
reformulate the user's intent for diagram generation. Maintain both 
Romanian and English. Output ONLY the corrected text.
```

### Generation Agent
```
You are an expert Software and Cloud Architect. Generate valid Mermaid.js 
syntax for the described diagram. Follow these rules:
1. Databases are data stores, place them appropriately
2. Load balancers sit in front of application servers
3. Firewalls protect internal networks
4. Use standard AWS/Azure/GCP icons when possible
5. Output ONLY Mermaid syntax, no explanations
```

## Testing Strategy

### Required Test Cases (Official Prompts)
1. Simple: "3-tier architecture with React, Node.js, PostgreSQL"
2. Complex: "Microservices with API Gateway, Redis cache, multiple databases"
3. Cloud: "AWS architecture with VPC, EC2, RDS, S3, CloudFront"
4. Edge cases: Typos, missing components, contradictory specs

### QA Checklist
- [ ] What happens with completely wrong input?
- [ ] What if user asks to edit only one element?
- [ ] Does history work correctly?
- [ ] Is the diagram technically accurate?

## Deliverables

1. **GitHub Repository** with:
   - Complete source code
   - README with setup instructions
   - Demo screenshots/videos

2. **Working Application** featuring:
   - Natural language → Mermaid diagram
   - Editable diagrams
   - Conversation history
   - Support for Romanian/English

3. **Demo Video** showing:
   - Full workflow
   - Edit capabilities
   - Edge case handling
   - Bonus features (if implemented)

## Team Assignments

| Role | Person | Tasks |
|------|--------|-------|
| Frontend Dev 1 | - | Diagram engine, React Flow, editability |
| Frontend Dev 2 | - | Chat UI, history sidebar, styling |
| AI/Architecture | - | Multi-agent pipeline, prompts, accuracy |
| Prompt Engineer | - | System prompts, test cases, iteration |
| Backend | - | API, database, LLM integration |
| Product/QA | - | Demo, testing, submission |

## Timeline

| Day | Milestone |
|-----|-----------|
| 1 | Project setup, basic LLM integration, simple diagram generation |
| 2 | Full editing capabilities, history, polish |
| 3 | Testing, bug fixes, bonus features |
| 4 | Final polish, demo recording, submission |

## API Endpoints

```
POST /api/generate
  Body: { prompt: string, history?: Message[] }
  Response: { mermaid: string, corrected_prompt: string }

POST /api/history
  Body: { session_id: string }
  Response: { messages: Message[] }

POST /api/export
  Body: { mermaid: string, format: "png" | "svg" | "pdf" }
  Response: { file: base64 }
```

## Database Schema

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  session_id TEXT,
  role TEXT,  -- "user" or "assistant"
  content TEXT,
  mermaid_code TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

*Plan created for LSEG Hackathon - 2026*
