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

Install required packages:
```sh
pip install streamlit ollama
```

If you still get build errors in package `pyarrow`, try installing `pyarrow`
as a binary:
```sh
pip install --only-binary=:all: pyarrow
```

Run the app:
```sh
streamlit run app.py
```
