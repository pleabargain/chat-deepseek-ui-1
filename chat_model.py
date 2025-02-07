import streamlit as st
from ollama import chat, list, pull
import logging
from const import DEFAULT_MODEL

logger = logging.getLogger(__name__)

def ensure_model_available(model_name):
    """Ensures the model is available, returns True if available, False otherwise."""
    try:
        available_models = [model.model for model in list().models]
        if model_name in available_models:
            return True
            
        # Model not found, attempt to pull it
        logger.info(f"Model {model_name} not found, attempting to pull...")
        st.info(f"⌛ Pulling model {model_name}... This may take a few minutes.")
        pull(model_name)
        
        # Verify model was pulled successfully
        available_models = [model.model for model in list().models]
        return model_name in available_models
        
    except Exception as e:
        logger.error(f"Error checking/pulling model {model_name}", exc_info=True)
        return False

def get_chat_model(model_name=DEFAULT_MODEL):
    """Returns a cached instance of the chat model based on the selected model."""
    try:
        # Check if model is available
        if not ensure_model_available(model_name):
            st.error(f"⚠️ Model '{model_name}' could not be loaded.")
            available_models = [model.model for model in list().models]
            if available_models:
                st.info(f"💡 Available models: {', '.join(available_models)}")
                st.code(f"ollama pull {model_name}", language="bash")
            else:
                st.warning("⚠️ No models available. Please ensure Ollama is running and try again.")
            st.stop()
            
        # Create chat function with error handling
        def chat_with_error_handling(messages):
            try:
                return chat(model=model_name, messages=messages, stream=True)
            except Exception as e:
                logger.error(f"Error in chat model response", exc_info=True)
                raise Exception(f"Failed to get response from model: {str(e)}")
                
        return chat_with_error_handling
        
    except Exception as e:
        logger.error(f"Error initializing chat model", exc_info=True)
        st.error("⚠️ Failed to initialize chat model. Please try again.")
        st.stop()
