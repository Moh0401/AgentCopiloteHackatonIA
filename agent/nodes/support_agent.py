"""Nœud Agent Support — spécialiste RAG réclamations."""

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from agent.config import llm
from agent.state import AgentState
from agent.tools import search_company_docs
from agent.tools.support_vector import search_complaints, get_complaint_summary

def support_agent_node(state: AgentState) -> dict:
    """Exécute l'agent Support avec outils RAG et SQL manuels."""
    try:
        # Étape 1 : Choisir l'outil et l'argument
        prompt_tool = ChatPromptTemplate.from_messages([
            ("system", "Tu es un agent de support client.\n"
                       "Tu as accès à deux bases de connaissances :\n"
                       "1. La FAQ et les politiques internes de l'entreprise.\n"
                       "2. La base de données des réclamations clients passées.\n\n"
                       "Si la question concerne les règles, politiques, FAQ, ou quoi faire dans une situation (ex: sac mouillé), tu DOIS chercher dans la FAQ.\n"
                       "Si la question concerne les réclamations ou des clients mécontents spécifiques, cherche dans les réclamations avec SEARCH_RECLAMATIONS.\n"
                       "Si la question demande un résumé, une analyse globale ou des statistiques sur les réclamations, utilise la commande SUMMARY_RECLAMATIONS.\n"
                       "Si tu as besoin de voir la liste complète ou les réclamations récentes pour les analyser, utilise RECENT_RECLAMATIONS.\n\n"
                       "Réponds UNIQUEMENT par l'une des commandes suivantes :\n"
                       "- SEARCH_DOCS: <mots clés de recherche>\n"
                       "- SEARCH_RECLAMATIONS: <mots clés de recherche>\n"
                       "- SUMMARY_RECLAMATIONS\n"
                       "- RECENT_RECLAMATIONS\n"
                       "Exemple: SEARCH_DOCS: sac riz mouillé remboursement"),
            ("placeholder", "{messages}")
        ])
        chain_tool = prompt_tool | llm
        res_tool = chain_tool.invoke({"messages": state["messages"]})
        command = res_tool.content.strip()
        
        # Étape 2 : Exécuter l'outil
        if command.startswith("SEARCH_DOCS:"):
            query = command.replace("SEARCH_DOCS:", "").strip()
            db_result = search_company_docs.invoke({"query": query})
            source = "FAQ / Politiques Internes"
        elif command.startswith("SEARCH_RECLAMATIONS:"):
            query = command.replace("SEARCH_RECLAMATIONS:", "").strip()
            db_result = search_complaints.invoke({"query": query})
            source = "Base de données des réclamations"
        elif command.startswith("SUMMARY_RECLAMATIONS") or command.startswith("ANALYSE_RECLAMATIONS"):
            db_result = get_complaint_summary.invoke({})
            source = "Base de données des réclamations (Résumé stat)"
        elif command.startswith("RECENT_RECLAMATIONS"):
            db_result = search_complaints.invoke({"query": ""})
            source = "Base de données des réclamations (Récentes)"
        else:
            # Fallback par défaut sur la FAQ
            db_result = search_company_docs.invoke({"query": command})
            source = "FAQ / Politiques Internes"

        # Étape 3 : Formuler la réponse finale
        prompt_final = ChatPromptTemplate.from_messages([
            ("system", "Tu es l'agent Support de MaliAgro.\n"
                       "Réponds à la question de l'utilisateur en te basant UNIQUEMENT sur les informations suivantes issues de '{source}' :\n\n"
                       "{db_result}\n\n"
                       "N'invente aucune règle. Si l'information n'est pas dans le texte, dis-le clairement."),
            ("placeholder", "{messages}")
        ])
        chain_final = prompt_final | llm
        final_res = chain_final.invoke({
            "messages": state["messages"],
            "source": source,
            "db_result": db_result
        })

        return {
            "messages": [AIMessage(content=final_res.content, name="support_agent")],
            "current_agent": "support_agent",
        }
    except Exception as exc:
        return {
            "messages": [AIMessage(content=f"Erreur agent Support : {exc}", name="support_agent")],
            "current_agent": "support_agent",
        }
