import streamlit as st
import json
from config import save_session, get_session, save_message, get_chat_history, redis_client
from chat_model import get_chat_model
from const import AVAILABLE_MODELS, DEFAULT_MODEL
from utils import process_stream, display_assistant_message, display_message

def handle_user_input():
    """Handles user input and generates the assistant's response."""
    # Get active session or create a new one
    active_session = st.session_state.get("active_session", "Default")

    # Model selection
    selected_model = st.selectbox("Choose a model", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(DEFAULT_MODEL))

    # Check if session exists
    session = get_session(active_session)
    if session:
        session_id, current_model = session
        if current_model != selected_model:
            st.warning("Switching models requires a new session.")
            st.stop()
    else:
        session_id = save_session(active_session, selected_model)

    # Fetch chat history (cache first, then database)
    cached_history = redis_client.get(f"session:{active_session}")
    if cached_history:
        chat_history = json.loads(cached_history)
    else:
        chat_history = get_chat_history(session_id)
        redis_client.set(f"session:{active_session}", json.dumps(chat_history), ex=300)  # Cache for 5 minutes

    # Display chat history
    for msg in chat_history:
        display_message({"role": msg[0], "content": msg[1]})

    # Get user input
    user_input = st.chat_input("💬 Type your message here...")
    if user_input:
        display_message({"role": "user", "content": user_input})
        save_message(session_id, "user", user_input)
        redis_client.delete(f"session:{active_session}")  # Invalidate cache

        with st.chat_message("assistant"):
            chat_model = get_chat_model(model_name=selected_model)
            stream = chat_model(chat_history + [{"role": "user", "content": user_input}])
            response_content = process_stream(stream, "💡 Responding...")
            
            display_assistant_message(response_content)
            save_message(session_id, "assistant", response_content)
            redis_client.delete(f"session:{active_session}")  # Invalidate cache
