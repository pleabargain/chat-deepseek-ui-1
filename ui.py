import base64
import streamlit as st
from input_handle import handle_user_input
from utils import display_message, display_assistant_message, display_chat_history, get_base64_image

def render_ui():
    """Renders the UI header with an image and title."""
    image_base64 = get_base64_image("assets/deep-seek.png")
    st.markdown(f"""
    <div style='text-align: center;'>
        <img src="data:image/png;base64,{image_base64}" width="150"/>
        <h1>🤖 Mini ChatGPT</h1>
        <h4>With an interactive thinking UI! 💡</h4>
    </div>
    """, unsafe_allow_html=True)

def render_chat_interface():
    """Displays chat history and handles user input."""
    display_chat_history()
    handle_user_input()
