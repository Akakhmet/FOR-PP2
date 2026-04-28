
-- 1. Add a phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE name = p_contact_name LIMIT 1;
    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
END;
$$;

-- 2. Move a contact to a group (creates group if missing)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name LIMIT 1;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    -- Create group if it doesn't exist
    INSERT INTO groups (name) VALUES (p_group_name) ON CONFLICT DO NOTHING;
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

-- 3. Extended search: name, email, and all phone numbers
DROP FUNCTION IF EXISTS search_contacts(TEXT);
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id       INTEGER,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS grp
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.name  ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.phone ILIKE '%' || p_query || '%';
END;
$$;
