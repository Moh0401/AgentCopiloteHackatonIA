"""Nœud Agent Marketing/Fidélisation — analyse portefeuille client."""

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from agent.config import llm
from agent.state import AgentState
from agent.tools.sales_db import execute_sales_query

MARKETING_SYSTEM = """Tu es l'agent Fidélisation d'un copilote PME.
Tu analyses le portefeuille client pour détecter :
- Clients inactifs (last_purchase_date ancienne ou is_active = false)
- Clients stratégiques (segment premium, total_spent élevé)
- Opportunités de réactivation

Tables disponibles :
- customers (id, name, email, segment, last_purchase_date, total_spent, is_active)
- sales (id, product_name, quantity, unit_price, total_amount, sale_date, customer_id, region)

Utilise execute_sales_query pour interroger la base. Présente des insights, pas des décisions.
"""

_marketing_agent = create_react_agent(
    llm,
    tools=[execute_sales_query],
    prompt=SystemMessage(content=MARKETING_SYSTEM),
)


def marketing_agent_node(state: AgentState) -> dict:
    """Exécute l'agent Marketing/Fidélisation."""
    try:
        result = _marketing_agent.invoke({"messages": state["messages"]})
        last_message = result["messages"][-1]
        return {
            "messages": [AIMessage(content=last_message.content, name="marketing_agent")],
            "current_agent": "marketing_agent",
        }
    except Exception as exc:
        return {
            "messages": [
                AIMessage(content=f"Erreur agent Marketing : {exc}", name="marketing_agent")
            ],
            "current_agent": "marketing_agent",
        }
