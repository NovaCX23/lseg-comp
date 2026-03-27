# Diagram Generator Specification

## Project Overview
- **Name**: Diagram Generator
- **Type**: Web Application
- **Core Functionality**: AI-powered diagram generator that converts natural language queries (with typos support) into interactive, draggable node-based diagrams
- **Target Users**: Developers, designers, anyone needing quick diagram generation

## Technical Stack
- **Backend**: Python with Flask
- **AI**: Ollama with qwen2.5-coder:7b local model
- **Database**: SQLite for conversation history
- **Frontend**: Vanilla HTML/CSS/JavaScript with interactive canvas

## UI/UX Specification

### Layout Structure
- **Header**: App title and clear history button
- **Main Area**: Split into two panels
  - Left panel (30%): Query input and conversation history
  - Right panel (70%): Diagram canvas
- **Responsive**: Single column on mobile (<768px)

### Visual Design
- **Color Palette**:
  - Background: #0d1117 (dark)
  - Surface: #161b22
  - Primary: #58a6ff (blue accent)
  - Secondary: #8b949e
  - Success: #3fb950
  - Error: #f85149
  - Text: #c9d1d9
  - Node colors: #ff6b6b, #4ecdc4, #ffe66d, #95e1d3, #dda0dd, #87ceeb, #f0e68c
- **Typography**:
  - Font: "JetBrains Mono", monospace
  - Headings: 24px bold
  - Body: 14px
- **Spacing**: 16px base unit

### Components
- **Query Input**: Textarea with send button, placeholder "Describe your diagram..."
- **History List**: Scrollable list of past queries, clickable to regenerate
- **Diagram Canvas**: 
  - SVG-based with draggable nodes
  - Pan/zoom support
  - Connection lines between nodes
- **Node**: Rounded rectangle with colored fill, label, drag handles

## Functionality Specification

### Core Features
1. **Query Processing**
   - Accept natural language input (tolerant of typos)
   - Send to Ollama for diagram generation
   - Parse JSON response into node/link structure

2. **Diagram Generation**
   - LLM generates JSON describing nodes and connections
   - Each node has: id, label, color, x, y
   - Each connection has: from, to, label (optional)

3. **Interactive Diagram**
   - Drag nodes to reposition
   - Connections follow nodes
   - Nodes have different colors
   - Double-click node to edit label

4. **Conversation History**
   - Store in SQLite: id, query, response_json, timestamp
   - Display recent 20 conversations
   - Click to reload any past diagram

5. **Clear History**
   - Button to clear all history
   - Confirmation before clearing

### Data Flow
1. User enters query → Flask API
2. API calls Ollama with prompt
3. Ollama returns JSON diagram spec
4. API stores in SQLite, returns to frontend
5. Frontend renders interactive diagram

### Edge Cases
- Invalid query: Show error message
- Ollama not running: Show connection error
- Empty response: Show "Could not generate diagram"
- Invalid JSON from model: Attempt to parse, fallback to error

## Acceptance Criteria
- [ ] Query input accepts text and sends to backend
- [ ] Ollama generates valid diagram JSON
- [ ] Nodes are rendered and draggable
- [ ] Connections render between nodes
- [ ] History persists across sessions (SQLite)
- [ ] History items are clickable to reload
- [ ] Clear history works with confirmation
- [ ] Error states handled gracefully
