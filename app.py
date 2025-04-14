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
                hashed_password = user["password"]
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
    
    # Tabs for the app
    if st.session_state["role"] == "admin":
        tabs = st.tabs(["Dashboard", "Employees", "Attendance", "Admin Management"])
    else:
        tabs = st.tabs(["Dashboard", "Employees", "Attendance"])
    
    # Dashboard Tab
    with tabs[0]:
        st.title("Dashboard")
        try:
            df = load_data("SELECT * FROM employees")
            if not df.empty:
                st.dataframe(df)
            else:
                st.info("No employee data available.")
        except Exception as e:
            st.error(f"Error loading dashboard data: {e}")
    
    # Employees Tab
    with tabs[1]:
        st.title("Employees")
        st.info("Employee management functionality goes here.")
    
    # Attendance Tab
    with tabs[2]:
        st.title("Attendance")
        st.info("Attendance tracking functionality goes here.")
    
    # Admin Management Tab (only visible for admin users)
    if st.session_state["role"] == "admin":
        with tabs[3]:
            st.title("Admin Management")
            
            # Add User
            st.subheader("Add New User")
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password", placeholder="Enter password for new user")
            new_role = st.selectbox("Role", ["admin", "user"])
            if st.button("Add User"):
                if validate_input(new_username, new_password):
                    try:
                        hashed_password = hash_password(new_password)
                        execute_query(
                            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                            (new_username, hashed_password, new_role),
                        )
                        st.success(f"User '{new_username}' added successfully!")
                    except Exception as e:
                        st.error(f"Error adding user: {e}")
            
            # Reset Password
            st.subheader("Reset Password")
            reset_username = st.text_input("Username to Reset", key="reset_username")
            reset_new_password = st.text_input(
                "New Password", type="password", placeholder="Enter new password", key="reset_new_password"
            )
            if st.button("Reset Password"):
                if validate_input(reset_username, reset_new_password):
                    try:
                        hashed_password = hash_password(reset_new_password)
                        execute_query(
                            "UPDATE users SET password = ? WHERE username = ?",
                            (hashed_password, reset_username),
                        )
                        st.success(f"Password for '{reset_username}' has been reset.")
                    except Exception as e:
                        st.error(f"Error resetting password: {e}")
            
            # Delete User
            st.subheader("Delete User")
            delete_username = st.text_input("Username to Delete", key="delete_username")
            if st.button("Delete User"):
                if delete_username:
                    if st.confirm("Are you sure you want to delete this user?"):
                        try:
                            execute_query("DELETE FROM users WHERE username = ?", (delete_username,))
                            st.success(f"User '{delete_username}' has been deleted.")
                        except Exception as e:
                            st.error(f"Error deleting user: {e}")
                    else:
                        st.info("User deletion canceled.")
                else:
                    st.warning("Please provide a username to delete.")
            
            # Show Existing Users
            st.subheader("Existing Users")
            try:
                user_df = load_data("SELECT username, role FROM users")
                if not user_df.empty:
                    st.dataframe(user_df)
                else:
                    st.info("No users found.")
            except Exception as e:
                st.error(f"Error loading user data: {e}")
