import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF Query Bot", layout="wide")

st.title("PDF Query Bot")
st.write("Upload a PDF and ask questions from it.")

#Sesssion State

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#Upload Section
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file and st.session_state.session_id is None:

    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("PDF too large! Max allowed size is 5 MB.")
        st.stop()
    
    with st.spinner("Processing PDF..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        res = requests.post(f"{FASTAPI_URL}/upload_pdf", files=files)

    if res.status_code == 200:
        data = res.json()
        st.session_state.session_id = data["session_id"]
        st.success("PDF uploaded and processed successfully!")
    else:
        st.error("Failed to process PDF.")

#Chat interface
if st.session_state.session_id:

    user_query = st.chat_input("Ask your question...")

    if user_query:
        #Add user message locally
        st.session_state.chat_history.append(("user", user_query))

        payload = {
            "session_id": str(st.session_state.session_id),
            "query": user_query
        }

        with st.spinner("Thinking..."):
            res = requests.post(f"{FASTAPI_URL}/chat", data=payload)

        if res.status_code == 200:
            bot_reply = res.json()["response"]
            st.session_state.chat_history.append(("bot", bot_reply))
        else:
            st.error("Error contacting the backend.")

    #Display chat messages
    for role, msg in st.session_state.chat_history:
        if role == "user":
            with st.chat_message("user"):
                st.write(msg)
        
        else:
            with st.chat_message("assistant"):
                st.write(msg)

    #Reset session
    if st.button("Reset Chat"):
        requests.post(f"{FASTAPI_URL}/reset", data={"session_id": str(st.session_state.session_id)})
        st.session_state.session_id = None
        st.session_state.chat_history = []
        st.success("Session cleared.")