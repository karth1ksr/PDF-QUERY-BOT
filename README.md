**PDF-Query-Bot**
A lightweight RAG chatbot for querying your PDFs using Gemini models. Upload a PDF, get a session ID, and chat with your document via simple POST endpoints. Built with FastAPI backend, LangGraph for stateful conversations, and Streamlit frontend.

**Features**
PDF to RAG: Converts uploaded PDFs to Chroma vector store with Gemini embeddings

Session-Based Chat: In-memory session management with conversation history

LangGraph Pipeline: Retrieve → Answer workflow with ephemeral memory

Gemini 2.5 Flash: Fast, context-aware responses (no local LLM needed)

Simple API: /upload_pdf → /chat → /reset endpoints

Streamlit UI: Clean frontend for testing

*Quick Start*

Prerequisites

bash
pip install streamlit fastapi python-multipart python-dotenv langchain-google-genai langgraph chromadb pypdf
1. Setup Environment

bash
cp .env.example .env
# Add your GOOGLE_API_KEY to .env

2. Run Backend
bash
uvicorn main:app --reload --port 8000

3. Run Frontend
bash
streamlit run frontend.py
Visit http://localhost:8501 to start querying PDFs!

*API Usage*

bash
# 1. Upload PDF
curl -X POST -F "file=@document.pdf" http://localhost:8000/upload_pdf
# Returns: {"session_id": 123456, "message": "PDF processed successfully."}

# 2. Chat
curl -X POST "http://localhost:8000/chat" \
  -d "session_id=123456" \
  -d "query=What is the main topic?"

# 3. Reset session
curl -X POST "http://localhost:8000/reset" -d "session_id=123456"

# How It Works
Upload PDF → Creates Chroma vectorstore from chunks (1200 chars, 150 overlap)

Session Created → Stores db, graph, messages in SESSIONS[session_id]

# Chat Flow:

text
Query → retrieve_context() → answer_query() → Response
          ↓                    ↓
    Vector search (k=4)    Gemini 2.5 + history
State Managed → LangGraph preserves conversation across turns

# Configuration
Edit .env:

text
GOOGLE_API_KEY=your_key_here
**Session Management**
In-Memory: SESSIONS = {} dictionary (resets on restart)

Session ID: Auto-generated from vectorstore object ID

Reset: POST /reset clears specific session

Multi-User Ready: Extend SESSIONS with Redis for production

**Development**
bash
# Install dev tools
pip install ruff black

# Lint & format
ruff check . && black .

# Run both services
# Terminal 1: uvicorn main:app --reload
# Terminal 2: streamlit run frontend.py

# Streamlit Frontend
The frontend.py provides:

File uploader for PDFs

Session ID display

Chat interface with send button

Clear session button

Response streaming


📄 License
MIT License © 2026 Karthik S R
