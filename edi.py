import streamlit as st
import streamlit.components.v1 as components
import ollama
import re
import html
import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path
import uuid

MODEL_NAME = "qwen2.5-coder:7b"
DB_PATH = Path(__file__).parent / "diagram_history.db"

st.set_page_config(
    page_title="Arhitect Diagrame AI Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                mermaid_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """
        )
        db.commit()


def create_session() -> str:
    session_id = str(uuid.uuid4())[:8]
    with get_db() as db:
        db.execute(
            "INSERT INTO sessions (id, title) VALUES (?, ?)",
            (session_id, f"Diagram {datetime.now().strftime('%H:%M')}"),
        )
    return session_id


def get_all_sessions():
    with get_db() as db:
        rows = db.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]


def get_session_messages(session_id: str):
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def save_message(
    session_id: str, role: str, content: str, mermaid_code: Optional[str] = None
):
    with get_db() as db:
        db.execute(
            "INSERT INTO messages (session_id, role, content, mermaid_code) VALUES (?, ?, ?, ?)",
            (session_id, role, content, mermaid_code),
        )
        db.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )
        db.commit()


def update_session_title(session_id: str, title: str):
    with get_db() as db:
        db.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
        db.commit()


def delete_session(session_id: str):
    with get_db() as db:
        db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        db.commit()


init_db()

