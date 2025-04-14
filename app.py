import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import uuid

# --- DATABASE SETTINGS ---
DB_FILE = "employee_management.db"

# --- DEFAULT ADMIN CREDENTIALS ---
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# --- DATABASE INITIALIZATION ---
def initialize_database():
    """Initialize the database and create necessary tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            status TEXT NOT NULL,
            doj TEXT NOT NULL
        )
    """)

    # Create attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Add default admin credentials if not already present
    cursor.execute("SELECT * FROM users WHERE username = ?", (DEFAULT_ADMIN_USERNAME,))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, "admin"))
        st.info("Default admin credentials added: Username='admin', Password='admin123'")

    conn.commit()
    conn.close()

# --- DATABASE CONNECTION ---
def get_connection():
    """Get a connection to the database."""
    return sqlite3.connect(DB_FILE)

# --- DATABASE OPERATIONS ---
def load_employee_data():
    """Load employee data from the database."""
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading employee data: {e}")
        return pd.DataFrame()

def load_users():
    """Load user data from the database."""
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM users", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return pd.DataFrame()

def add_user(username, password, role):
    """Add a new user to the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (username, password, role))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error adding user: {e}")

def reset_password(username, new_password):
    """Reset a user's password."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET password = ?
            WHERE username = ?
        """, (new_password, username))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error resetting password: {e}")

def delete_user(username):
    """Delete a user from the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error deleting user: {e}")

# --- STREAMLIT APP ---
# Initialize the database
initialize_database()

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""

def login():
    """User login interface."""
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user[2]  # Role is the 3rd column in the users table
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password. Please try again.")
        except Exception as e:
            st.error(f"An error occurred during login: {e}")

if not st.session_state["logged_in"]:
    login()
else:
    # Sidebar for logout and user details
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    st.sidebar.success(f"Logged in as: {st.session_state['username']}")

    # Tabs for the app
    if st.session_state["role"] == "admin":
        tabs = st.tabs(["Dashboard", "Employees", "Attendance", "Admin Management"])
    else:
        tabs = st.tabs(["Dashboard", "Employees", "Attendance"])

    with tabs[0]:
        st.title("Dashboard")
        df = load_employee_data()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No employee data available.")

    with tabs[1]:
        st.title("Employees")
        st.info("Employee management functionality goes here.")

    with tabs[2]:
        st.title("Attendance")
        st.info("Attendance tracking functionality goes here.")

    if st.session_state["role"] == "admin":
        with tabs[3]:
            st.title("Admin Management")
            
            # Add User
            st.subheader("Add New User")
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            new_role = st.selectbox("Role", ["admin", "user"])
            if st.button("Add User"):
                add_user(new_username, new_password, new_role)
                st.success(f"User '{new_username}' added successfully!")

            # Reset Password
            st.subheader("Reset Password")
            reset_username = st.text_input("Username to Reset", key="reset_username")
            reset_new_password = st.text_input("New Password", type="password", key="reset_new_password")
            if st.button("Reset Password"):
                reset_password(reset_username, reset_new_password)
                st.success(f"Password for '{reset_username}' has been reset.")

            # Delete User
            st.subheader("Delete User")
            delete_username = st.text_input("Username to Delete", key="delete_username")
            if st.button("Delete User"):
                delete_user(delete_username)
                st.success(f"User '{delete_username}' has been deleted.")

            # Show Existing Users
            st.subheader("Existing Users")
            user_df = load_users()
            if not user_df.empty:
                st.dataframe(user_df)
            else:
                st.info("No users found.")
