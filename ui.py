import base64
import streamlit as st
from input_handle import handle_user_input
from const import DEFAULT_MESSAGE
from sessions import create_new_session, rename_session, delete_session, switch_session
from utils import display_chat_history, get_base64_image

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

### --- UI COMPONENTS --- ###
def display_sidebar():
    """Displays the session management UI in the sidebar."""
    with st.sidebar:
        image_base64 = get_base64_image("assets/deep-seek.png")
        st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/png;base64,{image_base64}" width="150"/>
        </div>
        """, unsafe_allow_html=True)
        st.title("💬 Chat Sessions")
        for session_name in st.session_state["sessions"]:
            col1, col2 = st.columns([1, 1])  # Session name + Menu button
            
            with col1:
                if st.button(
                    f"📁 {session_name}",
                    key=f"session_{session_name}",
                    help="Switch to this session",
                    use_container_width=True):
                        switch_session(session_name)

            with col2:
                menu_option = st.selectbox(
                    "⋮", 
                    ["Options", "✏️ Rename", "🗑 Delete"], 
                    key=f"menu_{session_name}", 
                    label_visibility="collapsed"
                )
                
                if menu_option == "✏️ Rename":
                    rename_session(session_name)
                elif menu_option == "🗑 Delete":
                    delete_session(session_name)
        
        st.markdown("---")
        create_new_session()

def display_chat():
    """Displays the chat interface for the active session."""
    display_chat_history()
    handle_user_input()
