from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class GenerateResponse(BaseModel):
    mermaid: str
    corrected_prompt: str
    session_id: str

class Message(BaseModel):
    role: str
    content: str
    mermaid_code: Optional[str] = None

class HistoryRequest(BaseModel):
    session_id: str

class HistoryResponse(BaseModel):
    messages: list[Message]
