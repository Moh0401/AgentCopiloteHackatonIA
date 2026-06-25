import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import psycopg2
from pgvector.psycopg2 import register_vector

# Charger les variables du fichier .env
load_dotenv()

def process_company_documents():
    print("=== Début de la vectorisation des documents ===")

    # 1. Charger tous les fichiers .txt du dossier data_input
    # Si tu utilises des PDF plus tard, tu changeras 'TextLoader' par 'PyPDFLoader' et la glob en "*.pdf"
    loader = DirectoryLoader('./backend/data_input/', glob="**/*.txt", loader_cls=TextLoader)
    docs = loader.load()
    print(f"Nombre de documents détectés : {len(docs)}")

    if len(docs) == 0:
        print("Erreur : Aucun document trouvé dans backend/data_input/")
        return

    # 2. Chunking : Découpage intelligent (Morceaux de 600 caractères, chevauchement de 100)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Nombre de chunks générés : {len(chunks)}")

    # 3. Connexion à l'API Hugging Face pour les Embeddings
    print("Connexion à Hugging Face...")
    embeddings_model = HuggingFaceEndpointEmbeddings(
        model=os.getenv("HF_EMBED_MODEL", "mixedbread-ai/mxbai-embed-large-v1"),
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    )

    # 4. Connexion à la base PostgreSQL (Port 5433)
    conn = psycopg2.connect(os.getenv("POSTGRES_DATABASE_URL", "postgresql://user:password@127.0.0.1:5433/pme_db"))
    cursor = conn.cursor()
    register_vector(conn)

    # 5. Création de la table si elle n'existe pas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entreprise_docs_embeddings (
            id SERIAL PRIMARY KEY,
            titre VARCHAR(255),
            content TEXT,
            embedding VECTOR(1024) -- 1024 dimensions pour mxbai-embed-large-v1 (modifie si tu utilises nomic)
        );
    """)

    # Vider la table pour éviter les doublons si on relance le script
    cursor.execute("TRUNCATE TABLE entreprise_docs_embeddings;")

    # 6. Boucle d'envoi vers la base de données
    for idx, chunk in enumerate(chunks):
        texte_brut = chunk.page_content
        source_doc = chunk.metadata.get('source', 'Inconnu')
        
        print(f"Vectorisation du chunk {idx + 1}/{len(chunks)} issu de {source_doc}...")
        vector = embeddings_model.embed_query(texte_brut)
        
        cursor.execute(
            """INSERT INTO entreprise_docs_embeddings (titre, content, embedding) 
               VALUES (%s, %s, %s);""",
            (source_doc, texte_brut, vector)
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("=== Succès : Tous les documents sont dans pgvector ! ===")

if __name__ == "__main__":
    process_company_documents()