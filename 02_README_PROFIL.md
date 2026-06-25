# Copilote PME - Système Multi-Agents Local (LangGraph & Ollama)

Ce projet implémente un copilote d'intelligence artificielle métier destiné aux dirigeants de PME. Il utilise une architecture **Multi-Agents supervisée** propulsée par **LangGraph** et exécutée entièrement en local grâce à **Ollama**. Le système interagit avec une base de données PostgreSQL pour l'analyse des données structurées et textuelles.

## 🏗️ Architecture du Système

Le projet abandonne l'approche d'agent unique pour une architecture officielle LangGraph de type **Supervisor / Sub-Agents**. Cela permet de segmenter les compétences, de réduire la taille des prompts et de maximiser la précision des modèles locaux d'Ollama.

```text
                        +----------------------+
                        |   Interface Client   |
                        +----------+-----------+
                                   | (Langage Naturel)
                                   v
                       +-----------------------+
                       |   Agent Superviseur   | <--- (Ollama / Choix du nœud)
                       +----+------+------+----+
                            |      |      |
       +--------------------+      |      +--------------------+
       |                           v                           |
+------v------+             +------------+              +------v------+
|  Agent SQL  |             | Agent RAG  |              | Agent Client|
|  (Ventes)   |             | (Plaintes) |              | (Fidélité)  |
+------+------+             +-----+------+              +------+------+
       |                          |                            |
[Outil: SQL DB]            [Outil: Vector DB]          [Outil: Analytics]