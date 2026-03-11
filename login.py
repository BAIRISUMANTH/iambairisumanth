"""Authentication module backed by SQLite + streamlit-authenticator hashing helpers."""

from __future__ import annotations

import bcrypt
import streamlit as st
import streamlit_authenticator as stauth

from database import create_user, get_user_by_username


def register_widget() -> None:
    """Render registration form in sidebar."""
    with st.sidebar.expander("🆕 Register", expanded=False):
        with st.form("register_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account")

        if submitted:
            if not all([name.strip(), username.strip(), password.strip()]):
                st.warning("Please fill all fields.")
                return
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            password_hash = stauth.Hasher([password]).generate()[0]
            created = create_user(username=username, name=name, password_hash=password_hash)
            if created:
                st.success("Account created. You can now login.")
            else:
                st.error("Username already exists.")


def login_widget() -> bool:
    """Render login form and set session state if successful."""
    st.sidebar.subheader("🔐 Login")
    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = get_user_by_username(username)
        if not user:
            st.sidebar.error("Invalid username or password.")
            return False

        valid = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
        if not valid:
            st.sidebar.error("Invalid username or password.")
            return False

        st.session_state["authenticated"] = True
        st.session_state["username"] = user["username"]
        st.session_state["name"] = user["name"]
        st.sidebar.success(f"Welcome, {user['name']}!")
        return True

    return bool(st.session_state.get("authenticated", False))


def logout_widget() -> None:
    """Render a logout button in sidebar."""
    if st.sidebar.button("Logout"):
        for key in ["authenticated", "username", "name"]:
            st.session_state.pop(key, None)
        st.rerun()
