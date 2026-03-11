"""Display helpers for chat history in Streamlit."""

from __future__ import annotations

import streamlit as st


def render_history(rows) -> None:
    """Render historical chat messages in sidebar."""
    st.sidebar.markdown("### 🕘 Previous Chats")
    if not rows:
        st.sidebar.caption("No history yet.")
        return

    for row in rows:
        role = "🧑" if row["role"] == "user" else "🤖"
        st.sidebar.caption(
            f"{role} **{row['feature']}** · {row['created_at']}\n\n{row['message'][:120]}"
        )
        st.sidebar.divider()
