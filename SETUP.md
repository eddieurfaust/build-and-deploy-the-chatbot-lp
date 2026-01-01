# InfoHub LangChain Chatbot - Setup Guide

## Overview

This project consists of two components:
1. **LangServe Backend API** (`server.py`) - Provides LLM-powered Q&A via REST API
2. **Streamlit Chatbot UI** (`chatbot.py`) - Interactive chat interface

## Prerequisites

- Python 3.10+
- OpenAI API Key
- Existing Chroma vector database in `./chroma_db/`

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure OpenAI API Key:**
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

### Step 1: Start the LangServe Backend

```bash
python server.py
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Step 2: Start the Streamlit Chatbot

In a new terminal:
```bash
streamlit run chatbot.py
```

The chatbot will be available at:
- Local: http://localhost:8501

## Usage

1. Open http://localhost:8501 in your browser
2. Type your question about LangChain in the chat input
3. Press Enter to send
4. Wait for the AI assistant's response
5. Continue the conversation!

## Features

- ✅ Question-answering about LangChain documentation
- ✅ Conversational interface with chat history
- ✅ Real-time responses from OpenAI GPT-3.5-turbo
- ✅ Vector similarity search using Chroma
- ✅ Server health monitoring
- ✅ Clear chat history option

## Architecture

```
User → Streamlit UI (chatbot.py) → HTTP Request → LangServe API (server.py)
                                                        ↓
                                                   OpenAI API
                                                        ↓
                                                   Chroma DB
```

## API Endpoints

### LangServe Backend

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /chat/invoke` - Chat completion endpoint

**Example Request:**
```bash
curl -X POST http://localhost:8000/chat/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "What is LangChain?"}'
```

## Troubleshooting

**Server not connecting:**
- Ensure the LangServe backend is running on port 8000
- Check `server.log` for errors

**OpenAI API errors:**
- Verify your API key is set correctly in `.env`
- Check your OpenAI account has sufficient quota

**Import errors:**
- Run `pip install -r requirements.txt` again
- Ensure you're using Python 3.10+

## Project Structure

```
.
├── server.py           # LangServe backend API
├── chatbot.py          # Streamlit chatbot UI
├── requirements.txt    # Python dependencies
├── .env               # OpenAI API key (not in git)
├── .gitignore         # Git ignore rules
├── chroma_db/         # Vector database
└── README.md          # Project documentation
```
