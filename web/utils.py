import streamlit as st


def display_message(message):
    """Display a chat message."""
    role = message["role"]
    content = message["content"]

    with st.chat_message(role):
        st.markdown(content)


def display_assistant_message(content):
    """Display assistant's response."""
    with st.chat_message("assistant"):
        st.markdown(content)


def process_stream(stream, placeholder_text):
    """Process streaming response (if applicable)."""
    response_content = ""
    placeholder = st.empty()
    for chunk in stream:
        response_content += chunk
        placeholder.markdown(f"**{placeholder_text}**\n\n{response_content}")
    return response_content
