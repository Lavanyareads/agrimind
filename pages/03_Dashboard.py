import streamlit as st
import pandas as pd
import plotly.express as px
from components.auth import require_auth
from models.ml_utils import load_static_data
from utils.styling import get_css, apply_dark, PRIMARY, ACCENT, ACCENT2, AMBER, GRID, BORDER, TEXT_DIM, TEXT_MID

st.set_page_config(page_title="Global Dashboard", layout="wide")
require_auth()
st.markdown(get_css(), unsafe_allow_html=True)

df = load_static_data()

st.markdown('<div class="page-header"><h1>Global Insights Dashboard</h1><p>Explore feed and milk trends across the general dataset.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Breed and State Performance</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    breed_avg = df.groupby("Breed")["Feed_Quantity_kg"].mean().sort_values()
    fig = px.bar(breed_avg, orientation="h", labels={"value": "Feed (kg/day)", "index": "Breed"})
    fig.update_traces(marker=dict(color=breed_avg.values, colorscale=[[0, PRIMARY],[1, ACCENT]]))
    st.plotly_chart(apply_dark(fig, "Average Daily Feed by Breed"), use_container_width=True)

with c2:
    state_avg = df.groupby("Location_State")["Milk_Yield_Liters"].mean().sort_values()
    fig = px.bar(state_avg, orientation="h", labels={"value": "Milk (L/day)", "index": "State"})
    fig.update_traces(marker=dict(color=state_avg.values, colorscale=[[0, "#1B4332"],[1, ACCENT2]]))
    st.plotly_chart(apply_dark(fig, "Average Milk Yield by State"), use_container_width=True)

st.markdown('<div class="section-title">Efficiency and Temperature Analysis</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    fig = px.scatter(df, x="Temperature_C", y="Feed_Quantity_kg", color="Species", size="Weight_kg",
                     color_discrete_map={"Cow": ACCENT, "Buffalo": "#5B8FD4"}, opacity=0.7)
    st.plotly_chart(apply_dark(fig, "Temperature vs Feed Quantity"), use_container_width=True)

with c4:
    eff = df.groupby("Breed")["Milk_per_kg_feed"].mean().sort_values(ascending=False)
    fig = px.bar(eff, labels={"value": "L per kg feed", "index": "Breed"})
    fig.update_traces(marker=dict(color=eff.values, colorscale=[[0, "#5C3D0D"],[1, AMBER]]))
    st.plotly_chart(apply_dark(fig, "Feed Efficiency (Milk per kg Feed)"), use_container_width=True)
