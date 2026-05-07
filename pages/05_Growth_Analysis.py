import streamlit as st
import plotly.express as px
from components.auth import require_auth
from models.ml_utils import load_growth_data
from utils.styling import get_css, apply_dark, ACCENT, AMBER

st.set_page_config(page_title="Growth Analysis", layout="wide")
require_auth()
st.markdown(get_css(), unsafe_allow_html=True)

growth_df = load_growth_data()

st.markdown('<div class="page-header"><h1>Global Growth Analysis</h1><p>Understand how feed types and sunlight impact animal growth.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Growth Metrics by Feed Type and Sunlight</div>', unsafe_allow_html=True)
g1, g2 = st.columns(2)

with g1:
    fig = px.box(growth_df, x="Feed_Type", y="Weight_kg", color="Feed_Type",
                 color_discrete_map={"A": ACCENT, "B": "#5B8FD4"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(apply_dark(fig, "Body Weight Distribution by Feed Type", height=340), use_container_width=True)

with g2:
    fig = px.scatter(growth_df, x="Height_cm", y="Volume_liter",
                     color="Sunlight_label", size="Weight_kg",
                     color_discrete_map={"High Sunlight": AMBER, "Low Sunlight": "#5B8FD4"},
                     opacity=0.75)
    st.plotly_chart(apply_dark(fig, "Height vs Feed Volume by Sunlight Level", height=340), use_container_width=True)

st.markdown('<div class="section-title">Weight vs Feed Volume Correlation</div>', unsafe_allow_html=True)
g3, g4 = st.columns(2)

with g3:
    fig = px.scatter(growth_df, x="Weight_kg", y="Volume_liter", color="Feed_Type", trendline="ols",
                     color_discrete_map={"A": ACCENT, "B": "#5B8FD4"}, opacity=0.7)
    st.plotly_chart(apply_dark(fig, "Body Weight vs Feed Volume — OLS Trendline", height=320), use_container_width=True)

with g4:
    summary = (growth_df.groupby(["Feed_Type","Sunlight_label"])
               .agg(Avg_Weight=("Weight_kg","mean")).round(1).reset_index())
    fig = px.bar(summary, x="Feed_Type", y="Avg_Weight", color="Sunlight_label", barmode="group",
                 color_discrete_map={"High Sunlight": AMBER, "Low Sunlight": "#5B8FD4"})
    st.plotly_chart(apply_dark(fig, "Average Body Weight — Feed Type vs Sunlight", height=320), use_container_width=True)
