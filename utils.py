import re
import os
import json
import base64
import streamlit as st
from const import CHAT_HISTORY_FILE


# 🔹 Utility functions
def get_base64_image(image_path):
    """Encodes an image as a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def clean_tags(content, tag="think"):
    """Removes specified XML-like tags from content."""
    return re.sub(fr"</?{tag}>", "", content)


def display_message(message):
    """Displays a user or assistant message in the chat interface with highlighted styling."""
    role = message["role"]
    color = "#d1e7dd" if role == "user" else "#e6f7ff"
    text_color = "#0f5132" if role == "user" else "#055160"
    border_color = "#0f5132" if role == "user" else "#055160"
    st.markdown(f"""
        <div style='background-color: {color}; color: {text_color}; padding: 10px; border-radius: 10px; border-left: 5px solid {border_color}; margin-bottom: 10px;'>
            <strong>{'👤 You' if role == 'user' else '🤖 Assistant'}:</strong><br>
            {message['content']}
        </div>
    """, unsafe_allow_html=True)


def display_assistant_message(content):
    """Handles the display of the assistant's message, including 'thinking' content."""
    think_content = re.search(r"<think>(.*?)</think>", content, re.DOTALL)
    if think_content:
        with st.expander("🤔 Thinking..."):
            st.markdown(
                f"<div style='color: #666; font-style: italic;'>{clean_tags(think_content.group(0))}</div>", unsafe_allow_html=True)
        content = content.replace(think_content.group(0), "")
    display_message({"role": "assistant", "content": content})


def load_chat_history():
    """Loads chat history from a file if available."""
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as file:
            return json.load(file)
    return [{"role": "system", "content": "You are a helpful assistant."}]

# def save_chat_history():
#     """Saves chat history to a file."""
#     with open(CHAT_HISTORY_FILE, "w") as file:
#         json.dump(st.session_state["messages"], file)


def save_chat_history():
    """Saves the chat history for the active session."""
    if "messages" in st.session_state and "active_session" in st.session_state:
        save_json_file(CHAT_HISTORY_FILE, st.session_state["messages"])


def load_json_file(filename, default_value):
    """Loads JSON data from a file, handling corruption and missing files."""
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                return data if isinstance(data, type(default_value)) else default_value
        except (json.JSONDecodeError, ValueError):
            pass  # Handle file corruption gracefully
    return default_value


def save_json_file(filename, data):
    """Saves JSON data to a file safely."""
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def display_chat_history():
    """Displays previous chat messages for the active session, excluding system messages."""
    active_session = st.session_state.get("active_session", "Default")

    # ✅ Ensure messages exist in session state
    if "messages" not in st.session_state:
        # Initialize messages as an empty dictionary
        st.session_state["messages"] = {}

    # Ensure session exists in messages
    if active_session not in st.session_state["messages"]:
        st.session_state["messages"][active_session] = []

    # Iterate over messages of the active session
    for message in st.session_state["messages"][active_session]:
        if message["role"] != "system":
            display_message(message)


def process_stream(stream, status_text):
    """Processes assistant response stream efficiently with improved UI."""
    placeholder = st.empty()
    content = ""
    with st.status(status_text, expanded=True) as status:
        for chunk in stream:
            chunk_content = chunk["message"].get("content", "")
            content += chunk_content
            placeholder.markdown(
                f"<div style='color: #666; font-style: italic;'>{clean_tags(content)}</div>", unsafe_allow_html=True)
    return content
