# PDF-Query-Bot

A lightweight Retrieval-Augmented Generation (RAG) chatbot designed for querying PDF documents using Gemini models. This project allows users to upload a PDF, receive a unique session ID, and engage in a stateful conversation with the document via RESTful API endpoints.

## Features

* **PDF to RAG**: Converts uploaded PDFs to a Chroma vector store using Gemini embeddings.
* **Session-Based Chat**: In-memory session management with conversation history.
* **LangGraph Pipeline**: A structured Retrieve → Answer workflow with ephemeral memory.
* **Gemini 2.5 Flash**: Fast, context-aware responses without the need for local LLMs.
* **Simple API**: Dedicated endpoints for `/upload_pdf`, `/chat`, and `/reset`.
* **Streamlit UI**: A clean frontend interface for testing and interaction.

---

## Quick Start

### Prerequisites

Ensure you have Python installed, then install the required dependencies:

```bash
pip install streamlit fastapi python-multipart python-dotenv langchain-google-genai langgraph chromadb pypdf
```
# 1. Setup Environment
Create a .env file from the example and add your API key:

```bash
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

# 2. Run Backend
Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

3. Run Frontend
Start the Streamlit application:

```bash
streamlit run frontend.py
```
Visit http://localhost:8501 to start querying your documents.

# API Usage
## 1. Upload PDF
Endpoint: POST /upload_pdf

```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/upload_pdf
```
Returns: {"session_id": 123456, "message": "PDF processed successfully."}

## 2. Chat
Endpoint: POST /chat

```bash
curl -X POST "http://localhost:8000/chat" \
  -d "session_id=123456" \
  -d "query=What is the main topic?"
```

## 3. Reset Session
Endpoint: POST /reset

```bash
curl -X POST "http://localhost:8000/reset" -d "session_id=123456"
```

# How It Works

1. **Ingestion:** Uploaded PDFs are split into chunks (1200 characters with 150-character overlap) and stored in a Chroma vector store.
2. **Session Management:** A session is created in the SESSIONS dictionary, storing the database instance, the LangGraph workflow, and message history.
3. **Chat Flow:** 
    **Query:** User sends a prompt.retrieve_context(): Performs a vector search ($k=4$) to find relevant document sections.
    **answer_query():** Gemini 2.5 Flash generates a response using the context and history.
4. **State Management:** LangGraph preserves the conversation state across multiple turns.

# Configuration

## Session Management
**In-Memory:** The SESSIONS = {} dictionary resets whenever the server restarts.

**Session ID:** Automatically generated from the vector store object ID.

**Multi-User:** For production, extend the SESSIONS logic to use a persistent store like Redis.

## Development Tools

```bash
# Install dev tools
pip install ruff black

# Lint and format
ruff check . && black .
```

# Streamlit Frontend Features
**File Uploader:** Upload PDFs directly to the backend.

**Session ID:** Keep track of the current active session.

**Chat Interface:** Interactive chat window with a send button.

**Streaming:** Real-time response rendering for a smoother experience.
