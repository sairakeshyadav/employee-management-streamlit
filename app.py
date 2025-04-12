import streamlit as st
import pandas as pd
from datetime import date
import os

# --- AUTH SETUP USING FILE ---
def load_users():
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.write("admin,adminpass\n")
    users = {}
    with open("users.txt", "r") as f:
        for line in f:
            username, password = line.strip().split(",")
            users[username] = password
    return users

def login(users):
    st.markdown("""
        <style>
        .block-container { display: flex; justify-content: center; align-items: center; height: 90vh; }
        </style>
    """, unsafe_allow_html=True)
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["name"] = username.capitalize()
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# --- DUMMY EMPLOYEE DATA ---
def load_dummy_data():
    data = [
        {"id": "1", "name": "Alice", "email": "alice@example.com", "role": "Engineer", "department": "Tech", "status": "active", "doj": "2022-01-01"},
        {"id": "2", "name": "Bob", "email": "bob@example.com", "role": "Designer", "department": "Design", "status": "active", "doj": "2022-03-15"},
    ]
    return pd.DataFrame(data)

users = load_users()

# --- SESSION MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["name"] = ""

if not st.session_state["logged_in"]:
    login(users)
else:
    username = st.session_state["username"]
    name = st.session_state["name"]

    # Top right logout button
    st.markdown("""
        <style>
        .logout-button { position: absolute; top: 10px; right: 10px; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="logout-button">', unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.success(f"Welcome, {name} \U0001F44B")

    # --- MAIN TABS ---
    tabs = st.tabs(["\U0001F4CA Dashboard", "\U0001F4C5 Attendance", "\U0001F4DD Leaves", "\U0001F465 Employees"])

    # Load employee data
    df = load_dummy_data()

    with tabs[0]:  # Dashboard
        st.title("\U0001F4CA Dashboard Overview")
        if not df.empty:
            st.subheader("Employees by Department")
            st.bar_chart(df['department'].value_counts())
        else:
            st.info("No employee data available.")

    with tabs[1]:  # Attendance
        st.title("\U0001F4C5 Mark Attendance")
        today = date.today().isoformat()
        if not df.empty:
            for _, emp in df.iterrows():
                status = st.selectbox(f"{emp['name']} - {today}", ["present", "absent"], key=emp['id'])
                if st.button(f"Mark {emp['name']}", key=f"mark_{emp['id']}"):
                    st.success(f"{emp['name']} marked as {status}")
        else:
            st.info("No employees to mark attendance for.")

    with tabs[2]:  # Leaves
        st.title("\U0001F4DD Apply for Leave")
        if not df.empty:
            emp_name = st.selectbox("Select Employee", df['name'])
            reason = st.text_input("Reason for Leave")
            if st.button("Apply for Leave"):
                st.success(f"{emp_name} applied for leave: {reason}")
        else:
            st.info("No employees available.")

    with tabs[3]:  # Employees
        st.title("\U0001F465 Employee Directory")
        search = st.text_input("Search by name")
        filtered = df[df['name'].str.contains(search, case=False, na=False)]
        st.dataframe(filtered)

    # --- ADMIN PANEL ---
    if username == "admin":
        st.markdown("---")
        st.header("\U0001F6E0\ufe0f Admin Panel – Manage Employees")

        st.subheader("\U0001F4CB Current Employees")
        st.dataframe(df)

        st.subheader("\u2795 Add New Employee")
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        new_role = st.text_input("Role")
        new_dept = st.text_input("Department")
        new_status = st.selectbox("Status", ["active", "inactive"])
        new_doj = st.date_input("Date of Joining")

        if st.button("Add Employee"):
            new_row = pd.DataFrame([{"id": str(len(df)+1), "name": new_name, "email": new_email, "role": new_role, "department": new_dept, "status": new_status, "doj": str(new_doj)}])
            df = pd.concat([df, new_row], ignore_index=True)
            st.success(f"Added {new_name} to the employee list!")

        st.subheader("\u274C Delete Employee by ID")
        del_id = st.text_input("Enter Employee ID to Delete")
        if st.button("Delete"):
            df = df[df['id'] != del_id]
            st.success(f"Deleted employee ID {del_id}")
