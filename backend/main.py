import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import aiosqlite
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schema import GenerateRequest, GenerateResponse, Message, HistoryResponse
from agents import preprocess_prompt, generate_mermaid

load_dotenv()

DATABASE_PATH = "history.db"

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                mermaid_code TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="LSEG Diagram Generator API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    corrected = await preprocess_prompt(request.prompt)
    mermaid_code = await generate_mermaid(corrected)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO sessions (id, created_at, updated_at) VALUES (?, ?, ?)",
            (session_id, datetime.now().isoformat(), datetime.now().isoformat())
        )
        await db.execute(
            "INSERT INTO messages (session_id, role, content, mermaid_code, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, "user", request.prompt, None, datetime.now().isoformat())
        )
        await db.execute(
            "INSERT INTO messages (session_id, role, content, mermaid_code, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, "assistant", corrected, mermaid_code, datetime.now().isoformat())
        )
        await db.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), session_id)
        )
        await db.commit()
    
    return GenerateResponse(
        mermaid=mermaid_code,
        corrected_prompt=corrected,
        session_id=session_id
    )

@app.post("/api/history", response_model=HistoryResponse)
async def get_history(session_id: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT role, content, mermaid_code FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,)
        )
        rows = await cursor.fetchall()
    
    messages = [
        Message(role=row["role"], content=row["content"], mermaid_code=row["mermaid_code"])
        for row in rows
    ]
    return HistoryResponse(messages=messages)

@app.get("/api/sessions")
async def list_sessions():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, created_at, updated_at FROM sessions ORDER BY updated_at DESC LIMIT 20"
        )
        rows = await cursor.fetchall()
    return [{"id": row["id"], "created_at": row["created_at"], "updated_at": row["updated_at"]} for row in rows]

@app.get("/health")
async def health():
    return {"status": "ok"}
