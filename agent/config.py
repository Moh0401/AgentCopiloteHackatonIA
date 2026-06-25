import os
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_ollama import OllamaEmbeddings

# Chargement explicite du .env backend pour s'assurer que le token est présent.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))
load_dotenv()

token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not token:
    raise RuntimeError("HUGGINGFACEHUB_API_TOKEN is missing")

llm_endpoint = HuggingFaceEndpoint(
    repo_id=os.getenv("HF_LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct"),
    task="text-generation",
    huggingfacehub_api_token=token,
    temperature=0.7,
    max_new_tokens=512,
)

llm = ChatHuggingFace(llm=llm_endpoint)

# Les embeddings restent gérés par Ollama pour le moment.
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

embeddings = OllamaEmbeddings(
    model=OLLAMA_EMBED_MODEL,
    base_url=OLLAMA_BASE_URL,
)
