from pydantic import BaseModel, Field
from typing import Any

class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    session_id: str | None = None

class Citation(BaseModel):
    document_name: str
    page_number: int
    chunk_id: str

class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = []
    evidence_count: int = 0
    feedback_rounds: int = 0
    analysis: dict[str, Any] = {}
