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
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- DATA OPERATIONS ---
def load_employee_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

def save_employee(employee):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (id, name, email, role, department, status, doj)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, employee)
    conn.commit()
    conn.close()

def update_employee(employee_id, updated_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees
        SET name = ?, email = ?, role = ?, department = ?, status = ?, doj = ?
        WHERE id = ?
    """, (*updated_data, employee_id))
    conn.commit()
    conn.close()

def delete_employee(employee_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()

def save_attendance(attendance_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (employee_id, date, status)
        VALUES (?, ?, ?)
    """, attendance_data)
    conn.commit()
    conn.close()

def load_attendance_summary():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT employee_id, status, COUNT(*) as count
        FROM attendance
        GROUP BY employee_id, status
    """, conn)
    conn.close()
    return df

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
        if username == "admin" and password == "admin123":  # Replace with hashed password in production
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = "admin"
            st.session_state["name"] = "Admin"
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
    tabs = st.tabs(["\U0001F4CA Dashboard", "\U0001F4C5 Attendance", "\U0001F4DD Leaves", "\U0001F465 Employees"])

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

        # Department Distribution
        st.subheader("Employees by Department")
        if not df.empty:
            st.bar_chart(df['department'].value_counts())
        else:
            st.info("No employee data available.")

        # Attendance Summary
        st.subheader("Attendance Summary")
        attendance_summary = load_attendance_summary()
        st.dataframe(attendance_summary)

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

        # Add Employee
        if st.session_state["role"] == "admin":
            st.subheader("➕ Add New Employee")
            new_name = st.text_input("Name")
            new_email = st.text_input("Email")
            new_role = st.text_input("Role")
            new_dept = st.text_input("Department")
            new_status = st.selectbox("Status", ["active", "inactive"])
            new_doj = st.date_input("Date of Joining")
            if st.button("Add Employee"):
                new_id = str(uuid.uuid4())
                save_employee((new_id, new_name, new_email, new_role, new_dept, new_status, new_doj.isoformat()))
                st.success(f"Added {new_name} to the employee list!")

            # Delete Employee
            st.subheader("❌ Delete Employee by ID")
            del_id = st.text_input("Enter Employee ID to Delete")
            if st.button("Delete Employee"):
                delete_employee(del_id)
                st.success(f"Deleted employee ID {del_id}")

            # Edit Employee
            st.subheader("✏️ Edit Employee")
            edit_id = st.text_input("Enter Employee ID to Edit")
            if edit_id:
                employee_row = df[df['id'] == edit_id]
                if not employee_row.empty:
                    emp = employee_row.iloc[0]
                    updated_name = st.text_input("Name", emp['name'])
                    updated_email = st.text_input("Email", emp['email'])
                    updated_role = st.text_input("Role", emp['role'])
                    updated_dept = st.text_input("Department", emp['department'])
                    updated_status = st.selectbox("Status", ["active", "inactive"], index=["active", "inactive"].index(emp['status']))
                    updated_doj = st.date_input("Date of Joining", datetime.fromisoformat(emp['doj']))
                    if st.button("Update Employee"):
                        update_employee(edit_id, (updated_name, updated_email, updated_role, updated_dept, updated_status, updated_doj.isoformat()))
                        st.success(f"Updated employee ID {edit_id}")
                else:
                    st.warning("Employee ID not found.")
