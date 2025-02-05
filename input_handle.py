import streamlit as st
import json
from config import get_session, save_message, get_chat_history, redis_client
from chat_model import get_chat_model
from utils import process_stream, display_assistant_message, display_message


def handle_user_input():
    """Handles user input and generates the assistant's response."""

    # Get active session (default to "Default")
    active_session = st.session_state.get("active_session", "Default")

    # Ensure session exists in DB, else create it
    session = get_session(active_session)

    if session:
        session_id, selected_model = session  # Session exists, use stored model
    else:
        # If session doesn't exist, force user to create a new one
        st.error("⚠️ This session does not exist. Please create a new session.")
        st.stop()

    # Fetch chat history (cache first, then fallback to database)
    cache_key = f"session:{session_id}"
    cached_history = redis_client.get(cache_key)

    if cached_history:
        chat_history = json.loads(cached_history)
    else:
        chat_history = get_chat_history(session_id)
        redis_client.set(cache_key, json.dumps(chat_history),
                         ex=300)  # Cache for 5 minutes

    # 🛠 Ensure messages are properly formatted before sending to chat model
    formatted_chat_history = [
        {"role": msg[0], "content": msg[1]} for msg in chat_history]

    # Display chat history
    for msg in formatted_chat_history:
        display_message(msg)

    # Get user input
    user_input = st.chat_input("💬 Type your message here...")

    if user_input:
        # Save user input
        display_message({"role": "user", "content": user_input})
        save_message(session_id, "user", user_input)

        # Invalidate cache (only once, after saving)
        redis_client.delete(cache_key)

        # Generate response
        with st.chat_message("assistant"):
            chat_model = get_chat_model(model_name=selected_model)

            # 🛠 FIX: Pass correctly formatted history to the chat model
            stream = chat_model(formatted_chat_history +
                                [{"role": "user", "content": user_input}])

            response_content = process_stream(stream, "💡 Responding...")

            # Display & save assistant response
            display_assistant_message(response_content)
            save_message(session_id, "assistant", response_content)

            # Refresh cache
            redis_client.delete(cache_key)
