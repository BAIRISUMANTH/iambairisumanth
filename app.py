"""AI Study Assistant Streamlit app."""

from __future__ import annotations

import os
from typing import Generator

import streamlit as st
from openai import OpenAI

from chat_history import render_history
from code_generator import build_code_prompt
from database import get_chat_history, get_user_id, init_db, save_chat_message
from exam_solver import build_exam_prompt
from login import login_widget, logout_widget, register_widget
from pdf_reader import build_pdf_qa_prompt, extract_text_from_pdf
from voice_input import transcribe_audio_bytes

st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")


CUSTOM_CSS = """
<style>
.stApp {
    background-color: #0e1117;
    color: #f1f5f9;
}
.block-container {
    padding-top: 1.2rem;
}
.user-bubble {
    background-color: #1d4ed8;
    color: white;
    padding: 0.8rem 1rem;
    border-radius: 0.8rem;
    margin: 0.5rem 0;
}
.ai-bubble {
    background-color: #1f2937;
    color: #f9fafb;
    padding: 0.8rem 1rem;
    border-radius: 0.8rem;
    margin: 0.5rem 0;
    border: 1px solid #374151;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_client() -> OpenAI:
    """Create OpenAI client from environment variable."""
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("OPENAI_API_KEY is not configured. Add it to environment or .streamlit/secrets.toml")
        st.stop()
    return OpenAI(api_key=api_key)


def stream_answer(client: OpenAI, prompt: str, model: str = "gpt-4o-mini") -> Generator[str, None, None]:
    """Yield chunks from OpenAI streaming chat completion."""
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are AI Study Assistant. Be accurate and supportive."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta


def stream_to_text(gen: Generator[str, None, None], placeholder) -> str:
    """Write token stream to placeholder and return full text."""
    full = ""
    for part in gen:
        full += part
        placeholder.markdown(f"<div class='ai-bubble'>{full}</div>", unsafe_allow_html=True)
    return full


init_db()
client = get_client()

st.title("📚 AI Study Assistant")
st.caption("Chat, solve exams, generate code, and query your PDF notes in one place.")

register_widget()

if not st.session_state.get("authenticated"):
    if not login_widget():
        st.info("Please login or register to continue.")
        st.stop()

logout_widget()

username = st.session_state["username"]
user_id = get_user_id(username)
if user_id is None:
    st.error("Could not resolve user account.")
    st.stop()

history_rows = list(get_chat_history(user_id))
render_history(history_rows)

feature = st.sidebar.radio(
    "Navigate",
    ["💬 Chat", "📄 PDF Notes Assistant", "🎤 Voice Questions", "💻 Code Generator", "🧠 AI Exam Solver"],
)

if "live_chat" not in st.session_state:
    st.session_state["live_chat"] = []

if feature == "💬 Chat":
    st.subheader("ChatGPT-style Chat")
    for msg in st.session_state["live_chat"]:
        bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        st.markdown(f"<div class='{bubble_class}'>{msg['content']}</div>", unsafe_allow_html=True)

    user_prompt = st.chat_input("Ask anything about your studies...")
    if user_prompt:
        st.session_state["live_chat"].append({"role": "user", "content": user_prompt})
        save_chat_message(user_id, "user", user_prompt, feature="chat")
        st.markdown(f"<div class='user-bubble'>{user_prompt}</div>", unsafe_allow_html=True)
        placeholder = st.empty()
        answer = stream_to_text(stream_answer(client, user_prompt), placeholder)
        st.session_state["live_chat"].append({"role": "assistant", "content": answer})
        save_chat_message(user_id, "assistant", answer, feature="chat")

elif feature == "📄 PDF Notes Assistant":
    st.subheader("PDF Notes Assistant")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded:
        text = extract_text_from_pdf(uploaded.read())
        if not text:
            st.warning("No extractable text found in this PDF.")
        else:
            st.success("PDF loaded. Ask a question below.")
            question = st.text_input("Question about PDF")
            if st.button("Ask PDF", use_container_width=True) and question:
                save_chat_message(user_id, "user", question, feature="pdf")
                prompt = build_pdf_qa_prompt(text, question)
                placeholder = st.empty()
                answer = stream_to_text(stream_answer(client, prompt), placeholder)
                save_chat_message(user_id, "assistant", answer, feature="pdf")

elif feature == "🎤 Voice Questions":
    st.subheader("Voice Questions")
    st.caption("Use your microphone, then transcribe and send to AI.")
    audio = st.audio_input("Record your question")
    if audio is not None:
        if st.button("Transcribe & Ask", use_container_width=True):
            try:
                transcript = transcribe_audio_bytes(audio.read())
                st.markdown(f"**You said:** {transcript}")
                save_chat_message(user_id, "user", transcript, feature="voice")
                placeholder = st.empty()
                answer = stream_to_text(stream_answer(client, transcript), placeholder)
                save_chat_message(user_id, "assistant", answer, feature="voice")
            except Exception as exc:
                st.error(f"Voice transcription failed: {exc}")

elif feature == "💻 Code Generator":
    st.subheader("Code Generator")
    language = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++", "SQL", "Other"])
    request = st.text_area("Describe the code you want")
    if st.button("Generate Code", use_container_width=True) and request.strip():
        save_chat_message(user_id, "user", request, feature="code")
        prompt = build_code_prompt(request, language)
        placeholder = st.empty()
        answer = stream_to_text(stream_answer(client, prompt), placeholder)
        save_chat_message(user_id, "assistant", answer, feature="code")

elif feature == "🧠 AI Exam Solver":
    st.subheader("AI Exam Solver")
    question = st.text_area("Paste the exam question")
    if st.button("Solve", use_container_width=True) and question.strip():
        save_chat_message(user_id, "user", question, feature="exam")
        prompt = build_exam_prompt(question)
        placeholder = st.empty()
        answer = stream_to_text(stream_answer(client, prompt), placeholder)
        save_chat_message(user_id, "assistant", answer, feature="exam")
