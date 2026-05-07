import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import GradientBoostingRegressor, IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="AgriMind — Livestock Feed Optimizer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DARK DESIGN TOKENS ────────────────────────
BG          = "#0F1612"   # near-black with green tint
SURFACE     = "#161E19"   # cards / sidebar
SURFACE2    = "#1E2B23"   # elevated surfaces
BORDER      = "#2A3D30"   # subtle borders
PRIMARY     = "#2D6A4F"   # medium green
ACCENT      = "#52B788"   # bright green (CTA / highlights)
ACCENT2     = "#74C69D"   # lighter green
TEXT        = "#E8F0EB"   # primary text
TEXT_MID    = "#9DB8A4"   # secondary text
TEXT_DIM    = "#5A7A62"   # muted text
RED         = "#E05C4B"   # alert red
AMBER       = "#D4A843"   # warning amber
CHART_BG    = "#161E19"
GRID        = "#1E2B23"

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor=CHART_BG,
    plot_bgcolor=CHART_BG,
    font=dict(family="Inter, sans-serif", size=12, color=TEXT_MID),
    margin=dict(t=48, b=16, l=16, r=16),
    coloraxis_colorbar=dict(bgcolor=SURFACE2, tickcolor=TEXT_MID, outlinecolor=BORDER),
    xaxis=dict(gridcolor=GRID, linecolor=BORDER, tickcolor=BORDER, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, linecolor=BORDER, tickcolor=BORDER, zerolinecolor=GRID),
)

