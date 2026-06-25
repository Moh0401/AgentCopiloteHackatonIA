"""Configuration centralisée via variables d'environnement."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://user:password@localhost:5433/pme_db"
    mysql_database_url: str = (
        "mysql+pymysql://root:@localhost:3306/copilote_db?charset=utf8mb4"
    )
    postgres_database_url: str = "postgresql://user:password@localhost:5433/pme_db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:latest"
    ollama_embed_model: str = "nomic-embed-text"

    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "copilote-pme"
    langchain_endpoint: str = "https://api.smith.langchain.com"

    app_title: str = "Copilote IA PME"
    app_version: str = "0.1.0"


settings = Settings()
