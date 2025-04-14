import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import uuid
import os

# --- DATABASE MANAGEMENT ---
DB_FILE = "employee_management.db"

def initialize_database():
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
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- DATA OPERATIONS ---
# Load user data
def load_users():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

# Add a new user
def add_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password)
        VALUES (?, ?)
    """, (username, password))
    conn.commit()
    conn.close()

# Update a user's password
def reset_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE username = ?
    """, (new_password, username))
    conn.commit()
    conn.close()

# Delete a user
def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM users
        WHERE username = ?
    """, (username,))
    conn.commit()
    conn.close()

# --- STREAMLIT APP ---
# Initialize database
initialize_database()

# --- SESSION MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["name"] = ""
    st.session_state["role"] = ""

# --- LOGIN UI ---
def login():
    st.markdown("""
        <style>
        .block-container { display: flex; justify-content: center; align-items: center; height: 90vh; }
        </style>
    """, unsafe_allow_html=True)
    
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
            st.session_state["role"] = "admin"  # Assuming all users are admins for this example
            st.session_state["name"] = username.capitalize()
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid credentials")

# --- MAIN APP ---
if not st.session_state["logged_in"]:
    login()
else:
    # Top right logout button
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    st.sidebar.success(f"Welcome, {st.session_state['name']} \U0001F44B")

    # --- MAIN TABS ---
    tabs = st.tabs(["\U0001F4CA Dashboard", "\U0001F4C5 Attendance", "\U0001F4DD Leaves", "\U0001F465 Employees", "\U0001F511 Admin Management"])

    # --- DASHBOARD ---
    with tabs[0]:
        st.title("\U0001F4CA Dashboard Overview")
        df = load_employee_data()

        # Employee Overview
        total_employees = len(df)
        active_employees = len(df[df['status'] == 'active'])
        inactive_employees = len(df[df['status'] == 'inactive'])
        st.metric("Total Employees", total_employees)
        st.metric("Active Employees", active_employees)
        st.metric("Inactive Employees", inactive_employees)

    # --- ATTENDANCE ---
    with tabs[1]:
        st.title("\U0001F4C5 Mark Attendance")
        df = load_employee_data()
        today = date.today().isoformat()
        if not df.empty:
            for _, emp in df.iterrows():
                status = st.selectbox(f"{emp['name']} - {today}", ["present", "absent"], key=f"attendance_{emp['id']}")
                if st.button(f"Mark {emp['name']}", key=f"mark_{emp['id']}"):
                    save_attendance((emp['id'], today, status))
                    st.success(f"{emp['name']} marked as {status}")
        else:
            st.info("No employees to mark attendance for.")

    # --- LEAVES ---
    with tabs[2]:
        st.title("\U0001F4DD Apply for Leave")
        df = load_employee_data()
        if not df.empty:
            emp_name = st.selectbox("Select Employee", df['name'])
            reason = st.text_input("Reason for Leave")
            if st.button("Apply for Leave"):
                st.success(f"{emp_name} applied for leave: {reason}")
        else:
            st.info("No employees available.")

    # --- EMPLOYEES ---
    with tabs[3]:
        st.title("\U0001F465 Employee Directory")
        df = load_employee_data()
        search = st.text_input("Search by name")
        filtered = df[df['name'].str.contains(search, case=False, na=False)] if search else df
        st.dataframe(filtered)

    # --- ADMIN MANAGEMENT ---
    with tabs[4]:
        st.title("\U0001F511 Admin Management")

        # Add User
        st.subheader("➕ Add New User")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Add User"):
            add_user(new_username, new_password)
            st.success(f"User '{new_username}' added successfully!")

        # Reset Password
        st.subheader("🔄 Reset Password")
        reset_username = st.text_input("Username to Reset", key="reset_username")
        new_password = st.text_input("New Password", type="password", key="reset_password")
        if st.button("Reset Password"):
            reset_password(reset_username, new_password)
            st.success(f"Password for user '{reset_username}' has been reset!")

        # Delete User
        st.subheader("❌ Delete User")
        del_username = st.text_input("Username to Delete", key="delete_username")
        if st.button("Delete User"):
            delete_user(del_username)
            st.success(f"User '{del_username}' has been deleted!")

        # List of Users
        st.subheader("👥 Existing Users")
        users_df = load_users()
        st.dataframe(users_df)
