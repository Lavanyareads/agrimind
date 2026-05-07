import streamlit as st
import pandas as pd
from components.auth import require_auth
from database.db_utils import add_livestock, get_livestock_by_user
from utils.styling import get_css

st.set_page_config(page_title="My Herd", layout="wide")
require_auth()
st.markdown(get_css(), unsafe_allow_html=True)

st.markdown('<div class="page-header"><h1>My Herd Management</h1><p>Add and view your livestock records here.</p></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["View Herd", "Add New Animal"])

with tab1:
    st.subheader("Your Livestock")
    livestock = get_livestock_by_user(st.session_state.user_id)
    if not livestock:
        st.info("You don't have any animals registered yet. Go to 'Add New Animal' to get started.")
    else:
        df = pd.DataFrame(livestock)
        # Clean up dataframe for display
        df = df.drop(columns=["_id", "user_id"])
        st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Add Livestock Profile")
    with st.form("add_animal_form"):
        c1, c2 = st.columns(2)
        species = c1.selectbox("Species", ["Cow", "Buffalo", "Sheep", "Goat", "Pig", "Horse"])
        breed = c2.text_input("Breed (e.g., Gir, Murrah)")
        state = c1.text_input("Location State")
        age = c2.number_input("Age (Years)", 0.5, 20.0, 4.0, 0.5)
        weight = c1.number_input("Weight (kg)", 100, 1000, 400)
        
        if species in ["Cow", "Buffalo", "Sheep", "Goat"]:
            milk = c2.number_input("Daily Milk Yield (Liters)", 0.0, 40.0, 8.0, 0.5)
        else:
            milk = 0.0
            c2.info(f"{species} is non-dairy. Milk yield set to 0.")
        
        submitted = st.form_submit_button("Add to Herd", type="primary")
        
        if submitted:
            if not breed or not state:
                st.error("Please fill in all required fields.")
            else:
                add_livestock(st.session_state.user_id, species, breed, state, weight, age, milk)
                st.success("Animal added successfully!")
                st.rerun()
