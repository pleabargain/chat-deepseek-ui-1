import os
import json
import streamlit as st
from const import CHAT_HISTORY_FILE, SESSION_FILE, DEFAULT_MESSAGE
from utils import load_json_file, save_json_file, save_chat_history

# 🔹 Session management
def initialize_session():
    """Initializes session state and loads chat history."""
    
    # Load sessions from file or default to an empty list
    if "sessions" not in st.session_state:
        st.session_state["sessions"] = load_json_file(SESSION_FILE, [])

    # Ensure at least one default session exists
    if not st.session_state["sessions"]:
        st.session_state["sessions"] = ["Default"]

    # Load chat history from file or initialize an empty dictionary
    if "messages" not in st.session_state:
        st.session_state["messages"] = load_json_file(CHAT_HISTORY_FILE, {})

    # Ensure active session exists, defaulting to "Default"
    if "active_session" not in st.session_state or st.session_state["active_session"] not in st.session_state["sessions"]:
        st.session_state["active_session"] = "Default"

    # Ensure messages exist for the active session
    if st.session_state["active_session"] not in st.session_state["messages"]:
        st.session_state["messages"][st.session_state["active_session"]] = DEFAULT_MESSAGE.get("Default", [])

    # Save updates to session and chat history files
    save_json_file(SESSION_FILE, st.session_state["sessions"])
    save_json_file(CHAT_HISTORY_FILE, st.session_state["messages"])

def create_new_session():
    """Creates a new chat session with a unique name."""
    session_name = st.text_input("Enter a new session name:", key="new_session_name")
    
    if st.button("➕ Create"):
        if not session_name:
            st.warning("⚠️ Please enter a session name!")
            return
        
        if session_name in st.session_state["sessions"]:
            st.warning("⚠️ Session name already exists!")
            return

        # Add new session to session list
        st.session_state["sessions"].append(session_name)
        st.session_state["messages"][session_name] = DEFAULT_MESSAGE.get("Default", [])
        st.session_state["active_session"] = session_name

        # Save sessions and chat history
        save_json_file(SESSION_FILE, st.session_state["sessions"])
        save_json_file(CHAT_HISTORY_FILE, st.session_state["messages"])

        st.success(f"✅ Created new session: {session_name}")
        st.rerun()  # Refresh UI

def switch_session(session_name):
    """Switches to an existing chat session."""
    st.session_state["active_session"] = session_name
    st.rerun()

def delete_session(session_name):
    """Deletes a chat session."""
    if session_name in st.session_state["sessions"]:
        st.session_state["sessions"].remove(session_name)
        st.session_state["messages"].pop(session_name, None)

        if session_name == st.session_state["active_session"]:
            st.session_state["active_session"] = "Default"

        save_json_file(SESSION_FILE, st.session_state["sessions"])
        save_json_file(CHAT_HISTORY_FILE, st.session_state["messages"])
        st.rerun()
