## Chat deepseek UI
A simple web-based chat interface powered by Ollama's deep-seek model.
This tool provides an interactive, real-time chatting experience with the
assistant, using Streamlit for the frontend. The assistant processes and streams
responses back to the user, ensuring a seamless and engaging interaction.

![](./assets/demo.png)

## Features
- **Real-time Chat Interface**: Allows for dynamic interaction with the assistant.
- **Persistent Chat History**: Maintains chat history between sessions.
- **Save & Load Chat History**: Automatically saves chat history to a JSON file for persistent conversations.

### Setup

Install [ollama](https://ollama.com/download)

Pull deepseek-r1 model

```sh
ollama pull deepseek-r1 
```

Clone repo
```sh
git clone https://github.com/ductnn/chat-deepseek-ui.git
cd chat-deepseek-ui
```

Build postgres database and redis:
```sh
# Use docker-compose
docker-compose up -d
```

Install required packages:
```sh
pip install streamlit ollama
```

If you still get build errors in package `pyarrow`, try installing `pyarrow`
as a binary:
```sh
pip install --only-binary=:all: pyarrow
```

Create file `.env`, or copy from `.env.example` and fill in your database credentials:
```sh
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=localhost
DB_PORT=5432
```

Run the app:
```sh
streamlit run app.py
```
