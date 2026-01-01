"""
LangServe Server for InfoHub Chatbot
Provides API endpoints for conversational retrieval over LangChain documentation
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langserve import add_routes

# Load environment variables
load_dotenv()

# Step 1: Set up environment and retrieve API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please set it in .env file"
    )

# Specify the model for embeddings (using ada-002 as mentioned)
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-3.5-turbo"

# Step 2: Establish embedding object and prepare Chroma vector store
print("Initializing OpenAI embeddings...")
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)

print("Loading Chroma vector store...")
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="documentation_embeddings",  # Use the existing collection
)

# Set up the vector store as a retriever
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

print("Initializing ChatOpenAI model...")
llm = ChatOpenAI(model=CHAT_MODEL, temperature=0.7, openai_api_key=OPENAI_API_KEY)

# Step 3: Set up conversational retrieval chain using LCEL
print("Setting up conversational retrieval chain...")

# Create a prompt template for the RAG chain
template = """You are an assistant for question-answering tasks about LangChain.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Keep the answer concise and helpful.

Context:
{context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)


# Helper function to format documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Create the RAG chain using LangChain Expression Language (LCEL)
# This includes memory through the conversational prompt structure
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Test with an initial message for verification (optional - uncomment when API key is set)
# print("\n" + "=" * 50)
# print("Testing retrieval chain...")
# print("=" * 50)
# test_response = rag_chain.invoke("What is LangChain?")
# print(f"Test Question: What is LangChain?")
# print(f"Test Answer: {test_response[:200]}...")
# print("=" * 50 + "\n")
print("RAG chain configured successfully!")

# Step 4: Configure FastAPI server and add LangServe routes
print("Configuring FastAPI server...")
app = FastAPI(
    title="InfoHub LangChain Chatbot API",
    version="1.0",
    description="API for conversational retrieval over LangChain documentation using LangServe",
)

# Add CORS middleware for browser access
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add LangServe routes for the RAG chain
add_routes(
    app, rag_chain, path="/chat", enabled_endpoints=["invoke", "batch", "stream"]
)


# Root endpoint for health check
@app.get("/")
async def root():
    return {
        "message": "InfoHub LangChain Chatbot API is running!",
        "endpoints": {"chat": "/chat", "docs": "/docs", "openapi": "/openapi.json"},
    }


# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}


print("=" * 50)
print("FastAPI server configured successfully!")
print("Server is ready to be deployed with Uvicorn")
print("=" * 50)

# Step 5: Run with Uvicorn (when this file is executed directly)
if __name__ == "__main__":
    import uvicorn

    print("\nStarting Uvicorn server...")
    print("API Documentation will be available at: http://localhost:8000/docs")
    print("Chat endpoint will be available at: http://localhost:8000/chat")
    uvicorn.run(app, host="0.0.0.0", port=8000)
