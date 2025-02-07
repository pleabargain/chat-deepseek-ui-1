import streamlit as st
from ui import render_ui, display_sidebar, display_chat
from utils import logger
from streamlit.runtime.scriptrunner.script_runner import StopException

st.set_page_config(page_title="Mini Chat GPT", layout="wide")

def main():
    try:
        render_ui()
        display_sidebar()
        display_chat()
    except StopException:
        # This is a normal Streamlit control flow mechanism, not an error
        pass
    except Exception as e:
        logger.error("Uncaught application error", exc_info=True)
        st.error("⚠️ An unexpected error occurred. Please check the error logs for details.")
        st.info("💡 Try refreshing the page or creating a new session.")

if __name__ == "__main__":
    try:
        main()
    except StopException:
        # Normal Streamlit control flow
        pass
    except Exception as e:
        # This catch-all handler ensures we log any errors that might occur
        # during the main function execution
        logger.error("Fatal application error", exc_info=True)
        st.error("⚠️ A fatal error occurred. Please check the error logs for details.")
        st.info("💡 Try restarting the application.")
