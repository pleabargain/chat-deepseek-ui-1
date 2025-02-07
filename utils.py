import logging
from datetime import datetime
import os
import base64
import streamlit as st

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging with UTF-8 encoding
def setup_logging():
    # Get current date for log file name
    current_date = datetime.utcnow().strftime('%Y-%m-%d')
    log_file = f'logs/error_{current_date}.log'
    
    # Configure logging format
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s.%(msecs)03dZ] [%(levelname)s] %(message)s\n%(pathname)s:%(lineno)d\n%(exc_info)s\n---\n',
        datefmt='%Y-%m-%dT%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8', mode='a'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

def get_base64_image(image_path):
    """Convert an image to base64 string."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logger.error(f"Failed to convert image to base64: {image_path}", exc_info=True)
        return ""

def process_stream(stream, status_text="Processing..."):
    """Process a streaming response with a status indicator."""
    try:
        message_placeholder = st.empty()
        full_response = ""
        
        # Display status with spinner
        with st.spinner(status_text):
            for chunk in stream:
                if not chunk:
                    logger.warning("Received empty chunk in stream")
                    continue
                    
                # Log chunk structure for debugging
                logger.info(f"Chunk structure: {chunk.__dict__}")
                
                # Handle different response formats
                chunk_content = None
                if hasattr(chunk, 'message') and chunk.message:
                    chunk_content = chunk.message.content
                elif hasattr(chunk, 'content'):
                    chunk_content = chunk.content
                elif isinstance(chunk, dict):
                    chunk_content = chunk.get('content', '')
                elif isinstance(chunk, str):
                    chunk_content = chunk
                
                if chunk_content:
                    full_response += chunk_content
                    message_placeholder.markdown(full_response + "▌")
                else:
                    logger.warning(f"Could not extract content from chunk: {chunk}")
            
            # Final update without cursor
            if full_response:
                # Clean up any <think> tags from the response
                cleaned_response = full_response.replace('<think>', '').replace('</think>', '')
                message_placeholder.markdown(cleaned_response)
                return cleaned_response
            else:
                logger.error("No content was extracted from the stream")
                st.error("⚠️ No response content received")
                return ""
                
    except Exception as e:
        logger.error("Failed to process stream response", exc_info=True)
        st.error("⚠️ Error processing response")
        return ""

def display_message(message):
    """Display a chat message with proper formatting."""
    try:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    except Exception as e:
        logger.error(f"Failed to display message: {message}", exc_info=True)
        st.error("⚠️ Error displaying message")

def display_assistant_message(content):
    """Display an assistant message with proper formatting."""
    try:
        st.markdown(content)
    except Exception as e:
        logger.error(f"Failed to display assistant message", exc_info=True)
        st.error("⚠️ Error displaying assistant message")

def display_chat_history():
    """Display the chat history from the session state."""
    try:
        if "messages" in st.session_state:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    except Exception as e:
        logger.error("Failed to display chat history", exc_info=True)
        st.error("⚠️ Error displaying chat history")
