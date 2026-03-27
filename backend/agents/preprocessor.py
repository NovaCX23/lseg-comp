import os
import google.genai as genai
from google.genai import types

PREPROCESSOR_PROMPT = """You are a technical text normalizer. Fix typos, clarify ambiguities, and reformulate the user's intent for diagram generation.

Rules:
1. Fix all typos and grammar errors
2. Resolve ambiguities in technical terms
3. Expand abbreviations to full names (e.g., "fe" → "frontend", "bza" → "database")
4. Maintain the original language (Romanian or English)
5. Output ONLY the corrected text, nothing else

Common expansions:
- "fe" → "frontend"
- "be" → "backend"
- "bza" / "bd" → "database"
- "vb" → "verb" / "comunică"
- "pt" → "pentru"
- "cu" → "cu"
- "api" → "API"
- "redis" → "Redis"
- "postgre" → "PostgreSQL"
- "react" → "React"
- "node" → "Node.js"
- "cas" → "cache"

Respond with ONLY the corrected text."""

GENERATOR_PROMPT = """You are an expert Software and Cloud Architect. Generate valid Mermaid.js diagram syntax for the described architecture.

CRITICAL RULES:
1. Output ONLY the Mermaid.js code block, no explanations, no markdown fences
2. Use correct diagram type based on content:
   - graph TD or graph LR for flowcharts/architecture
   - sequenceDiagram for API interactions
   - erDiagram for database schemas
   - gantt for timelines
3. For architecture diagrams, follow these conventions:
   - Databases are data stores, place them at the end of data flow
   - Load balancers sit in front of application servers
   - Firewalls protect internal networks
   - API Gateways are entry points
   - Caches (Redis) sit between application and database
4. Use clear, descriptive node labels
5. Use arrows (--> or -.->) for connections
6. Mermaid syntax examples:
   - graph TD: A[Label] --> B[Label]
   - sequenceDiagram: participant A\nA->>B: message

Start directly with the Mermaid syntax. Do not include ```mermaid tags."""

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

async def preprocess_prompt(user_input: str) -> str:
    """Preprocess user input to fix typos and clarify intent."""
    client = get_client()
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[PREPROCESSOR_PROMPT, user_input],
        config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=500)
    )
    return response.text.strip()

async def generate_mermaid(corrected_input: str) -> str:
    """Generate Mermaid.js syntax from corrected prompt."""
    client = get_client()
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[GENERATOR_PROMPT, corrected_input],
        config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=1000)
    )
    content = response.text.strip()
    if content.startswith("```mermaid"):
        content = content[9:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()
