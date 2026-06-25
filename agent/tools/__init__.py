import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import psycopg2
from pgvector.psycopg2 import register_vector

load_dotenv()

_hf_embeddings = HuggingFaceEndpointEmbeddings(
    model="mixedbread-ai/mxbai-embed-large-v1",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)


def _to_pgvector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"


@tool
def search_company_docs(query: str) -> str:
    """Recherche de documents d'entreprise via pgvector et renvoie les 3 meilleurs chunks."""
    try:
        query_vector = _hf_embeddings.embed_query(query)
        vector_literal = _to_pgvector_literal(query_vector)

        database_url = os.getenv("POSTGRES_DATABASE_URL", "postgresql://user:password@127.0.0.1:5433/pme_db")
        conn = psycopg2.connect(database_url)
        register_vector(conn)

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, titre, content,
                       embedding <=> CAST(%s AS vector) AS distance
                FROM entreprise_docs_embeddings
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> CAST(%s AS vector)
                LIMIT 3
                """,
                (vector_literal, vector_literal),
            )
            rows = cursor.fetchall()

        conn.close()

        if not rows:
            return f"Aucun document pertinent trouvé pour la requête : '{query}'."

        results = []
        for row in rows:
            doc_id, titre, content, distance = row
            results.append(
                f"Document #{doc_id} - {titre}\n{content.strip()}"
            )

        return "\n\n---\n\n".join(results)

    except Exception as exc:
        return f"Erreur de recherche dans les documents d'entreprise : {exc}"

