"""Database utilities for AI Study Assistant."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable

DB_PATH = Path("study_assistant.db")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they do not exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                feature TEXT DEFAULT 'chat',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )


def create_user(username: str, name: str, password_hash: str) -> bool:
    """Create a user. Returns False if username already exists."""
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, name, password_hash) VALUES (?, ?, ?)",
                (username.lower().strip(), name.strip(), password_hash),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str) -> sqlite3.Row | None:
    """Fetch a user by username."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.lower().strip(),)
        ).fetchone()


def get_user_id(username: str) -> int | None:
    """Return user id for username."""
    row = get_user_by_username(username)
    return int(row["id"]) if row else None


def save_chat_message(user_id: int, role: str, message: str, feature: str = "chat") -> None:
    """Persist a chat message for a user."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chats (user_id, role, message, feature) VALUES (?, ?, ?, ?)",
            (user_id, role, message, feature),
        )


def get_chat_history(user_id: int, limit: int = 100) -> Iterable[sqlite3.Row]:
    """Get recent chats for the user."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, message, feature, created_at
            FROM chats
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return rows[::-1]
