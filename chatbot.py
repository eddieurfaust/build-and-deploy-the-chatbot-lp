"""
InfoHub Streamlit Chatbot
Interactive chatbot interface for LangChain documentation Q&A
"""

# Step 1: Setup - Import necessary modules
import json
import os

import requests
import streamlit as st

# Configure Streamlit app properties
st.set_page_config(
    page_title="InfoHub LangChain Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)


# Helper function to get backend URL from secrets or environment
def get_backend_url():
    """Get backend URL from Streamlit secrets or environment variable"""
    try:
        # Try to get from Streamlit secrets (for Streamlit Cloud)
        return st.secrets.get("BACKEND_URL", "http://localhost:8000")
    except:
        # Fallback to environment variable (for local development)
        return os.getenv("BACKEND_URL", "http://localhost:8000")


# App title and description
st.title("🤖 InfoHub LangChain Chatbot")
st.markdown("""
Welcome to the InfoHub Chatbot! Ask me anything about LangChain and I'll help you find answers
from the documentation.
""")

# Step 2: Preparing the Chat Infrastructure - Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcome message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Hello! I'm your LangChain assistant. How can I help you today?",
        }
    )

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Step 3: Define function to generate response from backend
def generate_response(user_message):
    """
    Makes an HTTP request to the LangServe backend API

    Args:
        user_message (str): The user's question

    Returns:
        str: The assistant's response
    """
    try:
        # Backend API endpoint - configurable via secrets or environment variable
        backend_url = get_backend_url()
        api_url = f"{backend_url}/chat/invoke"

        # Prepare the payload
        payload = {"input": user_message}

        # Make the POST request
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            result = response.json()
            # Extract the output from the response
            return result.get("output", "Sorry, I couldn't generate a response.")
        else:
            return (
                f"Error: Received status code {response.status_code} from the server."
            )

    except requests.exceptions.ConnectionError:
        backend_url = get_backend_url()
        return f"Error: Could not connect to the server. Please make sure the LangServe server is running on {backend_url}"
    except requests.exceptions.Timeout:
        return "Error: The request timed out. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"


# Step 3 (continued): Capture user input
if prompt := st.chat_input("Ask me anything about LangChain..."):
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Step 4: Check if we need to generate a response
    # The last message should be from the user, so we need an assistant response
    if st.session_state.messages[-1]["role"] == "user":
        # Display thinking spinner
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Generate response from the API
                response = generate_response(prompt)

            # Display the assistant's response
            st.markdown(response)

        # Step 4 (continued): Update message history with assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})

# Step 5: Continuous interaction
# Streamlit automatically reruns the script on each interaction,
# so the chat continuously listens for new input through st.chat_input
# The session state maintains the conversation history across reruns

# Add a sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This chatbot uses:
    - **LangChain** for LLM orchestration
    - **OpenAI** for embeddings and chat
    - **Chroma** for vector storage
    - **LangServe** for API deployment
    - **Streamlit** for the UI
    """)

    st.header("How to use")
    st.markdown("""
    1. Type your question in the chat input
    2. Press Enter or click Send
    3. Wait for the assistant's response
    4. Continue the conversation!
    """)

    # Add a clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your LangChain assistant. How can I help you today?",
            }
        ]
        st.rerun()

    st.markdown("---")
    st.markdown("**Server Status**")

    # Check server health
    try:
        backend_url = get_backend_url()
        health_response = requests.get(f"{backend_url}/health", timeout=2)
        if health_response.status_code == 200:
            st.success("✅ Server is running")
        else:
            st.error("❌ Server error")
    except:
        st.error("❌ Server not reachable")
