from ollama import chat

def get_chat_model():
    """Returns a cached instance of the chat model."""
    return lambda messages: chat(model="deepseek-r1", messages=messages, stream=True)
