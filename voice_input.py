"""Voice input utilities using SpeechRecognition."""

from __future__ import annotations

from io import BytesIO

import speech_recognition as sr


def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribe WAV/MP3 audio bytes into text using Google recognizer backend."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(BytesIO(audio_bytes)) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)
