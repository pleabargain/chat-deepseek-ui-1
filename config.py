import psycopg2
import redis
from const import DB_PARAMS


def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)


# Redis Connection
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


# Save session details
def save_session(name, model):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sessions (name, model) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING RETURNING id;",
            (name, model)
        )
        session_id = cur.fetchone()
        conn.commit()
        return session_id


# Fetch session by name
def get_session(name):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, model FROM sessions WHERE name = %s;", (name,))
        return cur.fetchone()


# Save message
def save_message(session_id, role, content):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s);",
                    (session_id, role, content))
        conn.commit()


# Fetch chat history from database
def get_chat_history(session_id):
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at ASC;", (session_id,))
        return cur.fetchall()
