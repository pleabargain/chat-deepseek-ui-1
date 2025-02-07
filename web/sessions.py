import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"


def fetch_sessions():
    """Fetch all available sessions from FastAPI."""
    response = requests.get(f"{API_BASE_URL}/sessions")
    return response.json() if response.status_code == 200 else []


def create_session(session_name, model):
    """Create a new session via API."""
    response = requests.post(
        f"{API_BASE_URL}/session", json={"name": session_name, "model": model})
    return response.status_code == 201


def delete_session(session_name):
    """Delete a session via API."""
    response = requests.delete(f"{API_BASE_URL}/sessions/{session_name}")
    return response.status_code == 200


def switch_session(session_name):
    """Switch session in Streamlit state."""
    st.session_state["active_session"] = session_name
    # st.experimental_rerun()


def get_active_session():
    """Return the currently active session."""
    return st.session_state.get("active_session")


def manage_sessions():
    """Manage chat sessions in the sidebar."""
    with st.sidebar:
        st.title("💬 Chat Sessions")
        sessions = fetch_sessions()
        print(sessions)

        if sessions:
            session_name = st.selectbox(
                "Select a session", sessions, key="session_selector")
            if st.button("Switch Session", key="switch_session_btn"):
                switch_session(session_name)

        st.markdown("---")

        # Create new session
        new_session_name = st.text_input("New Session Name")
        model_choice = st.selectbox(
            "Choose Model", ["deepseek-r1", "deepseek-v3"])
        if st.button("Create Session"):
            if new_session_name:
                if create_session(new_session_name, model_choice):
                    st.success(f"Session '{new_session_name}' created!")
                    st.experimental_rerun()
                else:
                    st.error("Failed to create session.")
            else:
                st.warning("Enter a session name!")

        st.markdown("---")

        # Delete session
        delete_session_name = st.selectbox(
            "Delete Session", sessions, key="delete_session_selector")
        if st.button("Delete", key="delete_session_btn"):
            if delete_session(delete_session_name):
                st.success(f"Deleted session '{delete_session_name}'.")
                st.experimental_rerun()
            else:
                st.error("Failed to delete session.")
