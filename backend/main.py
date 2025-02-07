from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from session import save_session, get_session, get_all_sessions, delete_session, switch_session
from message import save_message, get_chat_history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages FastAPI startup and shutdown."""
    yield  # Run application
    # Perform cleanup if needed

app = FastAPI(lifespan=lifespan)


@app.post("/session/")
def create_session(name: str, model: str):
    """Creates a new chat session."""
    session_id = save_session(name, model)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session already exists")
    return {"session_id": session_id, "name": name, "model": model}


@app.get("/session/{name}")
def fetch_session(name: str):
    """Fetches a session by name."""
    session = get_session(name)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session[0], "model": session[1]}


@app.get("/sessions/")
def list_sessions():
    """Lists all available chat sessions."""
    return {"sessions": get_all_sessions()}


@app.delete("/session/{name}")
def remove_session(name: str):
    """Deletes a session by name."""
    if delete_session(name):
        return {"message": f"Session '{name}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.post("/session/{current_name}/switch/{new_name}")
def change_session(current_name: str, new_name: str):
    """Switches from one session to another."""
    new_session = switch_session(current_name, new_name)
    if not new_session:
        raise HTTPException(status_code=404, detail="Target session not found")
    return {"session_id": new_session[0], "model": new_session[1]}


@app.post("/message/{session_id}")
def add_message(session_id: int, role: str, content: str):
    """Adds a message to the session's chat history."""
    save_message(session_id, role, content)
    return {"message": "Message saved successfully"}


@app.get("/history/{session_id}")
def fetch_chat_history(session_id: int):
    """Fetches the chat history for a session."""
    history = get_chat_history(session_id)
    return {"history": history}
