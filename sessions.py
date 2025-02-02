import os
import json
import streamlit as st
from const import CHAT_HISTORY_FILE, DEFAULT_MESSAGE
from utils import save_chat_history, load_chat_history

def initialize_session():
    """Initializes session state and loads chat history."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = load_chat_history()

def save_chat_history():
    """Saves chat history to a file."""
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(st.session_state["messages"], file)

def load_chat_history():
    """Loads chat history from a file, handling empty or corrupt files."""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as file:
                history = json.load(file)
                return history if history else DEFAULT_MESSAGE
        except (json.JSONDecodeError, ValueError):
            pass  # If the file is corrupt, fallback to default

    return DEFAULT_MESSAGE
