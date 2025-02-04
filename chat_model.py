import streamlit as st
from ollama import chat, list


def get_chat_model(model_name="deepseek-r1"):
    """Returns a cached instance of the chat model based on the selected model."""

    return lambda messages: chat(model=model_name, messages=messages, stream=True)
