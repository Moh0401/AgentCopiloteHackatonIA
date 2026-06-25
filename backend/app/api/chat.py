"""Endpoint /chat — interaction avec le graphe multi-agents."""

import os
import sys

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from agent.graph import get_graph
from backend.app.api.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Envoie un message au copilote et retourne la réponse."""
    graph = get_graph()
    config = {"configurable": {"thread_id": request.thread_id}}

    try:
        # On utilise le thread_id comme rôle de l'utilisateur connecté
        formatted_message = f"Rôle de l'utilisateur : {request.thread_id}\nQuestion : {request.message}"
        result = graph.invoke(
            {"messages": [HumanMessage(content=formatted_message)]},
            config=config,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur graphe : {exc}") from exc

    messages = result.get("messages", [])
    if not messages:
        raise HTTPException(status_code=500, detail="Aucune réponse générée.")

    last = messages[-1]
    agent_name = getattr(last, "name", None) or result.get("current_agent", "supervisor")

    return ChatResponse(
        thread_id=request.thread_id,
        response=last.content,
        agent=agent_name,
    )
