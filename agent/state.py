"""État partagé du graphe multi-agents."""

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """État global maintenu par LangGraph entre les nœuds."""

    messages: Annotated[list, add_messages]
    next: str
    current_agent: str

MemberName = Literal["sales_agent", "support_agent", "marketing_agent", "FINISH"]
