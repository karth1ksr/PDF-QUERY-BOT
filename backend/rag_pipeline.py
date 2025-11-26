import os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from typing import TypedDict, List
from pydantic import Field, root_validator

from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

#Defining the models for embedding and chatting
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1, 
    )


#Defining the state schema to store ephemeral memory
class ChatState(TypedDict):
    messages: List[dict]
    db: object
    context: str

# Creating vectors from the uploaded pdf bytes
def create_vector_from_pdf(pdf_bytes):
    """ Takes PDF bytes -> return in-memory Chroma vectorstore"""
    tmp = NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(pdf_bytes)
    tmp.flush()
    tmp.close()


    loader = PyPDFLoader(tmp.name)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=150,
        )
    
    chunks = text_splitter.split_documents(docs)

    db = Chroma.from_documents(
        documents= chunks, 
        embedding=embeddings, 
        persist_directory=None,
       )

    return db

#Graph node 1: Retrieving data
def retrieve_context(state:ChatState):
    query = state["messages"][-1]["content"]
    db = state["db"]

    docs = db.similarity_search(query, k = 4)
    ctx = "\n\n".join([d.page_content for d in docs])

    return {"context": ctx}

#Graph node 2: LLM Reponse
def answer_query(state: ChatState):
    ctx = state["context"]
    history = state["messages"]
    query = history[-1]["content"]

    #Building conversation history
    conversation = ""
    for turn in history[:-1]:
        role = "User" if turn["type"] == "human" else "Assistant"
        conversation += f"{role}: {turn['content']}\n"
    
    prompt = f"""
        Use only the context given below to answer the questions of the user. 
        If you can't find any answers based on the given context, say "I don't know"

        Context:
        {ctx}

        Conversation so far:
        {conversation}

        User: {query}

        Assistant:
        """
    
    response = llm.invoke(prompt)
    answer = response.content

    return {"context": ctx,
            "messages": history + [{"type":"ai", "content": answer}],
            "db": state["db"]}

#Building Graph to store ephemeral memory

def build_chat_graph():
    workflow = StateGraph(ChatState)

    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("answer", answer_query)

    workflow.add_edge("__start__", "retrieve")
    workflow.add_edge("retrieve", "answer")
    workflow.add_edge("answer", "__end__")

    app = workflow.compile()

    return app