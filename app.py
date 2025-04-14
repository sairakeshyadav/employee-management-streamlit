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
                if new_username and new_password:
                    try:
                        execute_query(
                            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                            (new_username, new_password, new_role),
                        )
                        st.success(f"User '{new_username}' added successfully!")
                    except Exception as e:
                        st.error(f"Error adding user: {e}")
                else:
                    st.warning("Please provide both username and password.")

            # Reset Password
            st.subheader("Reset Password")
            reset_username = st.text_input("Username to Reset", key="reset_username")
            reset_new_password = st.text_input(
                "New Password", type="password", placeholder="Enter new password", key="reset_new_password"
            )
            if st.button("Reset Password"):
                if reset_username and reset_new_password:
                    try:
                        execute_query(
                            "UPDATE users SET password = ? WHERE username = ?",
                            (reset_new_password, reset_username),
                        )
                        st.success(f"Password for '{reset_username}' has been reset.")
                    except Exception as e:
                        st.error(f"Error resetting password: {e}")
                else:
                    st.warning("Please provide both username and new password.")

            # Delete User
            st.subheader("Delete User")
            delete_username = st.text_input("Username to Delete", key="delete_username")
            if st.button("Delete User"):
                if delete_username:
                    try:
                        execute_query("DELETE FROM users WHERE username = ?", (delete_username,))
                        st.success(f"User '{delete_username}' has been deleted.")
                    except Exception as e:
                        st.error(f"Error deleting user: {e}")
                else:
                    st.warning("Please provide a username to delete.")

            # Show Existing Users
            st.subheader("Existing Users")
            try:
                user_df = load_data("SELECT * FROM users")
                if not user_df.empty:
                    st.dataframe(user_df)
                else:
                    st.info("No users found.")
            except Exception as e:
                st.error(f"Error loading user data: {e}")
