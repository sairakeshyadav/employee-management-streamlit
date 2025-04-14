import streamlit as st
import pandas as pd
from datetime import date
import os

# --- AUTH SETUP USING FILE ---
def load_users():
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.write("admin,admin123,admin\n")
    users = {}
    with open("users.txt", "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                username, password, role = parts
                users[username] = {"password": password, "role": role}
            else:
                st.warning(f"Ignoring invalid user line: {line.strip()}")
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
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["name"] = username.capitalize()
            st.session_state["role"] = users[username]["role"]
        else:
            st.error("Invalid credentials")

# --- EMPLOYEE DATA MANAGEMENT ---
EMPLOYEE_FILE = "employees.csv"
ATTENDANCE_FILE = "attendance.csv"

def load_employee_data():
    if not os.path.exists(EMPLOYEE_FILE):
        df = pd.DataFrame([
            {"id": "1", "name": "Alice", "email": "alice@example.com", "role": "Engineer", "department": "Tech", "status": "active", "doj": "2022-01-01"},
            {"id": "2", "name": "Bob", "email": "bob@example.com", "role": "Designer", "department": "Design", "status": "active", "doj": "2022-03-15"},
        ])
        df.to_csv(EMPLOYEE_FILE, index=False)
    else:
        df = pd.read_csv(EMPLOYEE_FILE)
    return df

def save_employee_data(df):
    df.to_csv(EMPLOYEE_FILE, index=False)

def load_attendance_data():
    if os.path.exists(ATTENDANCE_FILE):
        return pd.read_csv(ATTENDANCE_FILE)
    else:
        return pd.DataFrame(columns=["employee_id", "name", "date", "status"])

def save_attendance_record(record):
    att_df = load_attendance_data()
    today = record["date"]
    emp_id = record["employee_id"]
    if not ((att_df["employee_id"] == emp_id) & (att_df["date"] == today)).any():
        att_df = pd.concat([att_df, pd.DataFrame([record])], ignore_index=True)
        att_df.to_csv(ATTENDANCE_FILE, index=False)

users = load_users()

# --- SESSION MANAGEMENT ---
defaults = {
    "logged_in": False,
    "username": "",
    "name": "",
    "role": ""
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state["logged_in"]:
    login(users)
else:
    username = st.session_state["username"]
    name = st.session_state["name"]
    role = st.session_state["role"]

    st.markdown("""
        <style>
        .logout-button { position: absolute; top: 10px; right: 10px; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="logout-button">', unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.clear()
    st.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.success(f"Welcome, {name} \U0001F44B")

    tab_labels = ["\U0001F4CA Dashboard", "\U0001F4C5 Attendance", "\U0001F4DD Leaves", "\U0001F465 Employees"]
    if role == "admin":
        tab_labels.append("\U0001F6E0️ Admin Panel")
    tabs = st.tabs(tab_labels)

    df = load_employee_data()

    with tabs[0]:
        st.title("\U0001F4CA Dashboard Overview")
        if not df.empty:
            st.subheader("Employees by Department")
            st.bar_chart(df['department'].value_counts())
        else:
            st.info("No employee data available.")

    with tabs[1]:
        st.title("\U0001F4C5 Mark Attendance")
        today = date.today().isoformat()
        att_df = load_attendance_data()

        if not df.empty:
            for _, emp in df.iterrows():
                status_key = f"status_{emp['id']}"
                button_key = f"mark_{emp['id']}"
                status = st.selectbox(
                    f"{emp['name']} - {today}",
                    ["present", "absent"],
                    key=status_key
                )
                if st.button(f"Mark {emp['name']}", key=button_key):
                    record = {
                        "employee_id": emp["id"],
                        "name": emp["name"],
                        "date": today,
                        "status": status
                    }
                    if ((att_df["employee_id"] == emp["id"]) & (att_df["date"] == today)).any():
                        st.warning(f"{emp['name']} already marked for {today}.")
                    else:
                        save_attendance_record(record)
                        st.success(f"{emp['name']} marked as {status} for {today}")
        else:
            st.info("No employees to mark attendance for.")

    with tabs[2]:
        st.title("\U0001F4DD Apply for Leave")
        if not df.empty:
            emp_name = st.selectbox("Select Employee", df['name'])
            reason = st.text_input("Reason for Leave")
            if st.button("Apply for Leave"):
                st.success(f"{emp_name} applied for leave: {reason}")
        else:
            st.info("No employees available.")

    with tabs[3]:
        st.title("\U0001F465 Employee Directory")
        search = st.text_input("Search by name")
        filtered = df[df['name'].str.contains(search, case=False, na=False)]
        st.dataframe(filtered)

    if role == "admin":
        with tabs[4]:
            st.markdown("---")
            st.header("\U0001F6E0️ Admin Panel – Manage Employees")

            st.subheader("\U0001F4CB Current Employees")
            st.dataframe(df)

            st.subheader("➕ Add New Employee")
            new_name = st.text_input("Name")
            new_email = st.text_input("Email")
            new_role = st.text_input("Role")
            new_dept = st.text_input("Department")
            new_status = st.selectbox("Status", ["active", "inactive"])
            new_doj = st.date_input("Date of Joining")

            if st.button("Add Employee"):
                new_row = pd.DataFrame([{"id": str(len(df)+1), "name": new_name, "email": new_email, "role": new_role, "department": new_dept, "status": new_status, "doj": str(new_doj)}])
                df = pd.concat([df, new_row], ignore_index=True)
                save_employee_data(df)
                st.success(f"Added {new_name} to the employee list!")

            st.subheader("❌ Delete Employee by ID")
            del_id = st.text_input("Enter Employee ID to Delete")
            if st.button("Delete"):
                df = df[df['id'] != del_id]
                save_employee_data(df)
                st.success(f"Deleted employee ID {del_id}")

            st.subheader("✏️ Edit Employee")
            edit_id = st.text_input("Enter Employee ID to Edit")
            if edit_id in df['id'].values:
                emp_row = df[df['id'] == edit_id].iloc[0]
                new_name = st.text_input("New Name", emp_row['name'])
                new_email = st.text_input("New Email", emp_row['email'])
                new_role = st.text_input("New Role", emp_row['role'])
                new_dept = st.text_input("New Department", emp_row['department'])
                new_status = st.selectbox("New Status", ["active", "inactive"], index=["active", "inactive"].index(emp_row['status']))
                new_doj = st.date_input("New Date of Joining", pd.to_datetime(emp_row['doj']))
                if st.button("Update Employee"):
                    df.loc[df['id'] == edit_id, ['name', 'email', 'role', 'department', 'status', 'doj']] = [new_name, new_email, new_role, new_dept, new_status, str(new_doj)]
                    save_employee_data(df)
                    st.success(f"Updated employee ID {edit_id}")
            elif edit_id:
                st.warning("Employee ID not found.")

            st.subheader("\U0001F464 User Role Management")
            st.markdown("_Manage login credentials and roles stored in users.txt_")
            user_data = load_users()
            st.write(pd.DataFrame([{"username": u, "role": r["role"]} for u, r in user_data.items()]))

            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            new_user_role = st.selectbox("Role", ["admin", "employee"])
            if st.button("Add User"):
                with open("users.txt", "a") as f:
                    f.write(f"{new_user},{new_pass},{new_user_role}\n")
                st.success(f"User {new_user} added successfully!")

            st.subheader("✏️ Edit Existing User")
            edit_user = st.selectbox("Select User to Edit", list(user_data.keys()))
            new_pass_edit = st.text_input("New Password for User", key="edit_pass")
            new_role_edit = st.selectbox("New Role", ["admin", "employee"], key="edit_role")

            if st.button("Update User"):
                updated_lines = []
                for u, data in user_data.items():
                    if u == edit_user:
                        updated_lines.append(f"{u},{new_pass_edit},{new_role_edit}\n")
                    else:
                        updated_lines.append(f"{u},{data['password']},{data['role']}\n")
                with open("users.txt", "w") as f:
                    f.writelines(updated_lines)
                st.success(f"User {edit_user} updated!")

            st.subheader("❌ Delete User")
            del_user = st.selectbox("Select User to Delete", list(user_data.keys()), key="delete_user")
            if st.button("Delete User"):
                updated_lines = [
                    f"{u},{data['password']},{data['role']}\n"
                    for u, data in user_data.items()
                    if u != del_user
                ]
                with open("users.txt", "w") as f:
                    f.writelines(updated_lines)
                st.success(f"User {del_user} deleted!")
