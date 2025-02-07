import streamlit as st
import requests
from sessions import get_active_session
from utils import display_message, display_assistant_message, process_stream

API_BASE_URL = "http://localhost:8000"


def fetch_chat_history(session_name):
    """Fetch chat history from FastAPI."""
    response = requests.get(f"{API_BASE_URL}/sessions/{session_name}/messages")
    return response.json() if response.status_code == 200 else []


def send_message(session_name, user_input):
    """Send a message and get assistant response."""
    response = requests.post(
        f"{API_BASE_URL}/sessions/{session_name}/messages", json={"content": user_input})
    return response.json() if response.status_code == 200 else {}


def chat_interface():
    """Chat UI and message handling."""
    active_session = get_active_session()
    if not active_session:
        st.warning(
            "⚠️ No active session selected. Please create or switch a session.")
        return

    # Display previous messages
    chat_history = fetch_chat_history(active_session)
    for msg in chat_history:
        role, content = msg["role"], msg["content"]
        display_message({"role": role, "content": content})

    # User Input
    user_input = st.chat_input("💬 Type your message here...")
    if user_input:
        display_message({"role": "user", "content": user_input})

        # Send to API
        response = send_message(active_session, user_input)

        if response:
            assistant_response = response["content"]
            display_assistant_message(assistant_response)
        else:
            st.error("Failed to get response from the assistant.")
