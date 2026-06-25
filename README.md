# Copilote IA pour PME SaaS (Challenge IA)

Ce projet implémente un assistant décisionnel basé sur une architecture multi-agents supervisée avec **LangGraph**. Il permet aux dirigeants et équipes de PME d'interagir en langage naturel avec leurs données de ventes, de gestion client et de support.

## 🏢 Architecture du Projet

```text
copilote-pme-ia/
├── backend/                  # API Rest (FastAPI)
│   ├── app/
│   │   ├── api/              # Points d'accès (Endpoints /chat, /history)
│   │   ├── core/             # Configuration des variables d'environnement
│   │   └── database/         # Session & Modèles SQLAlchemy/PostgreSQL
│   └── main.py
│
├── agent/                    # Écosystème LangGraph
│   ├── __init__.py
│   ├── config.py             # Initialisation de ChatOllama (ex: llama3)
│   ├── state.py              # Définition du TypedDict d'état global
│   ├── graph.py              # Assemblage du workflow et compilation du graphe
│   │
│   ├── nodes/                # Logique des nœuds du graphe
│   │   ├── __init__.py
│   │   ├── supervisor.py     # Cerveau d'aiguillage
│   │   ├── sales_agent.py    # Nœud Agent Ventes
│   │   ├── support_agent.py  # Nœud Agent Réclamations
│   │   └── marketing_agent.py# Nœud Agent Fidélisation
│   │
│   └── tools/                # Fonctions d'action (Outils LangChain)
│       ├── __init__.py
│       ├── sales_db.py       # Exécuteur de requêtes SQL PostgreSQL
│       └── support_vector.py # Recherche de similarité (pgvector)
│
├── docker-compose.yml        # Pour lancer PostgreSQL + pgvector localement
├── requirements.txt          # Dépendances Python
└── README.md