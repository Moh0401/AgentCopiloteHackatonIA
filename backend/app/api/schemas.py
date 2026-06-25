"""Schémas Pydantic pour l'API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message de l'utilisateur")
    thread_id: str = Field(..., description="Identifiant unique de session")


class ChatResponse(BaseModel):
    thread_id: str
    response: str
    agent: str


class HistoryMessage(BaseModel):
    role: str
    content: str
    agent: str | None = None


class HistoryResponse(BaseModel):
    thread_id: str
    messages: list[HistoryMessage]
