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

def get_css():
    return f"""
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
      [data-testid="stMultiSelect"] > div,
      [data-testid="stTextInput"] input,
      [data-testid="stPasswordInput"] input {{
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

      /* Alert strips */
      .strip {{ padding: 12px 16px; border-radius: 4px; font-size: 0.84rem; margin: 8px 0; line-height: 1.65; }}
      .strip-red    {{ background: rgba(224,92,75,0.12);  border-left: 3px solid {RED};   color: #F0A89F; }}
      .strip-amber  {{ background: rgba(212,168,67,0.12); border-left: 3px solid {AMBER}; color: #E0C980; }}
      .strip-green  {{ background: rgba(82,183,136,0.12); border-left: 3px solid {ACCENT};color: {ACCENT2}; }}
      .strip-neutral{{ background: {SURFACE2};             border-left: 3px solid {BORDER};color: {TEXT_MID}; }}

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
    """
