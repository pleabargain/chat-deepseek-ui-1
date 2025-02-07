from config import get_db_connection, redis_client


def save_session(name: str, model: str):
    """Creates a new session if it does not exist and returns its ID."""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sessions (name, model) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING RETURNING id;",
            (name, model)
        )
        session_id = cur.fetchone()
        conn.commit()
        return session_id


def get_session(name: str):
    """Fetches session ID and model based on session name."""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, model FROM sessions WHERE name = %s;", (name,))
        return cur.fetchone()


def get_all_sessions():
    """Fetches all session names."""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT name FROM sessions;")
        return [row[0] for row in cur.fetchall()]


def delete_session(name: str):
    """Deletes a session and its messages, removing it from cache."""
    session = get_session(name)
    if not session:
        return False

    session_id, _ = session

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE id = %s;", (session_id,))
        conn.commit()

    # Invalidate Redis cache for this session
    redis_client.delete(f"session:{session_id}")
    return True


def switch_session(current_name: str, new_name: str):
    """Switches to another session by name."""
    session = get_session(new_name)
    if not session:
        return None  # Session not found

    return session  # Returns (session_id, model)
