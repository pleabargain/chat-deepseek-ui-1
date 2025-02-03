import os
from dotenv import load_dotenv

CHAT_HISTORY_FILE = "chat_history.json"
SESSION_FILE = "chat_sessions.json"
DEFAULT_MESSAGE = {
    "Default": [{"role": "system", "content": "You are a helpful assistant."}]
}

# Default model and available models
DEFAULT_MODEL = "deepseek-r1"
AVAILABLE_MODELS = ["deepseek-r1", "deepseek-v3", "deepseek-coder"]

# Load environment variables from the .env file
load_dotenv()

# PostgreSQL Connection
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}