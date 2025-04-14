import streamlit as st
import pandas as pd
from datetime import date
import os

# --- AUTH SETUP USING FILE ---
def load_users():
    default_user = "admin,admin123,admin"
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.write(default_user + "\n")
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

# --- DATA SETUP ---
if not os.path.exists("employees.csv"):
    pd.DataFrame(columns=["ID", "Name", "Department", "Join Date", "Role"]).to_csv("employees.csv", index=False)
if not os.path.exists("attendance.csv"):
    pd.DataFrame(columns=["ID", "Name", "Date", "Status"]).to_csv("attendance.csv", index=False)

# --- LOGIN ---
def login(users):
    st.title("👥 Employee Manager Login")
    if "login_failed" not in st.session_state:
        st.session_state.login_failed = False

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = users[username]["role"]
                st.session_state.login_failed = False
                st.success("Login successful. Please reload the page.")
                st.stop()
            else:
                st.session_state.login_failed = True

    if st.session_state.login_failed:
        st.error("Invalid credentials")

# --- MAIN APP ---
users = load_users()
if "logged_in" not in st.session_state:
    login(users)
else:
    st.sidebar.title("Navigation")
    tabs = ["Dashboard", "Attendance", "Employees", "Leave Management"]
    if st.session_state["role"] == "admin":
        tabs.append("Admin Panel")

    choice = st.sidebar.radio("Go to", tabs)

    st.sidebar.write(f"Logged in as: {st.session_state['username']} ({st.session_state['role']})")
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "username", "role"]:
            if key in st.session_state:
                del st.session_state[key]
        st.stop()

    if choice == "Dashboard":
        st.title("📊 Employee Analytics Dashboard")
        emp_df = pd.read_csv("employees.csv")
        att_df = pd.read_csv("attendance.csv")
        st.metric("Total Employees", len(emp_df))
        st.metric("Attendance Records", len(att_df))
        st.dataframe(emp_df.describe(include='all'))

    elif choice == "Attendance":
        st.title("🗕️ Attendance Tracking")
        att_df = pd.read_csv("attendance.csv")
        st.dataframe(att_df)
        st.subheader("📄 Export Attendance Data")
        if not att_df.empty:
            csv_attendance = att_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Attendance CSV", csv_attendance, "attendance_export.csv", "text/csv")
        else:
            st.info("No attendance data available to export.")

    elif choice == "Employees":
        st.title("🧾 Employee Directory")
        emp_df = pd.read_csv("employees.csv")
        if not emp_df.empty:
            department_filter = st.selectbox("Filter by Department", ["All"] + emp_df["Department"].unique().tolist())
            if department_filter != "All":
                filtered = emp_df[emp_df["Department"] == department_filter]
            else:
                filtered = emp_df
            st.dataframe(filtered)
            st.subheader("📄 Export Employee Data")
            csv_employees = filtered.to_csv(index=False).encode("utf-8")
            st.download_button("Download Employee CSV", csv_employees, "employee_export.csv", "text/csv")
        else:
            st.info("No employee data to export.")

    elif choice == "Leave Management":
        st.title("📝 Leave Management")
        if not os.path.exists("leaves.csv"):
            pd.DataFrame(columns=["Username", "From", "To", "Reason", "Status"]).to_csv("leaves.csv", index=False)
        leave_df = pd.read_csv("leaves.csv")

        st.subheader("Apply for Leave")
        with st.form("leave_form"):
            from_date = st.date_input("From Date")
            to_date = st.date_input("To Date")
            reason = st.text_area("Reason")
            submit_leave = st.form_submit_button("Submit")
            if submit_leave:
                new_leave = pd.DataFrame([[st.session_state['username'], from_date, to_date, reason, "Pending"]],
                                         columns=["Username", "From", "To", "Reason", "Status"])
                leave_df = pd.concat([leave_df, new_leave], ignore_index=True)
                leave_df.to_csv("leaves.csv", index=False)
                st.success("Leave request submitted.")

        st.subheader("Leave History")
        st.dataframe(leave_df[leave_df["Username"] == st.session_state["username"]])

    elif choice == "Admin Panel" and st.session_state["role"] == "admin":
        st.title("⚙️ Admin Panel")

        st.subheader("Add New Employee")
        with st.form("add_emp"):
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Name")
            dept = st.text_input("Department")
            join = st.date_input("Join Date", date.today())
            role = st.selectbox("Role", ["employee", "admin"])
            submitted = st.form_submit_button("Add Employee")
            if submitted:
                new_emp = pd.DataFrame([[emp_id, name, dept, join, role]],
                                       columns=["ID", "Name", "Department", "Join Date", "Role"])
                emp_df = pd.read_csv("employees.csv")
                emp_df = pd.concat([emp_df, new_emp], ignore_index=True)
                emp_df.to_csv("employees.csv", index=False)
                st.success("Employee added!")

        st.subheader("Add New User")
        with st.form("add_user"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["employee", "admin"])
            add_user_btn = st.form_submit_button("Add User")
            if add_user_btn:
                with open("users.txt", "a") as f:
                    f.write(f"{new_user},{new_pass},{new_role}\n")
                st.success("User added!")
                users = load_users()  # Reload users after adding new one

        st.subheader("Review Leave Requests")
        leave_df = pd.read_csv("leaves.csv")
        for idx, row in leave_df[leave_df["Status"] == "Pending"].iterrows():
            st.write(f"User: {row['Username']} | From: {row['From']} | To: {row['To']} | Reason: {row['Reason']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Approve {idx}"):
                    leave_df.at[idx, "Status"] = "Approved"
            with col2:
                if st.button(f"Reject {idx}"):
                    leave_df.at[idx, "Status"] = "Rejected"
        leave_df.to_csv("leaves.csv", index=False)
        st.success("Leave requests updated.")
