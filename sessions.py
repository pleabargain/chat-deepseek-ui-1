import os
import json
import streamlit as st
from utils import save_chat_history, load_chat_history

CHAT_HISTORY_FILE = "chat_history.json"

def initialize_session():
    """Initializes session state and loads chat history."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = load_chat_history()

def save_chat_history():
    """Saves chat history to a file."""
    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(st.session_state["messages"], file)

def load_chat_history():
    """Loads chat history from a file if available."""
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as file:
            return json.load(file)
    return [{"role": "system", "content": "You are a helpful assistant."}]
