import streamlit as st
from ui import render_ui, display_sidebar, display_chat
from sessions import initialize_session

st.set_page_config(page_title="Mini Chat GPT", layout="wide")

def main():
    render_ui()
    initialize_session()
    display_sidebar()
    display_chat()

if __name__ == "__main__":
    main()
