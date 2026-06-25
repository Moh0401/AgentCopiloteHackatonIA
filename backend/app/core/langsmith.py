"""Initialisation LangSmith et variables d'environnement partagées."""

import os


def configure_langsmith(
    tracing_enabled: bool,
    api_key: str,
    project: str,
    endpoint: str,
) -> bool:
    """Configure LangSmith si une clé API valide est présente."""
    placeholder_keys = {"", "votre_cle_langsmith", "your_api_key", "changeme"}

    if not tracing_enabled:
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        return False

    if not api_key or api_key.strip() in placeholder_keys:
        print(
            "[langsmith] LANGCHAIN_TRACING_V2=true mais LANGCHAIN_API_KEY invalide. "
            "Définissez votre clé dans backend/.env"
        )
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = api_key.strip()
    os.environ["LANGCHAIN_PROJECT"] = project
    os.environ["LANGCHAIN_ENDPOINT"] = endpoint
    return True
