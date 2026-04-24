import psycopg2
from config import DB_CONFIG


def get_connection():
    """Return a new psycopg2 connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Run schema.sql and procedures.sql to set up / update the database."""
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()

    for sql_file in ("schema.sql", "procedures.sql"):
        with open(sql_file, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        print(f"[DB] Applied {sql_file}")

    cur.close()
    conn.close()