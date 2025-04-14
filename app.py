import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- DASHBOARD (Visible to Admin and Manager) ---
if choice == "Dashboard" and st.session_state["role"] in ["admin", "manager"]:
    st.title("📊 Employee Analytics Dashboard")
    
    # Load data
    emp_df = pd.read_csv("employees.csv")
    att_df = pd.read_csv("attendance.csv")
    
    # Display total metrics with icons
    total_employees = len(emp_df)
    total_attendance = len(att_df)
    total_departments = emp_df["Department"].nunique()
    
    # Display the key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Employees", total_employees, delta=None)
    with col2:
        st.metric("Attendance Records", total_attendance, delta=None)
    with col3:
        st.metric("Departments", total_departments, delta=None)

    # Visualize the number of employees by department
    st.subheader("👥 Employees by Department")
    department_count = emp_df["Department"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=department_count.index, y=department_count.values, ax=ax)
    ax.set_title('Employees by Department')
    ax.set_xlabel('Department')
    ax.set_ylabel('Number of Employees')
    st.pyplot(fig)

    # Visualize Attendance Status (Present/Absent)
    st.subheader("📝 Attendance Status")
    attendance_status = att_df["Status"].value_counts()
    fig2, ax2 = plt.subplots()
    sns.barplot(x=attendance_status.index, y=attendance_status.values, ax=ax2)
    ax2.set_title('Attendance Status')
    ax2.set_xlabel('Status')
    ax2.set_ylabel('Count')
    st.pyplot(fig2)

    # Display the full Employee Data in a better format
    st.subheader("👩‍💼 Employee Details")
    st.dataframe(emp_df.style.format({"Join Date": lambda x: pd.to_datetime(x).strftime("%B %d, %Y")}))

    # Filtered employees by role
    st.subheader("🧾 Employees by Role")
    role_filter = st.selectbox("Filter by Role", ["All"] + emp_df["Role"].unique().tolist())
    if role_filter != "All":
        filtered_emp = emp_df[emp_df["Role"] == role_filter]
        st.dataframe(filtered_emp)
    else:
        st.dataframe(emp_df)

    # Improved data download button
    st.subheader("📄 Export Employee Data")
    csv_employees = emp_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Employee CSV", csv_employees, "employee_export.csv", "text/csv")
