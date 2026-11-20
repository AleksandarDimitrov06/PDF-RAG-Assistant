import os
import requests
import streamlit as st
import uuid

API_URL = os.getenv("API_URL", "http://localhost:8000")
UPLOAD_URL = f"{API_URL}/upload"
QUERY_URL = f"{API_URL}/query"

st.title("PDF RAG Assistant")

if "session_id" not in st.session_state:
    st.session_state.session_id = "test_session_id" # str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

pdf_file = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"],
    key="pdf_uploader",
)

if pdf_file is not None:
    if st.session_state.get("pdf_name") != pdf_file.name:
        with st.spinner("Processing PDF..."):
            try:
                response = requests.post(
                    UPLOAD_URL,
                    params={"session_id":st.session_state.session_id},
                    files={
                        "file": (
                            pdf_file.name,
                            pdf_file.getvalue(),
                            "application/pdf",
                        )
                    },
                    timeout=120,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                st.error(f"Could not upload the PDF: {exc}")
            else:
                upload_result = response.json()
                st.session_state.document_hash = upload_result["document_hash"]
                st.session_state.pdf_name = pdf_file.name
                st.session_state.messages = []
                st.success(upload_result["message"])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask a question about the PDF...")

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        QUERY_URL,
                        json={"session_id": st.session_state.session_id,"document_hash": st.session_state.document_hash, "question": question},
                        timeout=120,
                    )
                    response.raise_for_status()
                    answer = response.json()["answer"]
                except requests.RequestException as exc:
                    if exc.response is not None:
                        try:
                            detail = exc.response.json().get("detail")
                            answer = detail or str(exc)
                        except ValueError:
                            answer = str(exc)
                    else:
                        answer = str(exc)

                st.write(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
else:
    st.session_state.pop("pdf_name", None)
    st.session_state.messages = []
    st.info("Upload a PDF to get started.")