def apply_dark(fig, title="", height=320):
    fig.update_layout(
        **PLOTLY_DARK,
        height=height,
        title=dict(text=title, font=dict(size=13, color=TEXT, family="Inter, sans-serif")),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, font=dict(color=TEXT_MID)),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=BORDER, tickcolor=BORDER, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, linecolor=BORDER, tickcolor=BORDER, zerolinecolor=GRID)
    return fig

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color:{BG}; color:{TEXT}; }}
  .stApp {{ background-color: {BG}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{ background-color: {SURFACE}; border-right: 1px solid {BORDER}; }}
  [data-testid="stSidebar"] * {{ color: {TEXT_MID} !important; }}
  [data-testid="stSidebar"] hr {{ border-color: {BORDER} !important; margin: 14px 0; }}
  [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background-color: {PRIMARY} !important; border: none !important;
  }}

  /* Inputs */
  [data-testid="stSelectbox"] > div > div,
  [data-testid="stNumberInput"] input,
  [data-testid="stMultiSelect"] > div {{
    background-color: {SURFACE2} !important;
    border-color: {BORDER} !important;
    color: {TEXT} !important;
  }}
  .stSlider [data-baseweb="slider"] {{ background-color: {SURFACE2}; }}

  /* KPI cards */
  [data-testid="metric-container"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-top: 2px solid {ACCENT};
    border-radius: 6px;
    padding: 18px 20px;
  }}
  [data-testid="metric-container"] label {{
    font-size: 0.7rem !important; text-transform: uppercase;
    letter-spacing: 0.08em; color: {TEXT_DIM} !important; font-weight: 600;
  }}
  [data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-size: 1.65rem !important; font-weight: 700 !important; color: {TEXT} !important;
  }}
  [data-testid="metric-container"] [data-testid="stMetricDelta"] svg {{ display:none; }}
  [data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-size: 0.75rem !important; color: {ACCENT2} !important;
  }}

  /* Page header */
  .page-header {{
    padding: 20px 0 12px 0;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 26px;
  }}
  .page-header h1 {{
    font-size: 1.45rem; font-weight: 700; color: {TEXT};
    margin: 0; letter-spacing: -0.01em;
  }}
  .page-header p {{ font-size: 0.82rem; color: {TEXT_DIM}; margin: 5px 0 0 0; }}

  /* Section titles */
  .section-title {{
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: {TEXT_DIM}; margin: 26px 0 14px 0;
    padding-bottom: 8px; border-bottom: 1px solid {BORDER};
  }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 0; border-bottom: 1px solid {BORDER}; background: transparent;
  }}
  .stTabs [data-baseweb="tab"] {{
    font-size: 0.78rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.07em; color: {TEXT_DIM}; background: transparent;
    border: none; border-bottom: 2px solid transparent;
    padding: 10px 22px; margin-bottom: -1px;
  }}
  .stTabs [aria-selected="true"] {{
    color: {ACCENT} !important;
    border-bottom: 2px solid {ACCENT} !important;
    background: transparent !important;
  }}

  /* Alert strips */
  .strip {{ padding: 12px 16px; border-radius: 4px; font-size: 0.84rem; margin: 8px 0; line-height: 1.65; }}
  .strip-red    {{ background: rgba(224,92,75,0.12);  border-left: 3px solid {RED};   color: #F0A89F; }}
  .strip-amber  {{ background: rgba(212,168,67,0.12); border-left: 3px solid {AMBER}; color: #E0C980; }}
  .strip-green  {{ background: rgba(82,183,136,0.12); border-left: 3px solid {ACCENT};color: {ACCENT2}; }}
  .strip-neutral{{ background: {SURFACE2};             border-left: 3px solid {BORDER};color: {TEXT_MID}; }}

  /* Prediction result card */
  .result-card {{
    background: linear-gradient(135deg, {PRIMARY} 0%, #1B4332 100%);
    border: 1px solid {BORDER};
    border-radius: 6px; padding: 28px 24px; text-align: center; margin-bottom: 16px;
  }}
  .result-card .value {{ font-size: 3rem; font-weight: 800; color: {TEXT}; letter-spacing: -0.03em; line-height: 1; }}
  .result-card .unit  {{ font-size: 1rem; color: {ACCENT2}; margin-top: 4px; }}
  .result-card .label {{ font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.12em; color: {TEXT_DIM}; margin-top: 10px; }}

  /* HSI badge */
  .hsi-badge {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 20px; text-align: center;
  }}
  .hsi-badge .score {{ font-size: 2.4rem; font-weight: 800; line-height: 1; }}
  .hsi-badge .sublabel {{ font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em; color: {TEXT_DIM}; margin-top: 4px; }}
  .hsi-badge .tag {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.09em; margin-top: 10px; font-weight: 700; }}

  /* Flagged animals table */
  .styled-table {{ width:100%; border-collapse:collapse; font-size:0.81rem; }}
  .styled-table th {{
    background: {SURFACE2}; color: {TEXT_DIM}; padding: 9px 12px;
    text-align: left; font-weight: 700; font-size: 0.68rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    border-bottom: 1px solid {BORDER};
  }}
  .styled-table td {{ padding: 9px 12px; border-bottom: 1px solid {BORDER}; color: {TEXT_MID}; }}
  .styled-table tr:hover td {{ background: {SURFACE2}; }}
  .pill-alert {{
    background: rgba(224,92,75,0.15); color: {RED};
    border-radius: 20px; padding: 3px 10px; font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.05em;
  }}

  /* Sidebar labels */
  .sb-heading {{
    font-size: 0.66rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: {TEXT_DIM}; margin-bottom: 6px;
  }}

  /* Main bg override for all containers */
  .block-container {{ padding-top: 1.2rem !important; }}
  section[data-testid="stSidebar"] > div {{ padding-top: 1.5rem; }}
  div[data-testid="stVerticalBlock"] > div {{ gap: 0.5rem; }}

  /* Dataframe dark */
  [data-testid="stDataFrame"] {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px; }}

  /* Footer */
  .footer {{
    text-align: center; font-size: 0.68rem; color: {TEXT_DIM};
    padding: 20px 0; border-top: 1px solid {BORDER}; margin-top: 32px;
    text-transform: uppercase; letter-spacing: 0.07em;
  }}

  /* Button */
  .stButton > button[kind="primary"] {{
    background: {PRIMARY}; border: 1px solid {ACCENT}; color: {TEXT};
    font-weight: 600; font-size: 0.82rem; letter-spacing: 0.04em;
    border-radius: 4px; padding: 10px 0;
  }}
  .stButton > button[kind="primary"]:hover {{
    background: {ACCENT}; color: {BG};
  }}
</style>
""", unsafe_allow_html=True)


# ── DATA ──────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("data/india_livestock_feeding_dataset.xlsx")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.month_name()
    df["Feed_per_kg_body"] = df["Feed_Quantity_kg"] / df["Weight_kg"]
    df["Milk_per_kg_feed"]  = df["Milk_Yield_Liters"] / df["Feed_Quantity_kg"]
    df["HSI"] = (
        (df["Milk_Yield_Liters"] / df["Milk_Yield_Liters"].max()) * 50 +
        (df["Weight_kg"]         / df["Weight_kg"].max())          * 30 +
        ((40 - abs(df["Temperature_C"] - 25)) / 40).clip(0, 1)     * 20
    ).clip(0, 100).round(1)
    return df

@st.cache_data
def load_growth_data():
    df = pd.read_csv("data/cow_growth_metrics.csv")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    df.columns = ["Weight_kg", "Height_cm", "Volume_liter", "Feed_Type", "Sunlight"]
    df["Sunlight_label"] = df["Sunlight"].map({"Gt": "High Sunlight", "Lt": "Low Sunlight"})
    return df

@st.cache_resource
def train_models(df):
    le_species = LabelEncoder(); le_breed = LabelEncoder(); le_state = LabelEncoder()
    X = df[["Weight_kg", "Age_Years", "Milk_Yield_Liters", "Temperature_C"]].copy()
    X["Species_enc"] = le_species.fit_transform(df["Species"])
    X["Breed_enc"]   = le_breed.fit_transform(df["Breed"])
    X["State_enc"]   = le_state.fit_transform(df["Location_State"])
    y = df["Feed_Quantity_kg"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    gbr = GradientBoostingRegressor(n_estimators=150, max_depth=4, random_state=42)
    gbr.fit(X_train, y_train)
    mae = mean_absolute_error(y_test, gbr.predict(X_test))
    iso = IsolationForest(contamination=0.1, random_state=42)
    iso.fit(df[["Weight_kg", "Milk_Yield_Liters", "Feed_Quantity_kg"]])
    return gbr, iso, le_species, le_breed, le_state, mae

df        = load_data()
growth_df = load_growth_data()
gbr, iso, le_species, le_breed, le_state, model_mae = train_models(df)


# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="font-size:1.1rem;font-weight:700;color:{TEXT};letter-spacing:0.01em;margin-bottom:2px;">AgriMind</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.72rem;color:{TEXT_DIM};">Livestock Feed Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f'<div class="sb-heading">Dataset Filters</div>', unsafe_allow_html=True)
    sel_species = st.multiselect("Species", df["Species"].unique(),        default=list(df["Species"].unique()))
    sel_state   = st.multiselect("State",   df["Location_State"].unique(), default=list(df["Location_State"].unique()))
    sel_breed   = st.multiselect("Breed",   df["Breed"].unique(),          default=list(df["Breed"].unique()))
    st.markdown("---")
    st.markdown(f'<div class="sb-heading">Economic Parameters</div>', unsafe_allow_html=True)
    feed_cost  = st.slider("Feed cost (Rs/kg)",     10, 30, 18)
    milk_price = st.slider("Milk price (Rs/liter)", 30, 80, 50)
    herd_size  = st.slider("Herd size",              5, 50, 20)
    st.markdown("---")
    st.markdown(f'<div style="font-size:0.68rem;color:{TEXT_DIM};">Model MAE: {model_mae:.3f} kg &nbsp;|&nbsp; Records: {len(df)}</div>', unsafe_allow_html=True)

filtered = df[
    df["Species"].isin(sel_species) &
    df["Location_State"].isin(sel_state) &
    df["Breed"].isin(sel_breed)
]
if filtered.empty:
    st.warning("No records match the current filters.")
    st.stop()


# ── PAGE HEADER ───────────────────────────────
st.markdown(f"""
<div class="page-header">
  <h1>Livestock Feed Optimizer</h1>
  <p>AI-powered feeding recommendations for Indian cattle and buffalo &mdash; Gradient Boosting + Isolation Forest</p>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────
avg_feed     = filtered["Feed_Quantity_kg"].mean()
avg_milk     = filtered["Milk_Yield_Liters"].mean()
avg_hsi      = filtered["HSI"].mean()
daily_rev    = avg_milk * milk_price
daily_cost   = avg_feed * feed_cost
daily_profit = daily_rev - daily_cost

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avg Feed / Animal",      f"{avg_feed:.1f} kg")
k2.metric("Avg Milk Yield",         f"{avg_milk:.1f} L/day")
k3.metric("Avg Health Score",       f"{avg_hsi:.0f} / 100")
k4.metric("Daily Revenue / Animal", f"Rs {daily_rev:.0f}")
k5.metric("Daily Profit / Animal",  f"Rs {daily_profit:.0f}",
          delta=f"Rs {daily_profit * herd_size:,.0f} full herd")

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)


# ── TABS ──────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Feed Predictor", "Health Monitor", "Growth Analysis"])


# ════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Breed and State Performance</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        breed_avg = filtered.groupby("Breed")["Feed_Quantity_kg"].mean().sort_values()
        fig = px.bar(breed_avg, orientation="h",
                     labels={"value": "Feed (kg/day)", "index": "Breed"})
        fig.update_traces(marker_color=PRIMARY, marker_line_width=0)
        fig.update_traces(marker=dict(color=breed_avg.values,
                          colorscale=[[0, PRIMARY],[1, ACCENT]]))
        st.plotly_chart(apply_dark(fig, "Average Daily Feed by Breed"), use_container_width=True)

    with c2:
        state_avg = filtered.groupby("Location_State")["Milk_Yield_Liters"].mean().sort_values()
        fig = px.bar(state_avg, orientation="h",
                     labels={"value": "Milk (L/day)", "index": "State"})
        fig.update_traces(marker=dict(color=state_avg.values,
                          colorscale=[[0, "#1B4332"],[1, ACCENT2]]))
        st.plotly_chart(apply_dark(fig, "Average Milk Yield by State"), use_container_width=True)

    st.markdown('<div class="section-title">Efficiency and Temperature Analysis</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        fig = px.scatter(filtered, x="Temperature_C", y="Feed_Quantity_kg",
                         color="Species", size="Weight_kg",
                         labels={"Temperature_C": "Temperature (C)", "Feed_Quantity_kg": "Feed (kg)"},
                         color_discrete_map={"Cow": ACCENT, "Buffalo": "#5B8FD4"},
                         opacity=0.7)
        st.plotly_chart(apply_dark(fig, "Temperature vs Feed Quantity"), use_container_width=True)

    with c4:
        eff = filtered.groupby("Breed")["Milk_per_kg_feed"].mean().sort_values(ascending=False)
        fig = px.bar(eff, labels={"value": "L per kg feed", "index": "Breed"})
        fig.update_traces(marker=dict(color=eff.values,
                          colorscale=[[0, "#5C3D0D"],[1, AMBER]]))
        st.plotly_chart(apply_dark(fig, "Feed Efficiency — Milk Produced per kg of Feed"), use_container_width=True)

    st.markdown('<div class="section-title">Monthly Trends</div>', unsafe_allow_html=True)
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    monthly = (filtered.groupby("Month")
               .agg(Avg_Feed=("Feed_Quantity_kg","mean"), Avg_Milk=("Milk_Yield_Liters","mean"))
               .reindex(month_order).dropna())

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Feed (kg)", x=monthly.index, y=monthly["Avg_Feed"],
                         marker_color=PRIMARY, marker_line_width=0, yaxis="y"))
    fig.add_trace(go.Scatter(name="Milk (L)", x=monthly.index, y=monthly["Avg_Milk"],
                             mode="lines+markers", yaxis="y2",
                             line=dict(color=AMBER, width=2.5),
                             marker=dict(size=6, color=AMBER, line=dict(width=1.5, color=BG))))
    layout_config = PLOTLY_DARK.copy()

    layout_config["yaxis"] = dict(
        title=dict(text="Feed (kg)", font=dict(color=ACCENT)),
        tickfont=dict(color=TEXT_DIM),
        gridcolor=GRID,
        linecolor=BORDER
    )

    layout_config["yaxis2"] = dict(
        title=dict(text="Milk (L)", font=dict(color=AMBER)),
        tickfont=dict(color=TEXT_DIM),
        overlaying="y",
        side="right",
        gridcolor="rgba(0,0,0,0)",
        linecolor=BORDER
    )

    fig.update_layout(
        **layout_config,
        height=340,
        title=dict(
            text="Monthly Average — Feed Quantity vs Milk Yield",
            font=dict(size=13, color=TEXT, family="Inter, sans-serif")
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER,
            font=dict(color=TEXT_MID),
            orientation="h",
            y=1.08,
            x=0
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# TAB 2 — FEED PREDICTOR
# ════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Animal Input Parameters</div>', unsafe_allow_html=True)
    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        p_species = st.selectbox("Species",        ["Cow", "Buffalo"])
        p_breed   = st.selectbox("Breed",          sorted(df["Breed"].unique()))
        p_state   = st.selectbox("Location State", sorted(df["Location_State"].unique()))
        fc1, fc2  = st.columns(2)
        p_weight  = fc1.number_input("Weight (kg)",        300, 750, 480, step=5)
        p_age     = fc2.number_input("Age (years)",        0.5, 15.0, 4.0, step=0.5)
        fc3, fc4  = st.columns(2)
        p_milk    = fc3.number_input("Milk Yield (L/day)", 0.0, 25.0, 8.0, step=0.5)
        p_temp    = fc4.number_input("Temperature (C)",    10,  45,   28)
        run = st.button("Run Prediction", use_container_width=True, type="primary")

    with col_result:
        if run:
            try:   sp_enc = le_species.transform([p_species])[0]
            except: sp_enc = 0
            try:   br_enc = le_breed.transform([p_breed])[0]
            except: br_enc = 0
            try:   st_enc = le_state.transform([p_state])[0]
            except: st_enc = 0

            X_pred = pd.DataFrame([[p_weight, p_age, p_milk, p_temp, sp_enc, br_enc, st_enc]],
                                   columns=["Weight_kg","Age_Years","Milk_Yield_Liters",
                                            "Temperature_C","Species_enc","Breed_enc","State_enc"])
            pred_feed = gbr.predict(X_pred)[0]
            roughage  = round(pred_feed * 0.6, 2)
            conc      = round(pred_feed * 0.4, 2)

            hsi_val = min(100, max(0,
                (p_milk   / df["Milk_Yield_Liters"].max()) * 50 +
                (p_weight / df["Weight_kg"].max())          * 30 +
                max(0, (40 - abs(p_temp - 25)) / 40)        * 20
            ))
            hsi_color = ACCENT  if hsi_val >= 75 else (AMBER if hsi_val >= 50 else RED)
            hsi_label = "HEALTHY" if hsi_val >= 75 else ("MONITOR" if hsi_val >= 50 else "CRITICAL")

            st.markdown(f"""
            <div class="result-card">
              <div class="label">Recommended Daily Feed</div>
              <div class="value">{pred_feed:.2f}</div>
              <div class="unit">kg / day</div>
            </div>""", unsafe_allow_html=True)

            r1, r2 = st.columns(2)
            r1.metric("Roughage",    f"{roughage} kg", "60%")
            r2.metric("Concentrate", f"{conc} kg",     "40%")

            st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="hsi-badge">
              <div class="score" style="color:{hsi_color}">{hsi_val:.0f}</div>
              <div class="sublabel">Health Score Index (HSI)</div>
              <div class="tag" style="color:{hsi_color}">{hsi_label}</div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
            daily_cost_ = pred_feed * feed_cost
            daily_rev_  = p_milk    * milk_price
            monthly_net = (daily_rev_ - daily_cost_) * 30
            pclass = "strip-green" if monthly_net > 0 else "strip-red"
            st.markdown(f"""
            <div class="strip {pclass}">
              <strong>Monthly Economic Estimate (per animal)</strong><br>
              Feed cost: Rs {daily_cost_*30:,.0f} &nbsp;&nbsp;&nbsp;
              Milk revenue: Rs {daily_rev_*30:,.0f} &nbsp;&nbsp;&nbsp;
              Net profit: <strong>Rs {monthly_net:,.0f}</strong>
            </div>""", unsafe_allow_html=True)
                        # ── FEEDING SCHEDULER ─────────────────────
            st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="section-title">Smart Feeding Scheduler</div>
            """, unsafe_allow_html=True)

            morning_feed = round(pred_feed * 0.4, 2)
            afternoon_feed = round(pred_feed * 0.2, 2)
            evening_feed = round(pred_feed * 0.4, 2)

            schedule_df = pd.DataFrame({
                "Time": ["6:00 AM", "1:00 PM", "7:00 PM"],
                "Feed Quantity (kg)": [
                    morning_feed,
                    afternoon_feed,
                    evening_feed
                ],
                "Feed Type": [
                    "Roughage + Minerals",
                    "Light Concentrate",
                    "Roughage + Concentrate"
                ]
            })

            st.dataframe(schedule_df, use_container_width=True)

            # Water recommendation
            water_needed = round(pred_feed * 4.5, 1)

            st.markdown(f"""
            <div class="strip strip-green">
              <strong>Daily Care Recommendation</strong><br>
              Recommended water intake: <strong>{water_needed} liters/day</strong><br>
              Best feeding practice: Divide meals into 3 sessions for better digestion and milk productivity.
            </div>
            """, unsafe_allow_html=True)
        else:
            feat_names  = ["Weight","Age","Milk Yield","Temperature","Species","Breed","State"]
            importances = gbr.feature_importances_
            fig = px.bar(x=importances, y=feat_names, orientation="h",
                         labels={"x": "Relative Importance", "y": ""})
            fig.update_traces(marker=dict(color=importances,
                              colorscale=[[0, PRIMARY],[1, ACCENT]]))
            st.plotly_chart(apply_dark(fig, "Gradient Boosting — Predictor Weights", height=300),
                            use_container_width=True)
            st.markdown(f"""
            <div class="strip strip-neutral">
              Fill in the parameters on the left and click <strong>Run Prediction</strong>
              to get the AI-recommended feed quantity. &nbsp; Model accuracy: MAE = {model_mae:.3f} kg
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# TAB 3 — HEALTH MONITOR
# ════════════════════════════════════════════
with tab3:
    sample = filtered.sample(min(150, len(filtered)), random_state=42).copy()
    X_iso  = sample[["Weight_kg", "Milk_Yield_Liters", "Feed_Quantity_kg"]]
    sample["Anomaly"] = iso.predict(X_iso)
    sample["Status"]  = sample["Anomaly"].map({1: "Normal", -1: "Alert"})
    alerts  = sample[sample["Anomaly"] == -1]
    normals = sample[sample["Anomaly"] ==  1]

    st.markdown('<div class="section-title">Herd Status Summary</div>', unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Animals Sampled", len(sample))
    a2.metric("Status: Normal",  len(normals))
    a3.metric("Status: Flagged", len(alerts))
    a4.metric("Alert Rate",      f"{len(alerts)/len(sample)*100:.1f}%")

    st.markdown('<div class="section-title">Anomaly Detection Map — Feed vs Milk Yield</div>', unsafe_allow_html=True)
    fig = px.scatter(sample, x="Feed_Quantity_kg", y="Milk_Yield_Liters",
                     color="Status", size="Weight_kg",
                     color_discrete_map={"Normal": ACCENT, "Alert": RED},
                     hover_data=["Breed", "Species", "Location_State", "Temperature_C"],
                     labels={"Feed_Quantity_kg": "Feed (kg/day)", "Milk_Yield_Liters": "Milk (L/day)",
                             "Status": "Status"},
                     opacity=0.8)
    st.plotly_chart(apply_dark(fig,
        "Animals flagged by Isolation Forest deviate significantly from herd norms",
        height=400), use_container_width=True)

    st.markdown('<div class="section-title">Health Score Index (HSI) Distribution</div>', unsafe_allow_html=True)
    fig = px.histogram(filtered, x="HSI", nbins=25, color="Species",
                       color_discrete_map={"Cow": ACCENT, "Buffalo": "#5B8FD4"},
                       labels={"HSI": "Health Score Index (0–100)", "count": "Animals"},
                       barmode="overlay", opacity=0.75)
    fig.add_vline(x=75, line_dash="dash", line_color=ACCENT, line_width=1.5,
                  annotation_text="Healthy", annotation_font_color=ACCENT, annotation_font_size=11)
    fig.add_vline(x=50, line_dash="dash", line_color=RED,    line_width=1.5,
                  annotation_text="Critical", annotation_font_color=RED,  annotation_font_size=11)
    st.plotly_chart(apply_dark(fig,
        "HSI combines milk efficiency, body weight, and temperature resilience",
        height=340), use_container_width=True)

    if not alerts.empty:
        st.markdown('<div class="section-title">Flagged Animals — Action Required</div>', unsafe_allow_html=True)
        rows_html = ""
        for _, row in alerts.head(10).iterrows():
            avg_fb = filtered[filtered["Breed"] == row["Breed"]]["Feed_Quantity_kg"].mean()
            diff   = row["Feed_Quantity_kg"] - avg_fb
            diff_s = f"+{abs(diff):.1f} kg above avg" if diff > 0 else f"{abs(diff):.1f} kg below avg"
            hsi_c  = ACCENT if row["HSI"] >= 75 else (AMBER if row["HSI"] >= 50 else RED)
            rows_html += f"""
            <tr>
              <td>{row['Breed']}</td><td>{row['Species']}</td>
              <td>{row['Location_State']}</td><td>{row['Temperature_C']} C</td>
              <td>{row['Feed_Quantity_kg']:.1f} kg &nbsp;
                <span style='color:{AMBER};font-size:0.72rem'>({diff_s})</span></td>
              <td>{row['Milk_Yield_Liters']:.1f} L</td>
              <td><span style='color:{hsi_c};font-weight:700'>{row['HSI']:.0f}</span></td>
              <td><span class="pill-alert">ALERT</span></td>
            </tr>"""
        st.markdown(f"""
        <table class="styled-table">
          <thead><tr>
            <th>Breed</th><th>Species</th><th>State</th><th>Temp</th>
            <th>Feed</th><th>Milk</th><th>HSI</th><th>Status</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table><br>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# TAB 4 — GROWTH ANALYSIS
# ════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Growth Metrics by Feed Type and Sunlight</div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)

    with g1:
        fig = px.box(growth_df, x="Feed_Type", y="Weight_kg", color="Feed_Type",
                     color_discrete_map={"A": ACCENT, "B": "#5B8FD4"},
                     labels={"Weight_kg": "Weight (kg)", "Feed_Type": "Feed Type"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(apply_dark(fig, "Body Weight Distribution by Feed Type", height=340),
                        use_container_width=True)

    with g2:
        fig = px.scatter(growth_df, x="Height_cm", y="Volume_liter",
                         color="Sunlight_label", size="Weight_kg",
                         color_discrete_map={"High Sunlight": AMBER, "Low Sunlight": "#5B8FD4"},
                         labels={"Height_cm": "Height (cm)", "Volume_liter": "Feed Volume (L)",
                                 "Sunlight_label": "Sunlight"},
                         opacity=0.75)
        st.plotly_chart(apply_dark(fig, "Height vs Feed Volume by Sunlight Level", height=340),
                        use_container_width=True)

    st.markdown('<div class="section-title">Weight vs Feed Volume Correlation</div>', unsafe_allow_html=True)
    g3, g4 = st.columns(2)

    with g3:
        fig = px.scatter(growth_df, x="Weight_kg", y="Volume_liter",
                         color="Feed_Type", trendline="ols",
                         color_discrete_map={"A": ACCENT, "B": "#5B8FD4"},
                         labels={"Weight_kg": "Weight (kg)", "Volume_liter": "Feed Volume (L)"},
                         opacity=0.7)
        st.plotly_chart(apply_dark(fig, "Body Weight vs Feed Volume — OLS Trendline", height=320),
                        use_container_width=True)

    with g4:
        summary = (growth_df.groupby(["Feed_Type","Sunlight_label"])
                   .agg(Avg_Weight=("Weight_kg","mean")).round(1).reset_index())
        fig = px.bar(summary, x="Feed_Type", y="Avg_Weight", color="Sunlight_label", barmode="group",
                     color_discrete_map={"High Sunlight": AMBER, "Low Sunlight": "#5B8FD4"},
                     labels={"Avg_Weight": "Avg Weight (kg)", "Feed_Type": "Feed Type",
                             "Sunlight_label": "Sunlight"})
        st.plotly_chart(apply_dark(fig, "Average Body Weight — Feed Type vs Sunlight Exposure", height=320),
                        use_container_width=True)

    st.markdown('<div class="section-title">Dataset Summary Statistics</div>', unsafe_allow_html=True)
    st.dataframe(growth_df[["Weight_kg","Height_cm","Volume_liter"]].describe().round(2),
                 use_container_width=True)


# ── FOOTER ────────────────────────────────────
st.markdown(f"""
<div class="footer">
  AgriMind &nbsp;&mdash;&nbsp; Gradient Boosting + Isolation Forest &nbsp;&mdash;&nbsp;
  500 livestock records across 6 Indian states &nbsp;&mdash;&nbsp; Streamlit + Plotly
</div>""", unsafe_allow_html=True)