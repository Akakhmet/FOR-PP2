-- ============================================================
-- PhoneBook Schema  (Practice 9 — extension of Practice 7/8)
-- ============================================================

-- Groups / categories
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT DO NOTHING;

-- Contacts (extend existing table)
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER REFERENCES groups(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add new columns if the table already exists from Practice 7/8
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS email      VARCHAR(100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS birthday   DATE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS group_id   INTEGER REFERENCES groups(id);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

-- Separate phones table (1-to-many)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);
