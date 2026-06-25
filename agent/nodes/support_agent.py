"""Nœud Agent Support — spécialiste RAG réclamations."""

from functools import lru_cache

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabase, SQLDatabaseToolkit

from agent.config import llm
from agent.state import AgentState
from agent.tools.db import get_mysql_engine

SUPPORT_SYSTEM = """Tu es l'agent Support de MaliAgro.
Interdiction absolue d'inventer des chiffres ou des faits.
Tu DOIS exécuter une requête SQL sur la table 'reclamations' pour répondre aux questions de support.
Réponds obligatoirement à partir des données SQL réelles et ne fais aucune supposition.

Tables disponibles :
- reclamations

Règles strictes :
- Lorsque l'utilisateur demande une réclamation, un cas client, une statistique ou un motif d'insatisfaction, TU DOIS ABSOLUMENT utiliser les outils SQL fournis.
- Ne rédige jamais la requête SQL pour l'utilisateur.
- Ne pré-explique pas comment construire la requête.
- Utilise UNIQUEMENT des requêtes SELECT.
- Si le résultat est vide, indique clairement qu'aucune réclamation n'a été trouvée.
"""

@lru_cache(maxsize=1)
def _get_support_agent():
    support_db = SQLDatabase(
        get_mysql_engine(),
        include_tables=["reclamations"],
        lazy_table_reflection=True,
    )
    support_toolkit = SQLDatabaseToolkit(db=support_db, llm=llm)
    return create_react_agent(
        llm,
        tools=support_toolkit.get_tools(),
        prompt=SystemMessage(content=SUPPORT_SYSTEM),
    )


def support_agent_node(state: AgentState) -> dict:
    """Exécute l'agent Support avec outils RAG."""
    try:
        result = _get_support_agent().invoke({"messages": state["messages"]})
        last_message = result["messages"][-1]
        return {
            "messages": [AIMessage(content=last_message.content, name="support_agent")],
            "current_agent": "support_agent",
        }
    except Exception as exc:
        return {
            "messages": [AIMessage(content=f"Erreur agent Support : {exc}", name="support_agent")],
            "current_agent": "support_agent",
        }
