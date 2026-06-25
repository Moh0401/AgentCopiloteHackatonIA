# AgentCopiloteHackatonIA
## Copilote IA pour PME SaaS (Challenge IA)

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

📝 Guide d'Intégration Frontend & Environnement (Docker / Database)Ce document centralise la configuration des 3 endpoints clés pour le Frontend, la mise en route de Docker pour la base de données PostgreSQL, et l'affichage des données directement dans VS Code.1. Guide d'Intégration Frontend (Les 3 Endpoints)Dans cette configuration, le Frontend gère le thread_id en y passant directement le rôle de l'utilisateur connecté (Commercial, RESPON_PME, RESPON_REL_CLIENT). Cela permet d'isoler la mémoire de l'IA par profil métier sans aucune logique complexe côté Backend.Endpoint 1 : Authentification de l'utilisateur (Spring Boot)Avant toute chose, le Frontend doit connecter l'utilisateur pour récupérer son rôle et son jeton de sécurité.URL : POST http://localhost:8080/auth/loginRequest Body :JSON{
  "email": "awa.keita@maliagro.ml",
  "password": "AwaPassword123"
}
Ce que le Front doit stocker : L'accessToken (pour les requêtes métiers) et le rôle de l'utilisateur (qui servira de thread_id).Endpoint 2 : Saisie d'une Vente (Spring Boot)Cet endpoint métier est sécurisé. Le Front doit passer le token dans le header Authorization: Bearer <token>.URL : POST http://localhost:8080/api/ventesRequest Body :JSON{
  "clientId": 1,
  "lignes": [
    {
      "produitId": 1,
      "quantite": 3
    }
  ]
}
Endpoint 3 : Discussion avec l'Agent IA (Python FastAPI)C'est ici que la magie opère. Le Frontend injecte le rôle récupéré à l'étape 1 dans le champ thread_id.URL : POST http://localhost:8000/chatRequest Body :JSON{
  "message": "Quelle est le montant des ventes ?",
  "thread_id": "Commercial" 
}
Response Body :JSON{
  "thread_id": "Commercial",
  "response": "Le chiffre d'affaires total enregistré par l'équipe commerciale est de 300 000 F CFA.",
  "agent": "sales_agent"
}
2. Configuration des Outils Tech (Docker & VS Code)Pour que toute l'équipe travaille sur la même base PostgreSQL sans se prendre la tête avec des installations locales de serveurs, suivez cette procédure de déploiement.1.Installer Docker Desktop :Prérequis système.Téléchargez et installez Docker Desktop (disponible pour Windows, Mac et Linux). Lancez l'application et assurez-vous que le moteur Docker est actif (icône verte en bas à gauche).2.Lancer le conteneur PostgreSQL :En une seule commande.Ouvrez un terminal et exécutez la commande suivante pour télécharger et lancer l'image PostgreSQL officielle en arrière-plan :Bashdocker run --name maliagro-postgres -e POSTGRES_USER=root -e POSTGRES_PASSWORD=votre_mot_de_passe -e POSTGRES_DB=maliagro_db -p 5432:5432 -d postgres
3.Installer l'extension VS Code :Visualisation graphique.Dans VS Code, allez dans l'onglet Extensions (Ctrl+Shift+X), recherchez "Database Client" (développée par cweijan) ou "PostgreSQL" (par Chris Kolkman) et cliquez sur Installer.4.Connecter l'extension à Docker :Dernière étape.Cliquez sur l'icône de base de données apparue dans la barre latérale de VS Code. Cliquez sur Create Connection (+), choisissez PostgreSQL et entrez les paramètres suivants :Host : localhostPort : 5432User : rootPassword : votre_mot_de_passeDatabase : pme_dbCliquez sur Test Connection puis Save. Vous pouvez maintenant voir vos tables et vos données de test en temps réel !Pro-Tip Hackathon : Si le conteneur Docker est arrêté suite à un redémarrage de l'ordinateur, pas besoin de recréer la commande. Il suffit de taper docker start maliagro-postgres dans le terminal pour tout relancer instantanément.
