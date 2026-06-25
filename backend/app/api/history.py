"""Endpoint /history — récupération de l'historique de conversation."""

import os
import sys

from fastapi import APIRouter, HTTPException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from agent.graph import get_graph
from backend.app.api.schemas import HistoryMessage, HistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{thread_id}", response_model=HistoryResponse)
async def get_history(thread_id: str):
    """Retourne l'historique des messages pour un thread_id donné."""
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        state = graph.get_state(config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lecture état : {exc}") from exc

    if not state or not state.values:
        return HistoryResponse(thread_id=thread_id, messages=[])

    raw_messages = state.values.get("messages", [])
    history = []
    for msg in raw_messages:
        role = "user" if msg.type == "human" else "assistant"
        history.append(
            HistoryMessage(
                role=role,
                content=msg.content,
                agent=getattr(msg, "name", None),
            )
        )

    return HistoryResponse(thread_id=thread_id, messages=history)
