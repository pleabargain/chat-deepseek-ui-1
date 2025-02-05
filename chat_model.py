import streamlit as st
from ollama import chat, list
from const import DEFAULT_MODEL


def get_chat_model(model_name=DEFAULT_MODEL):
    """Returns a cached instance of the chat model based on the selected model."""

    # Check available models
    available_models = [model.model for model in list().models]

    if model_name not in available_models:
        st.error(
            f"⚠️ Model '{model_name}' not found. Available models: {available_models}")
        st.code(
            f"# Please pull this model\nollama pull {model_name}", language="bash")
        st.stop()

    return lambda messages: chat(model=model_name, messages=messages, stream=True)
