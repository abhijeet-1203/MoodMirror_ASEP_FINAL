# auth_system.py
import streamlit as st
import sqlite3
import hashlib
import os

# Database setup
def init_auth_db():
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# User registration
def register_user(username, password):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)",
                 (username, hashlib.sha256(password.encode()).hexdigest()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# User login
def verify_user(username, password):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0] == hashlib.sha256(password.encode()).hexdigest()
    return False

# Auth UI
def show_auth():
    init_auth_db()
    st.title("🔒 MoodMirror Authentication")
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if verify_user(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Choose username")
            new_password = st.text_input("Choose password", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif register_user(new_username, new_password):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists")