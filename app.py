# Full `app.py` with default admin functionality added
import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
from datetime import date

# --- Initialize Session State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""

# --- DATABASE CONNECTION FUNCTIONS ---
def get_connection():
    """Establish a connection to the database."""
    return sqlite3.connect("employee_management.db")

def load_data(query, params=()):
    """Load data from the database and return it as a DataFrame."""
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def execute_query(query, params=()):
    """Execute a query in the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database operation failed: {e}")

# --- HELPER FUNCTIONS ---
def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed_password):
    """Verify a password against its hash using bcrypt."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def validate_input(username, password):
    """Validate input for username and password."""
    if len(username) < 3:
        st.warning("Username must be at least 3 characters long.")
        return False
    if len(password) < 6:
        st.warning("Password must be at least 6 characters long.")
        return False
    return True

# --- Create Default Admin User ---
def create_default_admin():
    """Ensure a default admin user is created with a secure password."""
    default_admin_username = "admin"
    default_admin_password = "admin123"  # Update this to a stronger default password
    default_admin_role = "admin"

    # Hash the default admin password
    hashed_password = hash_password(default_admin_password)

    try:
        # Check if the admin user already exists
        query = "SELECT * FROM users WHERE username = ?"
        existing_admin = load_data(query, (default_admin_username,))
        if existing_admin.empty:
            # Insert the default admin user into the database
            execute_query(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (default_admin_username, hashed_password, default_admin_role),
            )
            st.info("Default admin user created. Username: 'admin', Password: 'admin123'")
        else:
            st.info("Default admin user already exists.")
    except Exception as e:
        st.error(f"Error creating default admin user: {e}")

# Ensure default admin user exists
create_default_admin()

# --- LOGIN FUNCTION ---
def login():
    """Display the login interface and handle authentication."""
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Login"):
        try:
            query = "SELECT username, password, role FROM users WHERE username = ?"
            user_df = load_data(query, (username,))
            if not user_df.empty:
                user = user_df.iloc[0]
                hashed_password = user["password"].encode("utf-8") if isinstance(user["password"], str) else user["password"]
                if verify_password(password, hashed_password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user["username"]
                    st.session_state["role"] = user["role"]
                    st.success(f"Welcome, {username}!")
                else:
                    st.error("Invalid password. Please try again.")
            else:
                st.error("Invalid username. Please try again.")
        except Exception as e:
            st.error(f"An error occurred during login: {e}")

# --- MAIN APPLICATION ---
if not st.session_state["logged_in"]:
    login()
else:
    # Sidebar for logout and user details
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    st.sidebar.success(f"Logged in as: {st.session_state['username']}")
    # Application tabs follow...
