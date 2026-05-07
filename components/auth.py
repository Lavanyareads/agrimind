import streamlit as st
from database.db_utils import authenticate_user, create_user

def require_auth():
    """To be called at the top of every page to protect it."""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("You must log in to view this page.")
        st.stop()

def login_signup_ui():
    """Renders the login and signup forms."""
    st.markdown('<div class="page-header"><h1>AgriMind Platform</h1><p>Welcome. Please log in or create an account.</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Log In", "Sign Up"])
    
    with tab1:
        st.subheader("Log In")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", type="primary")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    success, user = authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_id = str(user['_id'])
                        st.session_state.username = user['username']
                        st.session_state.farm_name = user['farm_name']
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                        
    with tab2:
        st.subheader("Create an Account")
        with st.form("signup_form"):
            new_username = st.text_input("Choose a Username")
            new_email = st.text_input("Email Address")
            new_farm = st.text_input("Farm Name")
            new_password = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Sign Up", type="primary")
            
            if submitted:
                if not new_username or not new_password or not new_email:
                    st.error("Please fill in all required fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = create_user(new_username, new_email, new_password, new_farm)
                    if success:
                        st.success("Account created successfully! Please log in.")
                    else:
                        st.error(f"Failed: {message}")

def logout_button():
    """Renders a logout button in the sidebar."""
    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.farm_name = None
        st.rerun()
