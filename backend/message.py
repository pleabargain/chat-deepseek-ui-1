import json
from config import get_db_connection, redis_client


def save_message(session_id: int, role: str, content: str):
    """Saves a message to the database."""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s);",
                    (session_id, role, content))
        conn.commit()

    # Invalidate Redis cache for this session
    redis_client.delete(f"session:{session_id}")


def get_chat_history(session_id: int):
    """Fetches chat history for a session, using Redis cache when available."""
    cache_key = f"session:{session_id}"
    cached_history = redis_client.get(cache_key)

    if cached_history:
        return json.loads(cached_history)

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at ASC;", (session_id,))
        chat_history = cur.fetchall()

    # Cache the retrieved history for future access
    redis_client.set(cache_key, json.dumps(chat_history),
                     ex=300)  # Cache for 5 minutes

    return chat_history
