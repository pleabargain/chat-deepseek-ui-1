import streamlit as st
from sessions import manage_sessions, get_active_session
from chat import chat_interface

st.set_page_config(page_title="Chat UI", layout="wide")


# Render UI Header
def render_ui():
    active_session = get_active_session()
    st.markdown(f"""
    <div style='text-align: center;'>
        <h1>🤖 Mini ChatGPT</h1>
        <h4>Session: <b>{active_session}</b> 💡</h4>
    </div>
    """, unsafe_allow_html=True)


# Sidebar: Manage Sessions
manage_sessions()

# Main Chat UI
render_ui()
chat_interface()
