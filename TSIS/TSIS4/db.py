"""db.py — PostgreSQL helpers using psycopg2."""

import psycopg2
from config import DB_CONFIG


def _conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create tables if they don't exist."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id       SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS game_sessions (
                    id            SERIAL PRIMARY KEY,
                    player_id     INTEGER REFERENCES players(id),
                    score         INTEGER   NOT NULL,
                    level_reached INTEGER   NOT NULL,
                    played_at     TIMESTAMP DEFAULT NOW()
                );
            """)
    print("[DB] Tables ready.")


def get_or_create_player(username):
    """Return player id, creating the row if needed."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) ON CONFLICT DO NOTHING",
                (username,)
            )
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            return cur.fetchone()[0]


def save_session(player_id, score, level):
    """Persist one game result."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                (player_id, score, level)
            )


def get_leaderboard():
    """Return top-10 rows: (username, score, level_reached, played_at)."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.username, gs.score, gs.level_reached,
                       TO_CHAR(gs.played_at, 'DD Mon HH24:MI') AS dt
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            return cur.fetchall()


def get_personal_best(player_id):
    """Return player's all-time best score (0 if none)."""
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                (player_id,)
            )
            return cur.fetchone()[0]
