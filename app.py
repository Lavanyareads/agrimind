import streamlit as st
from components.auth import login_signup_ui, logout_button
from utils.styling import get_css

st.set_page_config(
    page_title="AgriMind — Livestock Feed Optimizer",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_css(), unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_signup_ui()
else:
    st.sidebar.markdown(f"### Welcome, {st.session_state.username}")
    st.sidebar.markdown(f"**Farm:** {st.session_state.farm_name}")
    logout_button()
    
    st.markdown(f"""
    <div class="page-header">
      <h1>AgriMind Dashboard</h1>
      <p>Welcome back to {st.session_state.farm_name}'s management console.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("👈 Please select a page from the sidebar to manage your herd, view predictions, or monitor health.")