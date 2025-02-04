import sys
import os

# Agregar el directorio raíz al path de Python para permitir importaciones entre subdirectorios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '')))

import streamlit as st
from llama_index.core.llms import ChatMessage
import logging
import time
from llama_index.llms.ollama import Ollama
import sqlite3
from api.create_db import init_db
import json

logging.basicConfig(level=logging.INFO)

init_db()

def load_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

config = load_config()

# Initialize chat history in session state if not already present
if 'messages' not in st.session_state:
    st.session_state.messages = []

def add_message(user, message):
    conn = sqlite3.connect(config['database_path'])
    c = conn.cursor()
    c.execute("INSERT INTO messages (user, message) VALUES (?, ?)", (user, message))
    conn.commit()
    conn.close()

def get_messages(limit=4,all=True):
    conn = sqlite3.connect(config['database_path'])
    c = conn.cursor()
    if all:
        c.execute("SELECT timestamp, user, message FROM messages ORDER BY id DESC")
    else:
        c.execute("SELECT timestamp, user, message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    # Convertir las tuplas a diccionarios
    messages = [{'timestamp': row[0], 'user': row[1], 'message': row[2]} for row in rows]
    return messages[::-1]

# Function to stream chat response based on selected model
def stream_chat(model, messages):
    try:
        # Initialize the language model with a timeout
        llm = Ollama(model=model, request_timeout=120.0) 
        # Stream chat responses from the model
        resp = llm.stream_chat(messages)
        response = ""
        response_placeholder = st.empty()
        # Append each piece of the response to the output
        for r in resp:
            response += r.delta
            response_placeholder.write(response)
        # Log the interaction details
        logging.info(f"Model: {model}, Messages: {messages}, Response: {response}")
        return response
    except Exception as e:
        # Log and re-raise any errors that occur
        logging.error(f"Error during streaming: {str(e)}")
        raise e
    
def main():
    st.title("JosMan Chat")  # Set the title of the Streamlit app
    logging.info("App started")  # Log that the app has started

    messages = get_messages()
    for message in messages:
        with st.chat_message(message['user']):
            st.write(f"{message['message']}")

    # Sidebar for model selection
    model = st.sidebar.selectbox("Choose a model", ["phi", "llama3", "mistral"])
    logging.info(f"Model selected: {model}")

    # Prompt for user input and save to chat history
    if prompt := st.chat_input("Your question"):
        add_message("user",prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        logging.info(f"User input: {prompt}")

        # Display the user's query
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Generate a new response if the last message is not from the assistant
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                start_time = time.time()  # Start timing the response generation
                logging.info("Generating response")

                with st.spinner("Writing..."):
                    try:
                        # Update promt including context from 3 last messages
                        context_messages = get_messages(limit=4,all=False)
                        # Prepare messages for the LLM and stream the response
                        messages = [ChatMessage(role=msg["user"], content=msg["message"]) for msg in context_messages] #st.session_state.messages]
                        response_message = stream_chat(model, messages)
                        add_message("assistant",response_message)
                        duration = time.time() - start_time  # Calculate the duration
                        response_message_with_duration = f"{response_message}\n\nDuration: {duration:.2f} seconds"
                        st.session_state.messages.append({"role": "assistant", "content": response_message_with_duration})
                        st.write(f"Duration: {duration:.2f} seconds")
                        logging.info(f"Response: {response_message}, Duration: {duration:.2f} s")

                    except Exception as e:
                        # Handle errors and display an error message
                        st.session_state.messages.append({"role": "assistant", "content": str(e)})
                        st.error("An error occurred while generating the response.")
                        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()