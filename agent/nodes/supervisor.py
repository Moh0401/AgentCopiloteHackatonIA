"""Nœud Superviseur — aiguille la demande vers l'agent spécialisé."""

from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from agent.config import llm
from agent.state import AgentState, MemberName

SYSTEM_PROMPT = """Tu es le superviseur d'un copilote IA pour dirigeants de PME.
Analyse la demande de l'utilisateur et route vers l'agent le plus compétent :

- sales_agent : questions sur les ventes, chiffre d'affaires, produits, régions, statistiques SQL sur les ventes
- support_agent : réclamations clients, résumé des réclamations, statistiques de réclamations, insatisfaction, motifs de plaintes, support, FAQ, politiques internes, règles de l'entreprise, documents RAG
- marketing_agent : fidélisation, clients inactifs, segmentation, portefeuille client
- FINISH : uniquement si un agent spécialisé a déjà répondu à la question en cours

Ne choisis FINISH que lorsque la dernière réponse provient d'un agent (sales_agent, support_agent ou marketing_agent)."""


DIRECT_REPLY_PROMPT = """Tu es le copilote IA d'une PME SaaS.
Présente-toi brièvement et explique que tu peux aider sur les ventes, le support client et la fidélisation.
Ne prends jamais de décision à la place du dirigeant."""


class RouteDecision(BaseModel):
    """Décision de routage structurée."""

    next: MemberName = Field(description="Agent à activer ou FINISH")


def _fallback_route(content: str) -> Literal["sales_agent", "support_agent", "marketing_agent"]:
    content = content.lower()
    if any(k in content for k in ("vente", "ca", "chiffre", "produit", "sql")):
        return "sales_agent"
    if any(k in content for k in ("réclamation", "plainte", "support", "insatisfaction", "politique", "faq", "règle", "mouillé", "livré")):
        return "support_agent"
    if any(k in content for k in ("client", "fidél", "inactif", "segment")):
        return "marketing_agent"
    return "sales_agent"


def supervisor_node(state: AgentState) -> dict:
    """Analyse l'intention et choisit le prochain agent."""
    messages = state["messages"]
    last = messages[-1]
    agent_already_replied = getattr(last, "name", None) in (
        "sales_agent", "support_agent", "marketing_agent"
    )

    if agent_already_replied:
        return {"next": "FINISH", "current_agent": "supervisor"}

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT + "\n\nRéponds UNIQUEMENT par le nom de l'agent choisi parmi : sales_agent, support_agent, marketing_agent, ou FINISH. Aucun autre texte."),
        MessagesPlaceholder(variable_name="messages"),
    ])

    try:
        chain = prompt | llm
        response = chain.invoke({"messages": messages})
        output = response.content.strip().lower()
        
        if "support_agent" in output:
            next_agent = "support_agent"
        elif "marketing_agent" in output:
            next_agent = "marketing_agent"
        elif "finish" in output:
            next_agent = "FINISH"
        else:
            next_agent = "sales_agent"
    except Exception as exc:
        print(f"Erreur supervisor LLM: {exc}")
        next_agent = _fallback_route(str(last.content))

    if next_agent == "FINISH":
        reply = llm.invoke([
            SystemMessage(content=DIRECT_REPLY_PROMPT),
            *messages,
        ])
        return {
            "messages": [AIMessage(content=reply.content, name="supervisor")],
            "next": "FINISH",
            "current_agent": "supervisor",
        }

    return {"next": next_agent, "current_agent": "supervisor"}
