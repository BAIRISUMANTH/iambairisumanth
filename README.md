# AI Study Assistant

AI Study Assistant is a modular Streamlit web app that helps students chat with AI, ask questions from PDFs, submit voice questions, generate code, and solve exam questions step by step.

## Features

- **ChatGPT-style chat** with streaming responses.
- **PDF Notes Assistant** for Q&A on uploaded notes.
- **Voice Questions** using SpeechRecognition.
- **Code Generator** for programming tasks.
- **AI Exam Solver** with structured solutions.
- **SQLite chat history** persisted per user.
- **Login and registration system** with hashed passwords.
- **Professional dark UI** with sidebar navigation.

## Project Structure

```text
AI_STUDY_ASSISTANT/
│
├── app.py
├── login.py
├── database.py
├── pdf_reader.py
├── voice_input.py
├── code_generator.py
├── exam_solver.py
├── chat_history.py
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI key:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
   Or create `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "your_api_key_here"
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment (Streamlit Cloud)

1. Push this project to GitHub.
2. Open [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Create a new app and point it to `app.py`.
4. In app settings, add secret:
   - `OPENAI_API_KEY` = your key.
5. Deploy.

## Notes

- First user can register from the sidebar.
- Chat and feature outputs are saved in `study_assistant.db`.
- Voice recognition uses Google Web Speech API through the `SpeechRecognition` package.
