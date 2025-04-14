import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

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

    # Add role column if it does not exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
    except sqlite3.OperationalError:
        # Ignore if the column already exists
        pass

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
def load_data(query, params=()):
    """Load data from the database."""
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
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Login"):
        try:
            query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
            user_df = load_data(query, (username, password))

            if not user_df.empty:
                user = user_df.iloc[0]
                st.session_state["logged_in"] = True
                st.session_state["username"] = user["username"]
                st.session_state["role"] = user["role"]
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

    # Role-based Tabs
    with tabs[0]:
        st.title("Dashboard")
        df = load_data("SELECT * FROM employees")
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
            new_password = st.text_input("New Password", type="password", placeholder="Enter password for new user")
            new_role = st.selectbox("Role", ["admin", "user"])
            if st.button("Add User"):
                execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_username, new_password, new_role))
                st.success(f"User '{new_username}' added successfully!")

            # Reset Password
            st.subheader("Reset Password")
            reset_username = st.text_input("Username to Reset", key="reset_username")
            reset_new_password = st.text_input("New Password", type="password", placeholder="Enter new password", key="reset_new_password")
            if st.button("Reset Password"):
                execute_query("UPDATE users SET password = ? WHERE username = ?", (reset_new_password, reset_username))
                st.success(f"Password for '{reset_username}' has been reset.")

            # Delete User
            st.subheader("Delete User")
            delete_username = st.text_input("Username to Delete", key="delete_username")
            if st.button("Delete User"):
                execute_query("DELETE FROM users WHERE username = ?", (delete_username,))
                st.success(f"User '{delete_username}' has been deleted.")

            # Show Existing Users
            st.subheader("Existing Users")
            user_df = load_data("SELECT * FROM users")
            if not user_df.empty:
                st.dataframe(user_df)
            else:
                st.info("No users found.")
