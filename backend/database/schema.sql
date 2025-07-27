-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(128) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Table: diseases
CREATE TABLE diseases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    confidence_score NUMERIC(3,2)
);

-- Table: symptoms
CREATE TABLE symptoms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    keywords TEXT
);

-- Table: disease_symptoms
CREATE TABLE disease_symptoms (
    disease_id INTEGER NOT NULL REFERENCES diseases(id) ON DELETE CASCADE,
    symptom_id INTEGER NOT NULL REFERENCES symptoms(id) ON DELETE CASCADE,
    weight NUMERIC(3,2) NOT NULL,
    PRIMARY KEY (disease_id, symptom_id)
);

-- Table: suggestions
CREATE TABLE suggestions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    disease_id INTEGER REFERENCES diseases(id) ON DELETE CASCADE,
    is_general_advice BOOLEAN DEFAULT FALSE
);

-- Table: templates
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    template_type VARCHAR(32) NOT NULL,
    text TEXT NOT NULL,
    disease_id INTEGER REFERENCES diseases(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Table: chat_messages
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL,
    content TEXT,
    extracted_symptoms JSONB,
    recommendations JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);