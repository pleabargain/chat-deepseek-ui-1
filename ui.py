import streamlit as st
from utils import logger, display_chat_history, get_base64_image

# Import other modules with error handling
try:
    from input_handle import handle_user_input
    from sessions import create_new_session, rename_session, delete_session, switch_session
    from config import get_db_connection
except ImportError as e:
    logger.error("Failed to import required modules", exc_info=True)
    st.error("⚠️ Failed to load required modules. Please check the error logs.")
    raise


def render_ui():
    """Renders the main UI header with an image and title."""
    try:
        session_name = st.session_state.get("active_session", "Default")
        image_base64 = get_base64_image("assets/deep-seek.png")

        st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <img src="data:image/png;base64,{image_base64}" width="120" style="margin-bottom: 10px;"/>
            <h1 style="color: #333; margin-bottom: 5px;">🤖 Mini ChatGPT</h1>
            <h4 style="color: #666; font-weight: normal;">💬 Session: <span style="color: #0078FF;">{session_name}</span></h4>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        logger.error("Failed to render UI header", exc_info=True)
        st.error("⚠️ Error rendering UI header")


def display_sidebar():
    """Displays the chat session management UI in the sidebar."""
    try:
        with st.sidebar:
            render_sidebar_header()
            render_session_management()
    except Exception as e:
        logger.error("Failed to display sidebar", exc_info=True)
        st.error("⚠️ Error displaying sidebar")


def render_sidebar_header():
    """Displays the logo and sidebar title."""
    try:
        image_base64 = get_base64_image("assets/deep-seek.png")
        st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/png;base64,{image_base64}" width="150"/>
        </div>
        """, unsafe_allow_html=True)
        st.title("💬 Chat Sessions")
    except Exception as e:
        logger.error("Failed to render sidebar header", exc_info=True)
        st.error("⚠️ Error rendering sidebar header")


def render_session_management():
    """Displays session switching and management options."""
    try:
        with st.sidebar:
            # Fetch sessions from database
            try:
                with get_db_connection() as conn, conn.cursor() as cur:
                    cur.execute("SELECT name FROM sessions;")
                    sessions = [row[0] for row in cur.fetchall()]
            except Exception as e:
                logger.error("Failed to fetch sessions from database", exc_info=True)
                st.error("⚠️ Database connection error. Please check if the database is running.")
                st.info("💡 Tip: Try restarting the Docker containers with 'docker-compose down && docker-compose up -d'")
                # Provide a default session if database is unavailable
                sessions = ["Default"]

            for session_name in sessions:
                try:
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
                except Exception as e:
                    logger.error(f"Failed to render session {session_name}", exc_info=True)
                    st.error(f"⚠️ Error displaying session {session_name}")

            st.markdown("---")
            create_new_session()
    except Exception as e:
        logger.error("Failed to render session management", exc_info=True)
        st.error("⚠️ Error managing sessions")


def display_chat():
    """Displays the chat interface for the active session."""
    try:
        display_chat_history()
        handle_user_input()
    except Exception as e:
        logger.error("Failed to display chat interface", exc_info=True)
        if "OperationalError" in str(e):
            st.error("⚠️ Database connection error. Unable to load chat history.")
            st.info("💡 Tip: Check if the database is running and properly configured.")
            # Display a helpful message about database configuration
            st.markdown("""
            **Troubleshooting Steps:**
            1. Verify Docker containers are running
            2. Check database credentials in .env file
            3. Ensure PostgreSQL is accepting connections
            """)
        else:
            st.error("⚠️ Error displaying chat interface. Please check the error logs.")
