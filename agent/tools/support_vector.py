"""Outils de recherche et d'analyse de réclamations pour l'agent Support."""

from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.orm import Session

from agent.tools.db import get_mysql_engine


def _normalize_search_string(query: str) -> str:
    query = query.strip()
    query = query.replace("%", "%%")
    query = query.replace("_", "\\_")
    return f"%{query}%"


@tool
def search_complaints(query: str, limit: int = 5) -> str:
    """Recherche de réclamations clients dans MySQL par mots-clés.

    Args:
        query: Terme de recherche (ex: 'lenteur plateforme', 'facturation').
        limit: Nombre maximum de résultats.

    Returns:
        Les réclamations les plus pertinentes trouvées dans MySQL.
    """
    try:
        search_value = _normalize_search_string(query)
        engine = get_mysql_engine()
        with Session(engine) as session:
            result = session.execute(
                text("""
                   SELECT id, description, status, titre
                FROM reclamations
                WHERE titre LIKE :search OR description LIKE :search
                ORDER BY created_at DESC
                LIMIT :limit
                """),
                {"search": search_value, "limit": limit},
            )
            rows = result.fetchall()

            if not rows:
                return f"Aucune réclamation trouvée pour : '{query}'."

            lines = []
            for row in rows:
                lines.append(
                    f"[#{row.id}] statut={row.status} date={row.created_at}\\n"
                    f"Sujet: {row.subject}\\n"
                    f"Description: {row.description}"
                )
            return "\\n\\n".join(lines)

    except Exception as exc:
        return f"Erreur recherche réclamations : {exc}"


@tool
def get_complaint_summary() -> str:
    """Retourne un résumé statistique des réclamations par statut depuis MySQL."""
    try:
        engine = get_mysql_engine()
        with Session(engine) as session:
            result = session.execute(
                text("""
                    SELECT status, COUNT(*) AS count
                    FROM complaints
                    GROUP BY status
                    ORDER BY count DESC
                """),
            )
            rows = result.fetchall()
            if not rows:
                return "Aucune réclamation enregistrée."
            return "\\n".join(f"- {row.status}: {row.count}" for row in rows)

    except Exception as exc:
        return f"Erreur résumé réclamations : {exc}"
