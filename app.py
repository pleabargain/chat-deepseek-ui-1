import streamlit as st
from ui import render_ui, render_chat_interface
from sessions import initialize_session

st.set_page_config(page_title="Chat DeepSeek R1", layout="wide")

def main():
    initialize_session()
    render_ui()
    render_chat_interface()

if __name__ == "__main__":
    main()
