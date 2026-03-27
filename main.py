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

# =========================
# CONFIG & BAZA DE DATE
# =========================
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


# Inițializare bază de date
init_db()

# =========================
# UI STYLE
# =========================
st.markdown(
    """
    <style>
        .block-container { padding-top: 1rem; }
        .stTextArea textarea {
            font-family: "JetBrains Mono", "Fira Code", monospace !important;
            font-size: 13px !important;
            line-height: 1.45 !important;
        }
        [data-testid="stChatMessage"] {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
        }
        .badge {display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px;margin-right:6px;}
        .db{background:#dbeafe;color:#1e3a8a;}
        .api{background:#dcfce7;color:#14532d;}
        .user{background:#fef3c7;color:#78350f;}
        .danger{background:#fee2e2;color:#7f1d1d;}
        .queue{background:#ede9fe;color:#4c1d95;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(f"📊 Arhitect Diagrame AI Pro ({MODEL_NAME})")
st.caption(
    "Generează diagrame Mermaid editabile, cu stilizare automată, istoric și preview live."
)

# =========================
# SYSTEM PROMPT (AGRESIV + GHILIMELE)
# =========================
SYSTEM_PROMPT = f"""
You are a senior Diagram Architect specialized in Mermaid.js.
User language can be Romanian/English with typos. Do NOT correct typos in chat.

MANDATORY OUTPUT:
- Return ONLY one fenced block: ```mermaid ... ```
- NO explanations, NO extra prose, NO conversational text.

CRITICAL SYNTAX RULES (Violating these will crash the system):
1) NODE IDs MUST NOT HAVE SPACES. Use underscores or camelCase. BAD: `My Node[Text]`. GOOD: `My_Node[Text]`.
2) NO SPACES AFTER COMMAS IN CLASSES. BAD: `class A, B style`. GOOD: `class A,B style`.
3) SUBGRAPH IDs MUST BE ONE WORD without quotes. BAD: `subgraph "App"`. GOOD: `subgraph App`.
4) LABELS MUST BE IN QUOTES. BAD: `A[API Gateway]`. GOOD: `A["API Gateway"]`.

DIAGRAM QUALITY & STYLE:
1) Always start with: flowchart TD
2) Use semantic node labels with tech icons, e.g.:
   - User: "👤 User"
   - API: "⚙️ API Gateway"
   - Database: "🛢️ PostgreSQL"
   - Queue: "📨 Kafka"
3) Group related nodes inside subgraphs.

If user asks to update ("add/remove"), modify previous diagram contextually.
"""

# =========================
# GESTIUNE SESIUNI & STARE
# =========================
if "current_session_id" not in st.session_state:
    sessions = get_all_sessions()
    if sessions:
        st.session_state.current_session_id = sessions[0]["id"]
    else:
        st.session_state.current_session_id = create_session()


def load_session(session_id: str):
    st.session_state.current_session_id = session_id
    msgs = get_session_messages(session_id)

    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    last_code = ""
    for m in msgs:
        if m["role"] != "system":
            st.session_state.messages.append(
                {"role": m["role"], "content": m["content"]}
            )
        if m["mermaid_code"]:
            last_code = m["mermaid_code"]

    st.session_state.current_mermaid_code = last_code
    st.rerun()


if "messages" not in st.session_state:
    msgs = get_session_messages(st.session_state.current_session_id)
    if msgs:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        last_code = ""
        for m in msgs:
            if m["role"] != "system":
                st.session_state.messages.append(
                    {"role": m["role"], "content": m["content"]}
                )
            if m["mermaid_code"]:
                last_code = m["mermaid_code"]
        st.session_state.current_mermaid_code = last_code
    else:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.current_mermaid_code = ""

if "is_fullscreen" not in st.session_state:
    st.session_state.is_fullscreen = False

# =========================
# SIDEBAR CONTROLS & ISTORIC
# =========================
with st.sidebar:
    st.header("📜 Istoric")

    if st.button("➕ Diagramă Nouă", use_container_width=True):
        new_id = create_session()
        st.session_state.current_session_id = new_id
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.current_mermaid_code = ""
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
                    st.session_state.messages = [
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ]
                    st.session_state.current_mermaid_code = ""
                st.rerun()

    st.divider()
    st.header("⚙️ Setări Diagramă")
    mermaid_theme = st.selectbox(
        "Temă Mermaid", ["dark", "default", "forest", "neutral"], index=0
    )
    direction = st.selectbox("Direcție flowchart", ["TD", "LR", "RL", "BT"], index=0)
    auto_style = st.toggle("Auto-style semantic", value=True)
    st.markdown("### Legenda")
    st.markdown('<span class="badge user">👤 user</span>', unsafe_allow_html=True)
    st.markdown('<span class="badge api">⚙️ api/service</span>', unsafe_allow_html=True)
    st.markdown('<span class="badge db">🛢️ database</span>', unsafe_allow_html=True)
    st.markdown('<span class="badge queue">📨 queue</span>', unsafe_allow_html=True)
    st.markdown(
        '<span class="badge danger">❌ error/fail</span>', unsafe_allow_html=True
    )


# =========================
# SANITIZE + EXTRACT
# =========================
def fix_mermaid_text_errors(code: str) -> str:
    """Funcția salvatoare din al doilea cod care pune ghilimele la label-uri."""
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
                # Adăugăm ghilimele forțat ca să nu crape Mermaid
                line = f'{node_id}["{label}"]{rest}'

        fixed.append(line)

    return "\n".join(fixed)


def sanitize_mermaid(code: str) -> str:
    if not code:
        return ""

    lines = code.split("\n")
    cleaned = []

    for line in lines:
        stripped = line.strip()

        # Fix class A, B style -> class A,B style
        if stripped.startswith("class ") and not stripped.startswith("classDef "):
            parts = stripped.split()
            if len(parts) >= 3:
                ids_part = " ".join(parts[1:-1]).replace(", ", ",")
                cleaned.append(f"class {ids_part} {parts[-1]}")
                continue

        # Fix subgraph "My App" -> subgraph My_App
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


# =========================
# AUTO STYLE ENHANCER
# =========================
def apply_semantic_styles(code: str, flow_direction="TD"):
    if not code:
        return code

    # Aplicăm fix-ul pentru ghilimele
    code = fix_mermaid_text_errors(code)

    # Forțăm flowchart direction dacă e graph/flowchart
    code = re.sub(
        r"^\s*(graph|flowchart)\s+\w+\s*$",
        f"flowchart {flow_direction}",
        code,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    init_block = f"""%%{{init: {{"theme":"{mermaid_theme}","securityLevel":"loose","flowchart":{{"htmlLabels":true,"curve":"basis"}}}} }}%%"""

    class_defs = """
