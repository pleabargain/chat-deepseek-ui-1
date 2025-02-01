import streamlit as st
from chat_model import get_chat_model
from utils import process_stream, display_assistant_message, display_message
from sessions import save_chat_history

def handle_user_input():
    """Handles user input and generates the assistant's response."""
    user_input = st.chat_input("💬 Type your message here...")
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        display_message({"role": "user", "content": user_input})
        save_chat_history()  # Save after user input
        
        with st.chat_message("assistant"):
            chat_model = get_chat_model()
            stream = chat_model(st.session_state["messages"])
            thinking_content = process_stream(stream, "🤔 Thinking...")
            response_content = process_stream(stream, "💡 Responding...")
            full_response = thinking_content + response_content
            st.session_state["messages"].append({"role": "assistant", "content": full_response})
            display_assistant_message(full_response)
            save_chat_history()  # Save after assistant response
