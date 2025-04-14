import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import uuid

# --- DATABASE SETTINGS ---
DB_FILE = "employee_management.db"

# --- INITIALIZE DATABASE ---
def initialize_database():
    """Initialize the database and create necessary tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Employees table
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
    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
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
        return pd.DataFrame()  # Return an empty DataFrame


def save_employee(employee):
    """Save a new employee to the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employees (id, name, email, role, department, status, doj)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, employee)
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error saving employee: {e}")


def update_employee(employee_id, updated_data):
    """Update an employee's information in the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE employees
            SET name = ?, email = ?, role = ?, department = ?, status = ?, doj = ?
            WHERE id = ?
        """, (*updated_data, employee_id))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error updating employee: {e}")


def delete_employee(employee_id):
    """Delete an employee from the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error deleting employee: {e}")


def load_users():
    """Load user data from the database."""
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM users", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return pd.DataFrame()  # Return an empty DataFrame


def add_user(username, password):
    """Add a new user to the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, password))
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

# Session state for login
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
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = "admin"  # Assuming all users are admins
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid credentials")


if not st.session_state["logged_in"]:
    login()
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    st.sidebar.success(f"Welcome, {st.session_state['username']}")

    tabs = st.tabs(["Dashboard", "Employees", "Attendance", "Admin Management"])

    with tabs[0]:
        st.title("Dashboard")
        df = load_employee_data()
        st.write(df)

    with tabs[1]:
        st.title("Employees")
        # Add employee management logic here

    with tabs[2]:
        st.title("Attendance")
        # Add attendance logic here

    with tabs[3]:
        st.title("Admin Management")
        st.subheader("Add New User")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Add User"):
            add_user(new_username, new_password)
            st.success(f"User '{new_username}' added successfully!")

        st.subheader("Reset Password")
        reset_user = st.text_input("Username to Reset Password", key="reset_user")
        reset_pass = st.text_input("New Password", type="password", key="reset_pass")
        if st.button("Reset Password"):
            reset_password(reset_user, reset_pass)
            st.success(f"Password for user '{reset_user}' has been reset!")

        st.subheader("Delete User")
        del_user = st.text_input("Username to Delete", key="del_user")
        if st.button("Delete User"):
            delete_user(del_user)
            st.success(f"User '{del_user}' has been deleted!")

        st.subheader("Existing Users")
        st.write(load_users())