classDef user fill:#fef3c7,stroke:#f59e0b,color:#111827,stroke-width:1.5px;
classDef api fill:#dcfce7,stroke:#22c55e,color:#052e16,stroke-width:1.5px;
classDef db fill:#dbeafe,stroke:#3b82f6,color:#0b3b7a,stroke-width:1.5px;
classDef queue fill:#ede9fe,stroke:#8b5cf6,color:#3b0764,stroke-width:1.5px;
classDef cache fill:#ccfbf1,stroke:#14b8a6,color:#134e4a,stroke-width:1.5px;
classDef auth fill:#e0e7ff,stroke:#6366f1,color:#312e81,stroke-width:1.5px;
classDef ext fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-dasharray: 5 3;
classDef danger fill:#fee2e2,stroke:#ef4444,color:#7f1d1d,stroke-width:2px;
"""

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


# =========================
# RENDER
# =========================
def render_mermaid(mermaid_code, frame_height=600):
    safe_code = html.escape(mermaid_code)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: "{mermaid_theme}",
                securityLevel: "loose",
                flowchart: {{ htmlLabels: true, curve: "basis", useMaxWidth: true }}
            }});
        </script>
        <style>
            body {{
                margin: 0; padding: 14px;
                background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
                font-family: Inter, Segoe UI, Roboto, sans-serif;
            }}
            .card {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 14px;
                padding: 14px;
                box-shadow: 0 10px 30px rgba(0,0,0,.3);
                overflow: auto;
                height: {frame_height - 40}px;
            }}
            .mermaid {{
                display: flex;
                justify-content: center;
                align-items: flex-start;
                min-height: {frame_height - 80}px;
            }}
            svg {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="mermaid">{safe_code}</div>
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=frame_height, scrolling=True)


# =========================
# LAYOUT & LOGIC
# =========================

if st.session_state.is_fullscreen:
    # --- MOD FULL SCREEN ---
    st.subheader("🔍 Previzualizare Diagramă (Full Screen)")

    if st.button("🔙 Închide Full Screen", type="primary"):
        st.session_state.is_fullscreen = False
        st.rerun()

    render_mermaid(st.session_state.current_mermaid_code, frame_height=800)

else:
    # --- MOD NORMAL ---
    col_chat, col_editor = st.columns([1, 1], gap="large")

    with col_chat:
        st.subheader("💬 Chat AI")
        user_prompt = st.chat_input(
            "Ex: fă o arhitectură de e-commerce cu microservicii + kafka + redis"
        )
        if user_prompt:
            save_message(st.session_state.current_session_id, "user", user_prompt)
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            st.rerun()

        chat_container = st.container(height=520)
        with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] != "system":
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

    # Generate assistant reply when last is user
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with col_chat:
            with st.chat_message("assistant"):
                with st.spinner("Generez diagramă..."):
                    try:
                        response = ollama.chat(
                            model=MODEL_NAME, messages=st.session_state.messages
                        )
                        reply = response["message"]["content"]
                        st.session_state.messages.append(
                            {"role": "assistant", "content": reply}
                        )

                        code = extract_mermaid_code(reply)
                        if code:
                            if auto_style:
                                code = apply_semantic_styles(
                                    code, flow_direction=direction
                                )
                            st.session_state.current_mermaid_code = code

                        first_words = (st.session_state.messages[-2]["content"])[
                            :40
                        ].replace(" ", "_")
                        update_session_title(
                            st.session_state.current_session_id, first_words
                        )
                        save_message(
                            st.session_state.current_session_id,
                            "assistant",
                            reply,
                            code or "",
                        )

                        st.rerun()
                    except Exception as e:
                        st.error(f"Eroare Ollama: {e}")

    with col_editor:
        st.subheader("✏️ Editor Live & Preview")

        if st.session_state.current_mermaid_code:
            edited_code = st.text_area(
                "Modifică manual codul Mermaid:",
                value=st.session_state.current_mermaid_code,
                height=280,
            )

            st.session_state.current_mermaid_code = edited_code

            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                st.download_button(
                    "📄 Download .mmd",
                    data=st.session_state.current_mermaid_code.encode("utf-8"),
                    file_name="diagram.mmd",
                    mime="text/plain",
                )
            with c2:
                if st.button("🎨 Re-aplică auto-style"):
                    st.session_state.current_mermaid_code = apply_semantic_styles(
                        st.session_state.current_mermaid_code, flow_direction=direction
                    )
                    st.rerun()
            with c3:
                if st.button("🔍 Full Screen"):
                    st.session_state.is_fullscreen = True
                    st.rerun()

            st.markdown("### Previzualizare")
            render_mermaid(st.session_state.current_mermaid_code)
        else:
            st.info("👈 Scrie în chat ca să generăm prima diagramă.")
