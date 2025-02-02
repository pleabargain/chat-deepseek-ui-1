import streamlit as st
from ui import render_ui, render_chat_interface, display_sidebar, display_chat
from sessions import initialize_session

st.set_page_config(page_title="Chat DeepSeek R1", layout="wide")

def main():
    render_ui()
    initialize_session()
    display_sidebar()
    display_chat()
    # render_ui()
    # render_chat_interface()

if __name__ == "__main__":
    main()
