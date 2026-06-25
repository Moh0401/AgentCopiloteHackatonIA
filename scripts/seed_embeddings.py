"""Génère et stocke les embeddings vectoriels des réclamations dans PostgreSQL."""

import os
import sys

import psycopg2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.config import embeddings


def _to_pgvector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"


def seed_complaint_embeddings() -> int:
    database_url = os.getenv(
        "POSTGRES_DATABASE_URL", "postgresql://user:password@127.0.0.1:5433/pme_db"
    )
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, subject, description
                FROM complaints
                WHERE embedding IS NULL
                ORDER BY id
                """
            )
            rows = cursor.fetchall()

            if not rows:
                print("Toutes les réclamations ont déjà un embedding.")
                return 0

            count = 0
            for row in rows:
                row_id, subject, description = row
                text_to_embed = f"{subject}. {description}"
                vector = embeddings.embed_query(text_to_embed)
                vector_literal = _to_pgvector_literal(vector)

                cursor.execute(
                    """
                    UPDATE complaints
                    SET embedding = CAST(%s AS vector)
                    WHERE id = %s
                    """,
                    (vector_literal, row_id),
                )
                count += 1
                print(f"  Embedding généré pour réclamation #{row_id} — {subject}")

            conn.commit()
            return count


if __name__ == "__main__":
    print("Génération des embeddings pour les réclamations...")
    total = seed_complaint_embeddings()
    print(f"Terminé : {total} embedding(s) créé(s).")
