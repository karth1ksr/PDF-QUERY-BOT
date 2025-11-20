from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.rag_pipeline import create_vector_from_pdf, build_chat_graph
from langchain_core.messages import HumanMessage

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Session memory
SESSIONS = {}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF and create an in-memory vectorstore"""
    pdf_bytes = await file.read()
    db = create_vector_from_pdf(pdf_bytes)
    chat_graph = build_chat_graph()

    session_id = id(db)
    SESSIONS[session_id] = {
        "db": db,
        "graph": chat_graph,
        "messages": []
    }

    return {"session_id": session_id, "message": "PDF processed successfully."}


@app.post("/chat")
async def chat(session_id: int = Form(...), query: str = Form(...)):
    """Send a user question and get RAG-based answer."""
    
    if session_id not in SESSIONS:
        return {"error": "Invalid session ID"}
    
    session = SESSIONS[session_id]

    session["messages"].append({"type": "human", "content":query})

    input_state = {
        "messages": session["messages"],
        "db": session["db"],
        "context": ""
    }

    result = session["graph"].invoke(input_state)

    session["messages"] = result["messages"]

    return {"response": session["messages"][-1]["content"]}


@app.post("/reset")
def reset(session_id: int = Form(...)):
    if session_id in SESSIONS:
        SESSIONS.pop(session_id)
        return {"message": "Session Cleared"}
    return {"error": "Invalid session ID"}