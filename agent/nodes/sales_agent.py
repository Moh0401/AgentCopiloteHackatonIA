"""Nœud Agent Ventes — spécialiste SQL."""

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from agent.config import llm
from agent.state import AgentState
from agent.tools.sales_db import execute_sales_query

def sales_agent_node(state: AgentState) -> dict:
    """Exécute l'agent Ventes avec une extraction SQL explicite."""
    try:
        # Étape 1 : Générer la requête SQL
        prompt_sql = ChatPromptTemplate.from_messages([
            ("system", "Tu es un expert SQL. Ton rôle est de générer UNIQUEMENT une requête SQL SELECT valide pour répondre à la question de l'utilisateur.\n"
                       "Interdiction d'ajouter du texte, du markdown ou des explications. Ta réponse doit commencer par SELECT.\n"
                       "Tables disponibles :\n"
                       "- ventes (id, date_vente, montant_total, pme_id, statut, client_id, utilisateur_id)\n"
                       "- lignes_vente (id, pme_id, prix_unitaire, quantite, sous_total, vente_id, produit_id)\n"
                       "- clients (id, adresse, email, nom, pme_id, prenom, telephone)\n"
                       "Exemple: SELECT SUM(montant_total) FROM ventes;"),
            ("placeholder", "{messages}")
        ])
        chain_sql = prompt_sql | llm
        res_sql = chain_sql.invoke({"messages": state["messages"]})
        
        # Nettoyage de la réponse du LLM pour extraire uniquement la requête SQL
        sql_query = res_sql.content.strip().replace('```sql', '').replace('```', '').strip()
        
        # Étape 2 : Exécuter la requête
        if sql_query.upper().startswith("SELECT"):
            db_result = execute_sales_query.invoke({"sql_query": sql_query})
        else:
            db_result = f"Erreur : La requête générée n'est pas un SELECT valide. Requête générée : {sql_query}"

        # Étape 3 : Formuler la réponse finale
        prompt_final = ChatPromptTemplate.from_messages([
            ("system", "Tu es l'agent commercial de MaliAgro.\n"
                       "Réponds à la question de l'utilisateur de manière naturelle en te basant UNIQUEMENT sur le résultat SQL suivant : {db_result}.\n"
                       "N'invente aucun montant. Si le résultat est vide, dis-le. Exprime toujours les montants en Franc CFA (F CFA)."),
            ("placeholder", "{messages}")
        ])
        chain_final = prompt_final | llm
        final_res = chain_final.invoke({
            "messages": state["messages"],
            "db_result": db_result
        })

        return {
            "messages": [AIMessage(content=final_res.content, name="sales_agent")],
            "current_agent": "sales_agent",
        }
    except Exception as exc:
        return {
            "messages": [AIMessage(content=f"Erreur agent Ventes : {exc}", name="sales_agent")],
            "current_agent": "sales_agent",
        }
