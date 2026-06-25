-- Extension pgvector pour la recherche sémantique
CREATE EXTENSION IF NOT EXISTS vector;

-- Table des ventes
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    sale_date DATE NOT NULL,
    customer_id INTEGER,
    region VARCHAR(100)
);

-- Table des clients
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    segment VARCHAR(50),
    last_purchase_date DATE,
    total_spent DECIMAL(12, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Table des réclamations (avec embedding pour RAG)
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding vector(768)
);

-- Données de démonstration
INSERT INTO customers (name, email, segment, last_purchase_date, total_spent, is_active) VALUES
    ('Entreprise Alpha', 'contact@alpha.fr', 'premium', '2025-05-15', 45000.00, TRUE),
    ('Beta Corp', 'info@beta.fr', 'standard', '2024-11-20', 12000.00, FALSE),
    ('Gamma SARL', 'hello@gamma.fr', 'premium', '2025-06-01', 78000.00, TRUE),
    ('Delta SAS', 'admin@delta.fr', 'standard', '2025-01-10', 8500.00, TRUE),
    ('Epsilon Ltd', 'sales@epsilon.fr', 'standard', '2023-08-05', 3200.00, FALSE);

INSERT INTO sales (product_name, quantity, unit_price, total_amount, sale_date, customer_id, region) VALUES
    ('Licence Pro', 10, 500.00, 5000.00, '2025-06-01', 1, 'IDF'),
    ('Licence Standard', 25, 200.00, 5000.00, '2025-05-20', 3, 'Sud'),
    ('Support Premium', 5, 1000.00, 5000.00, '2025-05-15', 1, 'IDF'),
    ('Licence Pro', 3, 500.00, 1500.00, '2025-04-10', 4, 'Nord'),
    ('Formation', 2, 750.00, 1500.00, '2025-03-22', 2, 'Ouest'),
    ('Licence Standard', 15, 200.00, 3000.00, '2025-06-10', 3, 'Sud'),
    ('Support Premium', 2, 1000.00, 2000.00, '2025-02-14', 5, 'Est');

INSERT INTO complaints (customer_id, subject, description, status) VALUES
    (2, 'Lenteur du service', 'Le temps de réponse de la plateforme est devenu inacceptable depuis 3 semaines.', 'open'),
    (4, 'Facturation incorrecte', 'J''ai été facturé deux fois pour la même commande du mois de mars.', 'open'),
    (5, 'Manque de fonctionnalités', 'Nous avons besoin d''un export CSV que la plateforme ne propose pas encore.', 'resolved'),
    (1, 'Support réactif', 'Excellent accompagnement lors de notre migration, merci à l''équipe.', 'closed'),
    (3, 'Bug interface', 'Le tableau de bord affiche des chiffres incohérents depuis la dernière mise à jour.', 'open');

-- Index HNSW (utile après scripts/seed_embeddings.py)
CREATE INDEX IF NOT EXISTS complaints_embedding_idx
    ON complaints USING hnsw (embedding vector_cosine_ops);
