import streamlit as st
from ui import render_ui, render_chat_interface
from sessions import initialize_session

def main():
    initialize_session()
    render_ui()
    render_chat_interface()

if __name__ == "__main__":
    main()
