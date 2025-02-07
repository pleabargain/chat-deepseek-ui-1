import streamlit as st
import json
import logging
from config import get_session, save_message, get_chat_history, redis_client
from chat_model import get_chat_model
from utils import process_stream, display_assistant_message, display_message

logger = logging.getLogger(__name__)


def handle_user_input():
    """Handles user input and generates the assistant's response."""

    # Get active session (default to "Default")
    active_session = st.session_state.get("active_session", "Default")

    # Initialize variables
    session_id = None
    selected_model = None
    chat_history = []
    cache_key = None

    try:
        # Ensure session exists in DB, else create it
        session = get_session(active_session)

        if session:
            session_id, selected_model = session  # Session exists, use stored model
        else:
            # If session doesn't exist, show message and return
            st.warning("⚠️ Please create a new session to start chatting.")
            st.info("💡 Click 'Create' in the sidebar to create a new session.")
            return

        # Fetch chat history (cache first, then fallback to database)
        cache_key = f"session:{session_id}"
        cached_history = redis_client.get(cache_key)

        if cached_history:
            chat_history = json.loads(cached_history)
        else:
            chat_history = get_chat_history(session_id)
            redis_client.set(cache_key, json.dumps(chat_history),
                         ex=300)  # Cache for 5 minutes

    except Exception as e:
        st.error("⚠️ Error loading session or chat history. Please try again.")
        st.info("💡 If the problem persists, try creating a new session.")
        return

    # 🛠 Ensure messages are properly formatted before sending to chat model
    formatted_chat_history = []
    for msg in chat_history:
        content = msg[1]
        # Clean up any <think> tags from previous responses
        if msg[0] == "assistant":
            content = content.replace('<think>', '').replace('</think>', '')
        formatted_chat_history.append({"role": msg[0], "content": content})

    # Display chat history
    for msg in formatted_chat_history:
        display_message(msg)

    # Get user input
    user_input = st.chat_input("💬 Type your message here...")

    if user_input:
        try:
            # Save user input
            display_message({"role": "user", "content": user_input})
            save_message(session_id, "user", user_input)

            # Invalidate cache (only once, after saving)
            if cache_key:
                redis_client.delete(cache_key)

            # Generate response
            with st.chat_message("assistant"):
                try:
                    # Get chat model with error handling
                    chat_model = get_chat_model(model_name=selected_model)
                    
                    # Prepare messages with system context
                    messages = formatted_chat_history + [{"role": "user", "content": user_input}]
                    
                    # Log the messages being sent
                    logger.info(f"Sending messages to model: {messages}")
                    
                    try:
                        # Get streaming response
                        stream = chat_model(messages)
                        
                        # Process stream with status indicator
                        response_content = process_stream(stream, "💡 Responding...")
                        
                        if not response_content:
                            logger.error("Empty response from model")
                            st.error("⚠️ No response received from the model.")
                            st.info("💡 Please try again or select a different model.")
                            return
                            
                        # Display & save assistant response
                        display_assistant_message(response_content)
                        save_message(session_id, "assistant", response_content)
                        
                        # Refresh cache
                        if cache_key:
                            redis_client.delete(cache_key)
                            
                    except Exception as e:
                        logger.error("Error in model response", exc_info=True)
                        st.error(f"⚠️ Error getting model response: {str(e)}")
                        st.info("💡 Please check if Ollama is running and the model is available.")
                        return

                except Exception as e:
                    logger.error("Error in chat session", exc_info=True)
                    st.error("⚠️ Error in chat session. Please try again.")
                    st.info("💡 If the problem persists, try creating a new session.")
                    return

        except Exception as e:
            st.error("⚠️ Error processing your message. Please try again.")
            return
