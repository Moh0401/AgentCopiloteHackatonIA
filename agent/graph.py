"""Assemblage et compilation du graphe multi-agents LangGraph."""

import os
from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.nodes.marketing_agent import marketing_agent_node
from agent.nodes.sales_agent import sales_agent_node
from agent.nodes.supervisor import supervisor_node
from agent.nodes.support_agent import support_agent_node
from agent.state import AgentState

MEMBERS = ["sales_agent", "support_agent", "marketing_agent"]

_checkpointer = None
_graph = None


def _route_from_supervisor(state: AgentState) -> str:
    next_node = state.get("next", "FINISH")
    if next_node == "FINISH":
        return END
    return next_node


def build_graph(checkpointer=None):
    """Construit et compile le graphe Supervisor / Sub-Agents."""
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("sales_agent", sales_agent_node)
    workflow.add_node("support_agent", support_agent_node)
    workflow.add_node("marketing_agent", marketing_agent_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {member: member for member in MEMBERS} | {END: END},
    )

    for member in MEMBERS:
        workflow.add_edge(member, "supervisor")

    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)


def get_postgres_checkpointer():
    """Crée un PostgresSaver persistant via pool de connexions."""
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    database_url = os.getenv(
        "POSTGRES_DATABASE_URL", "postgresql://user:password@localhost:5433/pme_db"
    )

    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from psycopg_pool import ConnectionPool

        pool = ConnectionPool(
            conninfo=database_url,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        )
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        _checkpointer = checkpointer
        return _checkpointer
    except Exception as exc:
        print(f"[graph] PostgresSaver indisponible, fallback MemorySaver: {exc}")
        return MemorySaver()


def get_graph():
    """Retourne le graphe compilé avec PostgresSaver (ou MemorySaver en fallback)."""
    global _graph
    if _graph is None:
        checkpointer = get_postgres_checkpointer()
        _graph = build_graph(checkpointer=checkpointer)
    return _graph


def reset_graph():
    """Réinitialise le graphe (utile après changement de config)."""
    global _graph, _checkpointer
    _graph = None
    _checkpointer = None
