def login():
    """Display the login interface and handle authentication."""
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Login"):
        try:
            query = "SELECT username, password, role FROM users WHERE username = ?"
            user_df = load_data(query, (username,))
            if not user_df.empty:
                user = user_df.iloc[0]
                # Convert the hashed password to bytes
                hashed_password = user["password"].encode('utf-8') if isinstance(user["password"], str) else user["password"]
                if verify_password(password, hashed_password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user["username"]
                    st.session_state["role"] = user["role"]
                    st.success(f"Welcome, {username}!")
                else:
                    st.error("Invalid password. Please try again.")
            else:
                st.error("Invalid username. Please try again.")
        except Exception as e:
            st.error(f"An error occurred during login: {e}")
