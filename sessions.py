import streamlit as st
from config import save_session, get_session, get_db_connection, redis_client
import psycopg2
import redis
from datetime import datetime
from const import DEFAULT_MESSAGE

def initialize_session():
    """Initializes session state and loads chat history from PostgreSQL & Redis."""
    # Ensure session state variables exist
    if "messages" not in st.session_state:
        st.session_state["messages"] = {}  # Initialize an empty messages dictionary

    if "sessions" not in st.session_state:
        st.session_state["sessions"] = {}
    
    # Get PostgreSQL and Redis connections
    db_conn = get_db_connection()

    with db_conn.cursor() as cursor:
        # Load sessions from database
        cursor.execute("SELECT name, model FROM sessions ORDER BY created_at DESC;")
        sessions = cursor.fetchall()  # List of tuples [(session_name, model), ...]

        if "sessions" not in st.session_state:
            st.session_state["sessions"] = {name: model for name, model in sessions}

        # Ensure at least one session exists
        if not st.session_state["sessions"]:
            default_session_name = "Default"
            default_model = "deepseek-r1"
            cursor.execute("INSERT INTO sessions (name, model) VALUES (%s, %s) RETURNING id;", (default_session_name, default_model))
            db_conn.commit()
            st.session_state["sessions"] = {default_session_name: default_model}

        # Load active session
        if "active_session" not in st.session_state:
            st.session_state["active_session"] = list(st.session_state["sessions"].keys())[0]  # Pick first session
        
        active_session = st.session_state["active_session"]

        # Load chat history from Redis cache
        cached_messages = redis_client.get(f"chat:{active_session}")
        if cached_messages:
            st.session_state["messages"] = {active_session: eval(cached_messages)}  # Convert string back to list
        else:
            # If not cached, load from PostgreSQL
            cursor.execute("SELECT role, content FROM messages WHERE session_id = (SELECT id FROM sessions WHERE name = %s) ORDER BY created_at;", (active_session,))
            messages = cursor.fetchall()  # List of tuples [(role, content), ...]

            st.session_state["messages"] = {active_session: [{"role": role, "content": content} for role, content in messages]}

            # Store in Redis for caching
            redis_client.set(f"chat:{active_session}", str(st.session_state["messages"][active_session]), ex=3600)  # Cache for 1 hour

    db_conn.close()

def create_new_session():
    """Creates a new session with a unique name."""
    session_name = st.text_input("New Session Name", key="new_session_input")
    if st.button("Create", key="create_session"):
        save_session(session_name, "deepseek-r1")  # Default model

def rename_session(old_name):
    """Renames an existing session."""
    new_name = st.text_input(f"Rename {old_name}", key=f"rename_{old_name}")
    if st.button("Rename", key=f"rename_btn_{old_name}"):
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("UPDATE sessions SET name = %s WHERE name = %s;", (new_name, old_name))
            conn.commit()

def delete_session(session_name):
    """Deletes a session."""
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE name = %s;", (session_name,))
        conn.commit()

def switch_session(session_name):
    """Switches to a different session."""
    st.session_state["active_session"] = session_name