st.markdown(
    """
    <style>
        .block-container { padding-top: 1rem; }
        .stTextArea textarea { font-family: "JetBrains Mono", "Fira Code", monospace !important; font-size: 13px !important; }
        [data-testid="stChatMessage"] { border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; }
        .history-item { padding: 8px 12px; margin: 4px 0; border-radius: 8px; cursor: pointer; transition: background 0.2s; }
        .history-item:hover { background: rgba(255,255,255,0.1); }
        .history-item.active { background: rgba(59,130,246,0.3); border-left: 3px solid #3b82f6; }
        .session-title { font-weight: 600; font-size: 14px; }
        .session-time { font-size: 11px; color: #888; }
        .delete-btn { color: #ef4444; cursor: pointer; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title(f"📊 Arhitect Diagrame AI Pro")
st.caption("Generează diagrame Mermaid cu AI • Istoric salvat automat")

if "current_session_id" not in st.session_state:
    sessions = get_all_sessions()
    if sessions:
        st.session_state.current_session_id = sessions[0]["id"]
    else:
        st.session_state.current_session_id = create_session()

if "messages" not in st.session_state:
    st.session_state.messages = []


def load_session(session_id: str):
    st.session_state.current_session_id = session_id
    msgs = get_session_messages(session_id)
    st.session_state.messages = [
        {"role": m["role"], "content": m["content"], "mermaid": m["mermaid_code"]}
        for m in msgs
        if m["role"] != "system"
    ]
    st.rerun()


with st.sidebar:
    st.header("📜 Istoric")

    if st.button("➕ Diagramă Nouă", use_container_width=True):
        new_id = create_session()
        st.session_state.current_session_id = new_id
        st.session_state.messages = []
        st.rerun()

    st.divider()

    sessions = get_all_sessions()
    for sess in sessions:
        is_active = sess["id"] == st.session_state.current_session_id
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"**{sess['title']}**\n_{sess['updated_at']}_",
                key=f"sess_{sess['id']}",
                use_container_width=True,
            ):
                load_session(sess["id"])
        with col2:
            if st.button("🗑️", key=f"del_{sess['id']}"):
                delete_session(sess["id"])
                if st.session_state.current_session_id == sess["id"]:
                    sessions = get_all_sessions()
                    if sessions:
                        st.session_state.current_session_id = sessions[0]["id"]
                    else:
                        st.session_state.current_session_id = create_session()
                    st.session_state.messages = []
                st.rerun()

    st.divider()
    st.header("⚙️ Setări")
    mermaid_theme = st.selectbox(
        "Temă", ["dark", "default", "forest", "neutral"], index=0
    )
    direction = st.selectbox("Direcție", ["TD", "LR", "RL", "BT"], index=0)
    auto_style = st.toggle("Auto-style semantic", value=True)

    st.subheader("🎨 Culori noduri")
    color_user = st.color_picker("User/Client", "#fef3c7")
    color_api = st.color_picker("API/Service", "#dcfce7")
    color_db = st.color_picker("Database", "#dbeafe")
    color_queue = st.color_picker("Queue", "#ede9fe")
    color_cache = st.color_picker("Cache", "#ccfbf1")
    color_auth = st.color_picker("Auth", "#e0e7ff")
    color_danger = st.color_picker("Error/Danger", "#fee2e2")
    color_ext = st.color_picker("External", "#f3f4f6")

    node_colors = {
        "user": color_user,
        "api": color_api,
        "db": color_db,
        "queue": color_queue,
        "cache": color_cache,
        "auth": color_auth,
        "danger": color_danger,
        "ext": color_ext,
    }


def sanitize_mermaid(code: str) -> str:
    if not code:
        return ""

    lines = code.split("\n")
    cleaned = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("class ") and not stripped.startswith("classDef "):
            parts = stripped.split()
            if len(parts) >= 3:
                ids_part = " ".join(parts[1:-1]).replace(", ", ",")
                cleaned.append(f"class {ids_part} {parts[-1]}")
                continue

        if stripped.startswith("subgraph "):
            name = stripped[len("subgraph ") :].strip()
            name = name.replace('"', "").replace("'", "").replace(" ", "_")
            cleaned.append(f"subgraph {name}")
            continue

        cleaned.append(line)

    return "\n".join(cleaned).strip()


def extract_mermaid_code(text: str):
    match = re.search(r"```mermaid\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return sanitize_mermaid(match.group(1))
    return None


def fix_mermaid_text_errors(code: str) -> str:
    """Fix common mermaid syntax errors that cause 'Syntax error in text'"""
    if not code:
        return code

    lines = code.split("\n")
    fixed = []

    for line in lines:
        stripped = line.strip()

        match = re.match(r"^([A-Za-z0-9_]+)\[(.*?)\](.*)$", stripped)
        if match:
            node_id, label, rest = match.groups()
            label = label.strip()
            if label:
                label = label.strip("\"'")
                label = label.replace("\\", "").replace('"', '"').replace("\\'", "'")
                label = label.replace("\n", " ").replace("  ", " ").strip()
                line = f'{node_id}["{label}"]{rest}'

        fixed.append(line)

    return "\n".join(fixed)


def apply_semantic_styles(code: str, flow_direction="TD", node_colors=None):
    if not code:
        return code

    if node_colors is None:
        node_colors = {
            "user": "#fef3c7",
            "api": "#dcfce7",
            "db": "#dbeafe",
            "queue": "#ede9fe",
            "cache": "#ccfbf1",
            "auth": "#e0e7ff",
            "danger": "#fee2e2",
            "ext": "#f3f4f6",
        }

    code = re.sub(
        r"^\s*(graph|flowchart)\s+\w+\s*$",
        f"flowchart {flow_direction}",
        code,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    code = fix_mermaid_text_errors(code)

    init_block = f"""%%{{init: {{"theme":"{mermaid_theme}","securityLevel":"loose","flowchart":{{"htmlLabels":true,"curve":"basis"}}}} }}%%"""

    stroke_colors = {
        "user": "#f59e0b",
        "api": "#22c55e",
        "db": "#3b82f6",
        "queue": "#8b5cf6",
        "cache": "#14b8a6",
        "auth": "#6366f1",
        "danger": "#ef4444",
        "ext": "#6b7280",
    }
    text_colors = {
        "user": "#111827",
        "api": "#052e16",
        "db": "#0b3b7a",
        "queue": "#3b0764",
        "cache": "#134e4a",
        "auth": "#312e81",
        "danger": "#7f1d1d",
        "ext": "#111827",
    }

    class_defs_lines = []
    for cls, fill in node_colors.items():
        stroke = stroke_colors.get(cls, "#6b7280")
        text = text_colors.get(cls, "#111827")
        width = "2px" if cls == "danger" else "1.5px"
        dash = ",stroke-dasharray: 5 3" if cls == "ext" else ""
        class_defs_lines.append(
            f"classDef {cls} fill:{fill},stroke:{stroke},color:{text},stroke-width:{width}{dash};"
        )
    class_defs = "\n".join(class_defs_lines)

    node_ids = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[\[\(\{]", code))

    def pick_class(nid: str):
        x = nid.lower()
        if any(
            k in x for k in ["user", "client", "customer", "driver", "rider", "admin"]
        ):
            return "user"
        if any(k in x for k in ["api", "backend", "service", "server", "gateway"]):
            return "api"
        if any(
            k in x
            for k in ["db", "database", "postgres", "mysql", "mongo", "redisstore"]
        ):
            return "db"
        if any(k in x for k in ["queue", "kafka", "rabbit", "sqs", "stream"]):
            return "queue"
        if any(k in x for k in ["cache", "redis", "memcached"]):
            return "cache"
        if any(k in x for k in ["auth", "oauth", "jwt", "identity"]):
            return "auth"
        if any(k in x for k in ["error", "fail", "exception", "deadletter", "dlq"]):
            return "danger"
        if any(k in x for k in ["external", "thirdparty", "stripe", "twilio", "maps"]):
            return "ext"
        return None

    class_lines = []
    for nid in sorted(node_ids):
        cls = pick_class(nid)
        if cls:
            class_lines.append(f"class {nid} {cls};")

    out = code.strip()

    if "%%{init:" not in out:
        out = init_block + "\n" + out

    if re.search(r"^\s*(graph|flowchart)\b", out, flags=re.IGNORECASE | re.MULTILINE):
        if "classDef " not in out:
            out += "\n\n" + class_defs.strip() + "\n"
        if class_lines:
            out += "\n" + "\n".join(class_lines) + "\n"

    return sanitize_mermaid(out)


def render_mermaid(mermaid_code):
    safe_code = mermaid_code

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
        <style>
            body {{ margin: 0; padding: 14px; background: linear-gradient(180deg, #0b1220 0%, #111827 100%); font-family: Inter, sans-serif; }}
            .card {{ background: #0f172a; border: 1px solid #334155; border-radius: 14px; padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,.3); overflow: auto; height: 560px; }}
            .mermaid {{ display: flex; justify-content: center; align-items: flex-start; min-height: 520px; }}
            svg {{ max-width: 100%; height: auto; }}
            .node {{ cursor: grab; user-select: none; }}
            .node:hover rect, .node:hover circle {{ filter: brightness(1.15); }}
        </style>
    </head>
    <body>
        <div class="card" id="diagram-container">
            <div class="mermaid">{safe_code}</div>
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: false,
                theme: "{mermaid_theme}",
                securityLevel: "loose",
                flowchart: {{ htmlLabels: true, curve: "basis", useMaxWidth: true }}
            }});

            async function render() {{
                try {{
                    await mermaid.run({{ querySelector: '.mermaid' }});
                    initDrag();
                }} catch (e) {{
                    console.error('Mermaid error:', e);
                }}
            }}

            function initDrag() {{
                const svg = document.querySelector('#diagram-container svg');
                if (!svg) return;
                
                let dragging = null;
                let startX = 0, startY = 0;
                let origX = 0, origY = 0;

                svg.querySelectorAll('.node').forEach(node => {{
                    node.style.cursor = 'grab';
                    node.addEventListener('mousedown', (e) => {{
                        if (e.button !== 0) return;
                        e.preventDefault();
                        
                        dragging = node;
                        const transform = node.getAttribute('transform') || '';
                        const match = transform.match(/translate\\(([^,]+),\\s*([^)]+)\\)/);
                        origX = match ? parseFloat(match[1]) : 0;
                        origY = match ? parseFloat(match[2]) : 0;
                        startX = e.clientX;
                        startY = e.clientY;
                        node.style.cursor = 'grabbing';
                    }});
                }});

                document.addEventListener('mousemove', (e) => {{
                    if (!dragging) return;
                    
                    const dx = e.clientX - startX;
                    const dy = e.clientY - startY;
                    
                    dragging.setAttribute('transform', `translate(${{origX + dx}},${{origY + dy}})`);
                }});

                document.addEventListener('mouseup', () => {{
                    if (dragging) {{
                        dragging.style.cursor = 'grab';
                        dragging = null;
                    }}
                }});
            }}

            render();
        </script>
    </body>
    </html>"""
    components.html(html_code, height=600, scrolling=True)


SYSTEM_PROMPT = """
You are a senior Diagram Architect specialized in Mermaid.
User language can be Romanian/English. Generate clean Mermaid flowchart diagrams.

RULES:
- Return ONLY one fenced block: ```mermaid ... ```
- No extra text outside the code block
- Use flowchart with TD/LR direction
- Node IDs must be single words (no spaces, use underscore)
- Node labels in quotes: A["Label Text"]
- Keep syntax clean and valid
- Do NOT use emojis in node labels - use text only
- Use subgraphs for grouping: subgraph backend [...]

Example:
```mermaid
flowchart TD
    A["User"] --> B["API Gateway"]
    subgraph backend
        B --> C["Auth Service"]
        B --> D["Order Service"]
    end
```
"""

if "current_mermaid_code" not in st.session_state:
    st.session_state.current_mermaid_code = ""

col_chat, col_editor = st.columns([1, 1], gap="large")

with col_chat:
    st.subheader("💬 Chat AI")
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.markdown(msg["content"])
                else:
                    st.markdown(msg["content"])
                    if msg.get("mermaid"):
                        with st.expander("📊 Vezi codul Mermaid"):
                            st.code(msg["mermaid"], language="mermaid")

    user_prompt = st.chat_input("Ex: arhitectură e-commerce cu microservicii")
    if user_prompt:
        save_message(st.session_state.current_session_id, "user", user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with col_chat:
        with st.chat_message("assistant"):
            with st.spinner("Generez diagramă..."):
                try:
                    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                    for msg in st.session_state.messages:
                        messages_for_api.append(
                            {"role": msg["role"], "content": msg["content"]}
                        )

                    response = ollama.chat(model=MODEL_NAME, messages=messages_for_api)
                    reply = response["message"]["content"]

                    code = extract_mermaid_code(reply)
                    if code:
                        if auto_style:
                            code = apply_semantic_styles(
                                code, flow_direction=direction, node_colors=node_colors
                            )
                        st.session_state.current_mermaid_code = code

                        first_words = (user_prompt or "")[:40].replace(" ", "_")
                        update_session_title(
                            st.session_state.current_session_id, first_words
                        )

                    save_message(
                        st.session_state.current_session_id,
                        "assistant",
                        reply,
                        code or "",
                    )
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply, "mermaid": code}
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Eroare Ollama: {e}")

with col_editor:
    st.subheader("✏️ Editor & Preview")

    if st.session_state.current_mermaid_code:
        edited_code = st.text_area(
            "Cod Mermaid:", value=st.session_state.current_mermaid_code, height=200
        )
        st.session_state.current_mermaid_code = edited_code

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "📄 Download",
                data=edited_code.encode("utf-8"),
                file_name="diagram.mmd",
                mime="text/plain",
            )
        with c2:
            if st.button("🎨 Re-stilizează"):
                st.session_state.current_mermaid_code = apply_semantic_styles(
                    edited_code, flow_direction=direction, node_colors=node_colors
                )
                st.rerun()
        with c3:
            if st.button("🔄 Randează din nou"):
                st.rerun()

        st.markdown("### Previzualizare")
        try:
            render_mermaid(st.session_state.current_mermaid_code)
        except Exception as e:
            st.error(f"Eroare randare: {e}")
            st.code(st.session_state.current_mermaid_code, language="mermaid")
    else:
        st.info("👈 Scrie în chat pentru a genera o diagramă.")
