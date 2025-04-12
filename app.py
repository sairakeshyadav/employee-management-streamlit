import streamlit as st
import pandas as pd
import json
from datetime import date

# Sample data
employees = [{"id": "1", "name": "Alice", "email": "alice@example.com", "role": "Manager", "department": "HR", "status": "active", "dateOfJoining": "2023-01-10"}]
attendance = []
leaves = []

st.set_page_config(page_title="Employee Management", layout="wide")
page = st.sidebar.radio("Navigation", ["Dashboard", "Employees", "Attendance", "Leaves"])

if page == "Dashboard":
    st.title("📊 Employee Dashboard")
    df = pd.DataFrame(employees)
    st.bar_chart(df['department'].value_counts())

elif page == "Employees":
    st.title("👥 Employees")
    search = st.text_input("Search by name or email")
    filtered = [e for e in employees if search.lower() in e['name'].lower()]
    st.write(pd.DataFrame(filtered))

elif page == "Attendance":
    st.title("📅 Attendance")
    today = date.today().isoformat()
    for emp in employees:
        status = st.selectbox(f"{emp['name']} status", ["present", "absent"], key=emp['id'])
        if st.button(f"Mark {emp['name']}"):
            attendance.append({"employeeId": emp['id'], "date": today, "status": status})
            st.success(f"{emp['name']} marked as {status}")

elif page == "Leaves":
    st.title("📝 Leave Requests")
    name = st.selectbox("Employee", [e["name"] for e in employees])
    reason = st.text_input("Reason")
    if st.button("Apply"):
        st.success(f"{name} requested leave for: {reason}")
