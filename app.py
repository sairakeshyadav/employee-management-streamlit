import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import gspread
from datetime import date
import json
from google.oauth2.service_account import Credentials

# --- AUTH SETUP ---
users = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": stauth.Hasher(["adminpass"]).generate()[0]
        },
        "employee": {
            "name": "Employee",
            "password": stauth.Hasher(["employeepass"]).generate()[0]
        }
    }
}

authenticator = stauth.Authenticate(
    users["usernames"],
    "employee_app_cookie", "abcdef", cookie_expiry_days=1
)

name, auth_status, username = authenticator.login("Login", "main")

# --- LOGIN SCREEN CENTERED ---
if auth_status is None:
    st.markdown(
        """
        <style>
        .block-container { display: flex; justify-content: center; align-items: center; height: 90vh; }
        </style>
        """, unsafe_allow_html=True
    )
    st.warning("Please enter your username and password")
elif auth_status is False:
    st.error("Username/password incorrect")

# --- GOOGLE SHEET CONNECTION ---
@st.cache_resource

def load_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("EmployeeData").worksheet("Employees")

sheet = load_gsheet()

# --- LOGGED IN VIEW ---
if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name} \U0001F44B")

    # --- MAIN TABS ---
    tabs = st.tabs(["\U0001F4CA Dashboard", "\U0001F4C5 Attendance", "\U0001F4DD Leaves", "\U0001F465 Employees"])

    # Load employee data
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

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
            name = st.selectbox("Select Employee", df['name'])
            reason = st.text_input("Reason for Leave")
            if st.button("Apply for Leave"):
                st.success(f"{name} applied for leave: {reason}")
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
            new_row = [str(len(df)+1), new_name, new_email, new_role, new_dept, new_status, str(new_doj)]
            sheet.append_row(new_row)
            st.success(f"Added {new_name} to the employee list!")

        st.subheader("\u274C Delete Employee by ID")
        del_id = st.text_input("Enter Employee ID to Delete")
        if st.button("Delete"):
            records = sheet.get_all_records()
            for i, row in enumerate(records):
                if row["id"] == del_id:
                    sheet.delete_rows(i + 2)
                    st.success(f"Deleted employee ID {del_id}")
                    break
            else:
                st.error("ID not found")
