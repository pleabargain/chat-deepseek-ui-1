import base64
import streamlit as st
from input_handle import handle_user_input
from const import DEFAULT_MESSAGE
from sessions import create_new_session, rename_session, delete_session, switch_session
from utils import display_chat_history, get_base64_image
from config import save_session, get_session, redis_client, get_db_connection

### --- UI HEADER --- ###
def render_ui():
    """Renders the main UI header with an image and title."""
    image_base64 = get_base64_image("assets/deep-seek.png")
    st.markdown(f"""
    <div style='text-align: center;'>
        <img src="data:image/png;base64,{image_base64}" width="150"/>
        <h1>🤖 Mini ChatGPT</h1>
        <h4>With an interactive thinking UI! 💡</h4>
    </div>
    """, unsafe_allow_html=True)

### --- SIDEBAR UI COMPONENT --- ###
def display_sidebar():
    """Displays the chat session management UI in the sidebar."""
    with st.sidebar:
        render_sidebar_header()
        render_session_management()

### --- SIDEBAR HEADER --- ###
def render_sidebar_header():
    """Displays the logo and sidebar title."""
    image_base64 = get_base64_image("assets/deep-seek.png")
    st.markdown(f"""
    <div style='text-align: center;'>
        <img src="data:image/png;base64,{image_base64}" width="150"/>
    </div>
    """, unsafe_allow_html=True)
    st.title("💬 Chat Sessions")

### --- SESSION MANAGEMENT --- ###
def render_session_management():
    """Displays session switching and management options."""
    with st.sidebar:
        # Fetch sessions from database
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT name FROM sessions;")
            sessions = [row[0] for row in cur.fetchall()]

        for session_name in sessions:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if st.button(f"📁 {session_name}", key=f"session_{session_name}", help="Switch session", use_container_width=True):
                    switch_session(session_name)

            with col2:
                action = st.selectbox(
                    "⋮",
                    ["", "✏️ Rename", "🗑 Delete"],
                    key=f"menu_{session_name}",
                    label_visibility="collapsed"
                )
                
                if action == "✏️ Rename":
                    rename_session(session_name)
                elif action == "🗑 Delete":
                    delete_session(session_name)

        st.markdown("---")
        create_new_session()

### --- CHAT INTERFACE --- ###
def display_chat():
    """Displays the chat interface for the active session."""
    display_chat_history()
    handle_user_input()
