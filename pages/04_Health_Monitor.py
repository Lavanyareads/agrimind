import streamlit as st
import pandas as pd
import plotly.express as px
from components.auth import require_auth
from database.db_utils import get_livestock_by_user
from models.ml_utils import get_trained_models, calculate_hsi, load_static_data
from utils.styling import get_css, apply_dark, ACCENT, RED, AMBER

st.set_page_config(page_title="Health Monitor", layout="wide")
require_auth()
st.markdown(get_css(), unsafe_allow_html=True)

_, iso, _, _, _, _ = get_trained_models()
df_static = load_static_data()
max_milk = df_static["Milk_Yield_Liters"].max()
max_weight = df_static["Weight_kg"].max()

st.markdown('<div class="page-header"><h1>Herd Health Monitor</h1><p>Anomaly detection and Health Score Index for your livestock.</p></div>', unsafe_allow_html=True)

herd = get_livestock_by_user(st.session_state.user_id)

if not herd:
    st.warning("You have no livestock registered. Please go to 'My Herd' to add animals first.")
    st.stop()

# Prepare data for model
herd_df = pd.DataFrame(herd)
# Assume an average feed quantity for now or ask user for it. Since we don't have daily logs yet, 
# we'll use a placeholder or average feed to run the isolation forest.
# In a full app, this would pull from the daily_logs collection.
herd_df["Feed_Quantity_kg"] = herd_df["weight_kg"] * 0.03 # Rough estimate 3% of body weight for testing

# Run Isolation Forest
X_iso = herd_df[["weight_kg", "milk_yield_liters", "Feed_Quantity_kg"]].rename(columns={
    "weight_kg": "Weight_kg", 
    "milk_yield_liters": "Milk_Yield_Liters"
})
herd_df["Anomaly"] = iso.predict(X_iso)
herd_df["Status"]  = herd_df["Anomaly"].map({1: "Normal", -1: "Alert"})

# Calculate HSI
herd_df["HSI"] = herd_df.apply(lambda row: calculate_hsi(row["milk_yield_liters"], row["weight_kg"], 28, max_milk, max_weight, row["species"]), axis=1)

alerts  = herd_df[herd_df["Anomaly"] == -1]
normals = herd_df[herd_df["Anomaly"] ==  1]

st.markdown('<div class="section-title">Your Herd Status</div>', unsafe_allow_html=True)
a1, a2, a3, a4 = st.columns(4)
a1.metric("Total Animals", len(herd_df))
a2.metric("Status: Normal",  len(normals))
a3.metric("Status: Flagged", len(alerts))
a4.metric("Alert Rate", f"{len(alerts)/len(herd_df)*100:.1f}%")

st.markdown('<div class="section-title">Anomaly Detection Map</div>', unsafe_allow_html=True)
fig = px.scatter(herd_df, x="Feed_Quantity_kg", y="milk_yield_liters",
                 color="Status", size="weight_kg",
                 color_discrete_map={"Normal": ACCENT, "Alert": RED},
                 hover_data=["breed", "species"],
                 labels={"Feed_Quantity_kg": "Estimated Feed (kg)", "milk_yield_liters": "Milk (L/day)"},
                 opacity=0.8)
st.plotly_chart(apply_dark(fig, "Animals flagged by Isolation Forest (deviating from norms)"), use_container_width=True)

if not alerts.empty:
    st.markdown('<div class="section-title">Flagged Animals — Action Required</div>', unsafe_allow_html=True)
    st.dataframe(alerts[["breed", "species", "weight_kg", "milk_yield_liters", "HSI", "Status"]], use_container_width=True)
else:
    st.success("All your animals appear healthy based on the current data!")
