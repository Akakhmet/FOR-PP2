-- ============================================================
-- PhoneBook Stored Procedures — TSIS 1
-- (Practices 7-8 procedures are NOT duplicated here)
-- ============================================================

-- ------------------------------------------------------------
-- 1. add_phone(contact_name, phone, type)
--    Adds a new phone number to an existing contact.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || COALESCE(last_name, '')) ILIKE p_contact_name
    LIMIT 1;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home / work / mobile.', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact id=%.', p_phone, p_type, v_id;
END;
$$;


-- ------------------------------------------------------------
-- 2. move_to_group(contact_name, group_name)
--    Moves a contact to a group; creates the group if needed.
-- ------------------------------------------------------------
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Resolve contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || COALESCE(last_name, '')) ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Resolve or create group
    SELECT id INTO v_group_id FROM groups WHERE name ILIKE p_group_name LIMIT 1;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created (id=%).', p_group_name, v_group_id;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    RAISE NOTICE 'Contact id=% moved to group "%" (id=%).', v_contact_id, p_group_name, v_group_id;
END;
$$;


-- ------------------------------------------------------------
-- 3. search_contacts(query)
--    Full-text pattern search across: first_name, last_name,
--    email, and ALL phone numbers in the phones table.
--    Returns a deduplicated list of matching contacts.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones_agg TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name                                   AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
                                                 AS phones_agg
    FROM contacts c
    LEFT JOIN groups g  ON g.id = c.group_id
    LEFT JOIN phones p  ON p.contact_id = c.id
    WHERE
        c.first_name ILIKE '%' || p_query || '%'
        OR COALESCE(c.last_name, '') ILIKE '%' || p_query || '%'
        OR COALESCE(c.email, '')     ILIKE '%' || p_query || '%'
        OR p.phone                   ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
    ORDER BY c.first_name, c.last_name;
END;
$$;


-- ------------------------------------------------------------
-- 4. Paginated listing (used by console navigation loop)
--    Returns contacts sorted by chosen column with LIMIT/OFFSET.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_sort   VARCHAR DEFAULT 'first_name',   -- 'first_name' | 'birthday' | 'created_at'
    p_limit  INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones_agg TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Whitelist sort columns to prevent SQL injection
    IF p_sort NOT IN ('first_name', 'birthday', 'created_at') THEN
        p_sort := 'first_name';
    END IF;

    RETURN QUERY EXECUTE format(
        'SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                g.name AS group_name,
                STRING_AGG(p.phone || '' ('' || COALESCE(p.type,''?'') || '')'', '', '') AS phones_agg
         FROM contacts c
         LEFT JOIN groups g ON g.id = c.group_id
         LEFT JOIN phones p ON p.contact_id = c.id
         GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name,
                  c.created_at
         ORDER BY %I NULLS LAST
         LIMIT %L OFFSET %L',
        p_sort, p_limit, p_offset
    );
END;
$$;