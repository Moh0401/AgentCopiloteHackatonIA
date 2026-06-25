"""Outil SQL sécurisé pour l'agent Ventes."""

import re

from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.orm import Session

from agent.tools.db import get_mysql_engine

FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


@tool(return_direct=True)
def execute_sales_query(sql_query: str) -> str:
    """Exécute une requête SQL SELECT sur la base de données des ventes et clients.

    Args:
        sql_query: Requête SQL de type SELECT uniquement.

    Returns:
        Résultat formaté en texte ou message d'erreur.
    """
    query = sql_query.strip().rstrip(";")

    if not query.upper().startswith("SELECT"):
        return "Erreur : seules les requêtes SELECT sont autorisées."

    if FORBIDDEN_KEYWORDS.search(query):
        return "Erreur : opération d'écriture ou DDL interdite."

    try:
        engine = get_mysql_engine()
        with Session(engine) as session:
            result = session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())

            if not rows:
                return "Aucun résultat trouvé."

            header = " | ".join(columns)
            separator = "-|-".join(["-" * len(c) for c in columns])
            lines = [
                " | ".join(str(v) for v in row) for row in rows[:50]
            ]
            output = f"{header}\n{separator}\n" + "\n".join(lines)
            if len(rows) > 50:
                output += f"\n... ({len(rows) - 50} lignes supplémentaires)"
            return output

    except Exception as exc:
        return f"Erreur SQL : {exc}"
