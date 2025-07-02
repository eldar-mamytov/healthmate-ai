CREATE TABLE diseases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.5
);

CREATE TABLE symptoms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    keywords TEXT DEFAULT ''
);

CREATE TABLE disease_symptoms (
    disease_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0,
    PRIMARY KEY (disease_id, symptom_id),
    FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(id) ON DELETE CASCADE
);

CREATE TABLE suggestions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    disease_id INTEGER,
    is_general_advice BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE SET NULL
);