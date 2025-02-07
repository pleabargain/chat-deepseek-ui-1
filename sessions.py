import streamlit as st
import json
from config import save_session, get_db_connection, redis_client
from const import AVAILABLE_MODELS, DEFAULT_MODEL
from utils import logger


def initialize_session():
    """Initializes session state and loads chat history from PostgreSQL & Redis."""
    try:
        # Ensure session state variables exist
        if "messages" not in st.session_state:
            st.session_state["messages"] = {}

        if "sessions" not in st.session_state:
            st.session_state["sessions"] = {}

        # Get PostgreSQL and Redis connections
        try:
            db_conn = get_db_connection()
        except Exception as e:
            st.error("⚠️ Failed to connect to database. Please check your connection.")
            st.info("💡 Using default session settings.")
            st.session_state["sessions"] = {"Default": DEFAULT_MODEL}
            st.session_state["active_session"] = "Default"
            return

        try:
            with db_conn.cursor() as cursor:
                # Load sessions from database
                cursor.execute(
                    "SELECT name, model FROM sessions ORDER BY created_at DESC;")
                sessions = cursor.fetchall()

                st.session_state["sessions"] = {
                    name: model for name, model in sessions}

                # Ensure at least one session exists
                if not st.session_state["sessions"]:
                    default_session_name = "Default"
                    default_model = DEFAULT_MODEL
                    try:
                        cursor.execute("INSERT INTO sessions (name, model) VALUES (%s, %s) RETURNING id;",
                                   (default_session_name, default_model))
                        db_conn.commit()
                        st.session_state["sessions"] = {
                            default_session_name: default_model}
                    except Exception as e:
                        st.error("⚠️ Failed to create default session.")
                        return

                # Load active session
                if "active_session" not in st.session_state:
                    st.session_state["active_session"] = list(st.session_state["sessions"].keys())[0]

                active_session = st.session_state["active_session"]

                # Try Redis cache first
                try:
                    cached_messages = redis_client.get(f"chat:{active_session}")
                    if cached_messages:
                        try:
                            st.session_state["messages"] = {active_session: json.loads(cached_messages)}
                        except json.JSONDecodeError as e:
                            logger.error(f"Corrupted cache for session {active_session}", exc_info=True)
                            # If cache is corrupted, fall back to database
                            redis_client.delete(f"chat:{active_session}")
                            st.warning("💡 Cache corrupted, falling back to database.")
                            raise Exception("Cache corrupted")
                except Exception:
                    # If Redis fails or cache is corrupted, load from PostgreSQL
                    cursor.execute(
                        "SELECT role, content FROM messages WHERE session_id = (SELECT id FROM sessions WHERE name = %s) ORDER BY created_at;",
                        (active_session,))
                    messages = cursor.fetchall()

                    st.session_state["messages"] = {active_session: [
                        {"role": role, "content": content} for role, content in messages]}

                    # Try to update Redis cache
                    try:
                        # Ensure messages can be serialized to JSON
                        messages_json = json.dumps(st.session_state["messages"][active_session])
                        redis_client.set(f"chat:{active_session}", messages_json, ex=3600)
                    except (TypeError, json.JSONEncodeError) as e:
                        logger.error(f"Failed to serialize messages for session {active_session}", exc_info=True)
                    except Exception as e:
                        logger.error(f"Failed to update Redis cache for session {active_session}", exc_info=True)

        finally:
            db_conn.close()

    except Exception as e:
        st.error("⚠️ Error initializing session. Using default settings.")
        st.session_state["sessions"] = {"Default": DEFAULT_MODEL}
        st.session_state["active_session"] = "Default"
        st.session_state["messages"] = {"Default": []}


def create_new_session():
    """Creates a new session with a unique name."""
    try:
        # Model selection
        selected_model = st.selectbox(
            "Choose a model", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(DEFAULT_MODEL))

        session_name = st.text_input("New Session Name", key="new_session_input")
        if st.button("Create", key="create_new_session"):
            if not session_name.strip():
                st.warning("Please enter a session name.")
                return
            
            try:
                # Check if session name already exists
                with get_db_connection() as conn, conn.cursor() as cur:
                    cur.execute("SELECT name FROM sessions WHERE name = %s", (session_name.strip(),))
                    if cur.fetchone():
                        st.error("⚠️ A session with this name already exists.")
                        return

                # Save session with selected model
                save_session(session_name.strip(), selected_model)
                # Set new session as active
                st.session_state["active_session"] = session_name.strip()
                st.success("✅ Session created successfully!")
                st.rerun()  # Refresh UI to reflect changes
            except Exception as e:
                st.error("⚠️ Failed to create session. Please try again.")
                return
    except Exception as e:
        st.error("⚠️ Error in session creation interface.")
        return


def rename_session(old_name):
    """Renames an existing session."""
    try:
        if old_name == "Default":
            st.warning("Cannot rename the default session.")
            return

        new_name = st.text_input(f"Rename {old_name}", key=f"rename_{old_name}")
        if st.button("Rename", key=f"rename_btn_{old_name}"):
            if not new_name.strip():
                st.warning("Please enter a new name.")
                return

            try:
                with get_db_connection() as conn, conn.cursor() as cur:
                    # Check if new name already exists
                    cur.execute("SELECT name FROM sessions WHERE name = %s", (new_name.strip(),))
                    if cur.fetchone():
                        st.error("⚠️ A session with this name already exists.")
                        return

                    # Perform rename
                    cur.execute(
                        "UPDATE sessions SET name = %s WHERE name = %s;", (new_name.strip(), old_name))
                    conn.commit()
                    st.success("✅ Session renamed successfully!")
                    st.rerun()
            except Exception as e:
                st.error("⚠️ Failed to rename session. Please try again.")
                return
    except Exception as e:
        st.error("⚠️ Error in session rename interface.")
        return


def delete_session(session_name):
    """Deletes a session."""
    try:
        if session_name == "Default":
            st.warning("Cannot delete the default session.")
            return

        try:
            with get_db_connection() as conn, conn.cursor() as cur:
                # Delete session and its messages (cascade)
                cur.execute("DELETE FROM sessions WHERE name = %s;", (session_name,))
                conn.commit()
                
                # Clear session from state if it was active
                if st.session_state.get("active_session") == session_name:
                    st.session_state["active_session"] = "Default"
                
                st.success("✅ Session deleted successfully!")
                st.rerun()
        except Exception as e:
            st.error("⚠️ Failed to delete session. Please try again.")
            return
    except Exception as e:
        st.error("⚠️ Error in session deletion interface.")
        return


def switch_session(session_name):
    """Switches to a different session."""
    try:
        # Verify session exists
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT name FROM sessions WHERE name = %s", (session_name,))
            if not cur.fetchone():
                st.error("⚠️ Session not found.")
                return

        st.session_state["active_session"] = session_name
        st.success(f"✅ Switched to session: {session_name}")
        st.rerun()
    except Exception as e:
        st.error("⚠️ Failed to switch session. Please try again.")
        return
