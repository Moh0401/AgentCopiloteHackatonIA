"""Point d'entrée FastAPI du Copilote IA PME."""

import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

backend_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(backend_dir, ".env"))
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(backend_dir, "..")))

from backend.app.api.chat import router as chat_router
from backend.app.api.history import router as history_router
from backend.app.core.config import settings
from backend.app.core.langsmith import configure_langsmith

langsmith_enabled = configure_langsmith(
    tracing_enabled=settings.langchain_tracing_v2,
    api_key=settings.langchain_api_key,
    project=settings.langchain_project,
    endpoint=settings.langchain_endpoint,
)

os.environ.setdefault("DATABASE_URL", settings.database_url)
os.environ.setdefault("MYSQL_DATABASE_URL", settings.mysql_database_url)
os.environ.setdefault("POSTGRES_DATABASE_URL", settings.postgres_database_url)
os.environ.setdefault("OLLAMA_BASE_URL", settings.ollama_base_url)
os.environ.setdefault("OLLAMA_MODEL", settings.ollama_model)
os.environ.setdefault("OLLAMA_EMBED_MODEL", settings.ollama_embed_model)

from agent.graph import get_graph

get_graph()

app = FastAPI(title=settings.app_title, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(history_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.app_version,
        "langsmith": langsmith_enabled,
        "database_url": settings.database_url.split("@")[-1],
    }
