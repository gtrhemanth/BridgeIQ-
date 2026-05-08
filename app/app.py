"""
BridgeIQ — AI-Powered Business Intelligence & Process Transformation Platform
Built by: Sai Hemanth | Technical BA Portfolio Project
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="BridgeIQ | Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bridgeiq.db")
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Force sidebar open via JavaScript on every page load
# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Style header to match dark theme — DO NOT change color of children (breaks sidebar toggle icon) */
header[data-testid="stHeader"] { background: #0f1117 !important; }
[data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Hide the collapse arrow INSIDE sidebar so it can never be accidentally closed */
[data-testid="stSidebar"] button[data-testid="stBaseButton-header"],
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
[data-testid="stSidebarNavCloseButton"],
[data-testid="stSidebar"] button[kind="header"] {
    display: none !important;
}

/* ── Animations ──────────────────────────────────────────────────────────────── */
@keyframes pulse-dot {
    0%,100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.6); }
    50%      { box-shadow: 0 0 0 7px rgba(34,197,94,0); }
}
@keyframes slide-up {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes gradient-x {
    0%,100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
}
@keyframes danger-flash {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); }
    50%      { box-shadow: 0 0 0 8px rgba(239,68,68,0); }
}
@keyframes border-glow {
    0%,100% { box-shadow: 0 0 8px rgba(79,142,247,0.15), inset 0 0 8px rgba(79,142,247,0.05); }
    50%      { box-shadow: 0 0 24px rgba(79,142,247,0.4), inset 0 0 16px rgba(79,142,247,0.1); }
}
@keyframes float {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-6px); }
}
@keyframes count-in {
    from { opacity:0; transform:scale(0.8); }
    to   { opacity:1; transform:scale(1); }
}

/* Main background */
.stApp { background-color: #0f1117; }

/* Reduce top padding */
.main .block-container { padding-top: 0.5rem !important; padding-bottom: 1rem !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1a2d40 100%);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── KPI Cards ───────────────────────────────────────────────────────────────── */
.kpi-card {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2d40 100%);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #4F8EF7;
    border-radius: 14px;
    padding: 20px 22px;
    margin: 4px 0;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: slide-up 0.5s ease-out both;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content:'';
    position:absolute;
    top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, rgba(79,142,247,0.4), transparent);
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(79,142,247,0.2), 0 0 0 1px rgba(79,142,247,0.3);
    border-left-width: 4px;
}
.kpi-label {
    font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: #64748b !important; margin-bottom: 10px;
}
.kpi-value {
    font-size: 30px; font-weight: 800; color: #f1f5f9 !important;
    line-height: 1; animation: count-in 0.6s ease-out both; letter-spacing: -0.5px;
}
.kpi-delta-good    { font-size: 12px; color: #22c55e !important; margin-top: 8px; font-weight: 600; }
.kpi-delta-bad     { font-size: 12px; color: #ef4444 !important; margin-top: 8px; font-weight: 600; }
.kpi-delta-neutral { font-size: 12px; color: #94a3b8 !important; margin-top: 8px; font-weight: 500; }

/* ── Live Indicator ──────────────────────────────────────────────────────────── */
.live-dot {
    display: inline-block; width: 8px; height: 8px;
    background: #22c55e; border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
    vertical-align: middle; margin-right: 6px;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3);
    border-radius: 20px; padding: 3px 12px; font-size: 10px;
    font-weight: 700; letter-spacing: 1px; color: #22c55e; text-transform: uppercase;
}

/* ── Section Headers ─────────────────────────────────────────────────────────── */
.section-header {
    font-size: 16px; font-weight: 700; color: #f1f5f9;
    margin: 24px 0 12px 0; padding: 0 0 8px 12px;
    border-bottom: 1px solid #1e3a5f;
    border-left: 3px solid #4F8EF7;
    position: relative;
}

/* ── Page Title ──────────────────────────────────────────────────────────────── */
.page-title {
    font-size: 36px; font-weight: 800; letter-spacing: -1px;
    background: linear-gradient(270deg, #4F8EF7, #7bb3ff, #a5f3fc, #4F8EF7);
    background-size: 300% 300%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: gradient-x 5s ease infinite;
    margin-bottom: 6px;
}
.page-subtitle { font-size: 13px; color: #64748b; margin-bottom: 20px; }

/* ── Badges ──────────────────────────────────────────────────────────────────── */
.badge { display:inline-block; border-radius:20px; padding:2px 10px; font-size:11px; font-weight:700; letter-spacing:0.5px; }
.badge-green  { background:rgba(34,197,94,0.12);  color:#22c55e;  border:1px solid rgba(34,197,94,0.3);  }
.badge-red    { background:rgba(239,68,68,0.12);  color:#ef4444;  border:1px solid rgba(239,68,68,0.3);  animation: danger-flash 2.5s ease-in-out infinite; }
.badge-yellow { background:rgba(245,158,11,0.12); color:#f59e0b;  border:1px solid rgba(245,158,11,0.3); }
.badge-blue   { background:rgba(79,142,247,0.12); color:#4F8EF7;  border:1px solid rgba(79,142,247,0.3); }
.badge-purple { background:rgba(167,139,250,0.12);color:#a78bfa;  border:1px solid rgba(167,139,250,0.3);}

/* ── Hero Stats Strip ────────────────────────────────────────────────────────── */
.hero-strip {
    background: linear-gradient(90deg, #051525, #0d1b2a, #051525);
    border: 1px solid #1e3a5f; border-radius: 14px;
    padding: 16px 24px; margin-bottom: 20px;
    display: flex; align-items: center; gap: 0; overflow-x: auto;
    animation: border-glow 4s ease-in-out infinite;
}
.hero-stat { text-align:center; padding: 0 24px; flex: 1; min-width: 100px; }
.hero-stat + .hero-stat { border-left: 1px solid #1e3a5f; }
.hero-stat-label { font-size:9px; font-weight:700; letter-spacing:1.5px; color:#64748b; text-transform:uppercase; }
.hero-stat-value { font-size:22px; font-weight:800; color:#f1f5f9; margin-top:3px; letter-spacing:-0.5px; }
.hero-stat-delta { font-size:11px; font-weight:600; margin-top:2px; }

/* ── Progress Bar ────────────────────────────────────────────────────────────── */
.prog-bg   { background:#1e3a5f; border-radius:8px; height:5px; margin-top:8px; overflow:hidden; }
.prog-fill { height:100%; border-radius:8px; transition: width 1.5s cubic-bezier(0.4,0,0.2,1); }

/* ── Alert boxes ─────────────────────────────────────────────────────────────── */
.alert-critical {
    background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25);
    border-left: 4px solid #ef4444; border-radius: 10px; padding: 12px 16px; margin: 4px 0;
    animation: danger-flash 3s ease-in-out infinite;
}
.alert-warning {
    background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.25);
    border-left: 4px solid #f59e0b; border-radius: 10px; padding: 12px 16px; margin: 4px 0;
}

/* ── Floating AI icon ────────────────────────────────────────────────────────── */
.float-icon { animation: float 3s ease-in-out infinite; display:inline-block; font-size:52px; }

/* ── Button override ─────────────────────────────────────────────────────────── */
[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #4F8EF7, #3b82f6) !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(79,142,247,0.3) !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(79,142,247,0.5) !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1b2a;
    border-radius: 8px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #1e3a5f;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 6px;
    color: #64748b !important;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #4F8EF7 !important;
}

/* Alert boxes */
.alert-critical {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 4px 0;
}
.alert-warning {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 4px 0;
}

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1e3a5f; border-radius: 8px; }

/* ── Dropdowns & Selects ─────────────────────────────────────────────────────── */
/* Selectbox and multiselect control box */
[data-baseweb="select"] > div:first-child,
[data-baseweb="select"] > div {
    background-color: #1a2d40 !important;
    border: 1px solid #4F8EF7 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
}
/* Hover state */
[data-baseweb="select"] > div:first-child:hover {
    border-color: #7bb3ff !important;
    background-color: #1e3a5f !important;
}
/* The selected text inside dropdown */
[data-baseweb="select"] span,
[data-baseweb="select"] div[class*="placeholder"] {
    color: #f1f5f9 !important;
}
/* Dropdown arrow icon */
[data-baseweb="select"] svg { fill: #4F8EF7 !important; }

/* Dropdown menu (open list) */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] {
    background-color: #0d1b2a !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
}
/* Dropdown list items */
[data-baseweb="menu"] li,
[role="option"] {
    background-color: #0d1b2a !important;
    color: #e2e8f0 !important;
}
[data-baseweb="menu"] li:hover,
[role="option"]:hover,
[aria-selected="true"] {
    background-color: #1e3a5f !important;
    color: #4F8EF7 !important;
}

/* Multiselect tags */
[data-baseweb="tag"] {
    background-color: #1e3a5f !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span { color: #4F8EF7 !important; }

/* Text input fields */
[data-baseweb="input"] > div,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #1a2d40 !important;
    border: 1px solid #4F8EF7 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
}

/* Filter label */
.filter-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 4px;
}

/* Sidebar brand */
.brand-title {
    font-size: 22px;
    font-weight: 700;
    color: #4F8EF7 !important;
}
.brand-subtitle { font-size: 11px; color: #64748b !important; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ───────────────────────────────────────────────────────────────
PLOTLY_THEME = "plotly_dark"
PRIMARY   = "#4F8EF7"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
DANGER    = "#ef4444"
MUTED     = "#64748b"
BG        = "#0d1b2a"
CARD_BG   = "#111827"
COLORS    = [PRIMARY, "#7bb3ff", "#22c55e", "#f59e0b", "#a78bfa", "#f472b6", "#34d399"]

def chart_layout(fig, height=300, margin=None):
    m = margin or dict(t=20, b=20, l=10, r=10)
    fig.update_layout(
        template=PLOTLY_THEME,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=m,
        font=dict(family="Inter", size=12, color="#94a3b8"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    )
    return fig

# ── DB Helper ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def query_filtered(sql: str, plans=None, regions=None, industries=None) -> pd.DataFrame:
    filters = []
    if plans and "All" not in plans:
        ps = ", ".join([f"'{p}'" for p in plans])
        filters.append(f"c.plan_type IN ({ps})")
    if regions and "All" not in regions:
        rs = ", ".join([f"'{r}'" for r in regions])
        filters.append(f"c.region IN ({rs})")
    if industries and "All" not in industries:
        ins = ", ".join([f"'{i}'" for i in industries])
        filters.append(f"c.industry IN ({ins})")
    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    final_sql = sql.replace("{{WHERE}}", where).replace("{{AND}}", ("AND " + " AND ".join(filters)) if filters else "")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(final_sql, conn)
    conn.close()
    return df

# ── Top Navigation Bar (always visible, no sidebar dependency) ─────────────────
st.markdown("""
<div style="background:linear-gradient(90deg,#0d1b2a,#1a2d40);border-bottom:1px solid #1e3a5f;
     padding:10px 20px;margin:-0.5rem -1rem 1rem -1rem;display:flex;align-items:center;gap:16px">
    <div style="font-size:20px;font-weight:700;color:#4F8EF7;white-space:nowrap">BridgeIQ</div>
    <div style="font-size:10px;color:#64748b;letter-spacing:1px;white-space:nowrap">AI-POWERED BUSINESS INTELLIGENCE</div>
</div>
""", unsafe_allow_html=True)

PAGES = [
    "📊 Executive Dashboard",
    "🧠 AI Insights Engine",
    "🤖 AI Feedback Analyzer",
    "📋 AI Requirements Generator",
    "🎯 Interview Simulator",
    "🔍 Customer 360",
    "📐 BA Artifacts",
    "💡 What-If Simulator",
    "👤 About the Analyst",
]

nav_col, info_col = st.columns([3, 1])
with nav_col:
    page = st.selectbox("Navigate", PAGES, label_visibility="collapsed")
with info_col:
    st.markdown('<div style="text-align:right;font-size:11px;color:#64748b;padding-top:8px">Apex Solutions · B2B SaaS Demo · Built by <b>Sai Hemanth</b></div>', unsafe_allow_html=True)

st.markdown("---")

# Active page breadcrumb
_pname = " ".join(page.split(" ")[1:])
_picon = page.split(" ")[0]
st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;margin-top:-8px">
    <span style="font-size:11px;color:#374151">BridgeIQ</span>
    <span style="color:#374151;font-size:11px">›</span>
    <span style="background:rgba(79,142,247,0.12);border:1px solid rgba(79,142,247,0.25);border-radius:6px;padding:2px 10px;font-size:11px;color:#4F8EF7;font-weight:600">{_picon} {_pname}</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar (filters only, for Executive Dashboard) ───────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-title">BridgeIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">DASHBOARD FILTERS</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    all_plans      = ["All", "Starter", "Growth", "Enterprise"]
    all_regions    = ["All", "North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
    all_industries = ["All", "Healthcare", "Finance", "Retail", "Manufacturing", "Education",
                      "Logistics", "Real Estate", "Legal", "Technology", "Consulting"]

    st.markdown('<div class="filter-label">Global Filters (Dashboard only)</div>', unsafe_allow_html=True)
    sel_plans  = st.multiselect("Plan Type", all_plans, default=["All"], key="plan")
    sel_region = st.multiselect("Region",    all_regions, default=["All"], key="region")
    sel_ind    = st.multiselect("Industry",  all_industries, default=["All"], key="ind")
    st.markdown("---")
    st.caption("Built by **Sai Hemanth**")
    st.caption("Technical BA Portfolio · 2026")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Executive Dashboard":

    st.markdown('<div class="page-title">Executive Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Apex Solutions · B2B SaaS · Real-time business intelligence · All metrics update with filters</div>', unsafe_allow_html=True)

    # Build filter clause
    f_plans = sel_plans if "All" not in sel_plans else []
    f_regions = sel_region if "All" not in sel_region else []
    f_inds = sel_ind if "All" not in sel_ind else []

    def where_clause(prefix="c"):
        parts = []
        if f_plans:
            ps = ", ".join([f"'{p}'" for p in f_plans])
            parts.append(f"{prefix}.plan_type IN ({ps})")
        if f_regions:
            rs = ", ".join([f"'{r}'" for r in f_regions])
            parts.append(f"{prefix}.region IN ({rs})")
        if f_inds:
            ins = ", ".join([f"'{i}'" for i in f_inds])
            parts.append(f"{prefix}.industry IN ({ins})")
        return ("WHERE " + " AND ".join(parts)) if parts else ""

    def and_clause(prefix="c"):
        wc = where_clause(prefix)
        return wc.replace("WHERE ", "AND ") if wc else ""

    @st.cache_data(ttl=60)
    def get_kpis(fp, fr, fi):
        wc = where_clause()
        return query(f"""
            SELECT
                COUNT(CASE WHEN status='Active' THEN 1 END) AS active_customers,
                COUNT(CASE WHEN status='Churned' THEN 1 END) AS churned_customers,
                ROUND(SUM(CASE WHEN status='Active' THEN mrr ELSE 0 END),0) AS total_mrr,
                ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
                ROUND(AVG(CASE WHEN status='Active' THEN health_score END),1) AS avg_health,
                ROUND(AVG(CASE WHEN status='Active' THEN nps_score END),1) AS avg_nps
            FROM customers c {wc}
        """)

    kpi = get_kpis(tuple(f_plans), tuple(f_regions), tuple(f_inds)).iloc[0]

    open_tickets = query("SELECT COUNT(*) AS cnt FROM support_tickets WHERE status IN ('Open','In Progress')").iloc[0]["cnt"]
    onb_pct      = query("SELECT ROUND(COUNT(CASE WHEN completed=1 THEN 1 END)*100.0/COUNT(*),1) AS pct FROM onboarding").iloc[0]["pct"]
    at_risk_n    = query("""SELECT COUNT(*) AS n FROM (
        WITH t AS (SELECT customer_id,COUNT(*) tc FROM support_tickets GROUP BY customer_id),
             u AS (SELECT customer_id,COUNT(*) uc FROM product_usage GROUP BY customer_id),
             o AS (SELECT customer_id,completed FROM onboarding)
        SELECT c.customer_id,
            (CASE WHEN c.health_score<60 THEN 30 WHEN c.health_score<75 THEN 15 ELSE 0 END)+
            (CASE WHEN COALESCE(t.tc,0)>15 THEN 20 WHEN COALESCE(t.tc,0)>8 THEN 10 ELSE 0 END)+
            (CASE WHEN COALESCE(u.uc,0)<3 THEN 25 WHEN COALESCE(u.uc,0)<8 THEN 12 ELSE 0 END)+
            (CASE WHEN COALESCE(o.completed,0)=0 THEN 15 ELSE 0 END)+
            (CASE WHEN c.nps_score<5 THEN 10 ELSE 0 END) AS rs
        FROM customers c LEFT JOIN t ON c.customer_id=t.customer_id
        LEFT JOIN u ON c.customer_id=u.customer_id LEFT JOIN o ON c.customer_id=o.customer_id
        WHERE c.status='Active') WHERE rs>=50""").iloc[0]["n"]

    arr = int(kpi["total_mrr"]) * 12
    mrr_at_risk = round(int(kpi["total_mrr"]) * float(kpi["churn_rate"]) / 100)

    # ── Live Hero Strip ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-strip">
        <div style="display:flex;align-items:center;gap:8px;padding-right:24px;border-right:1px solid #1e3a5f;white-space:nowrap">
            <span class="live-dot"></span>
            <span style="font-size:10px;font-weight:800;color:#22c55e;letter-spacing:2px">LIVE DATA</span>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-label">Total ARR</div>
            <div class="hero-stat-value">${arr:,}</div>
            <div class="hero-stat-delta" style="color:#22c55e">▲ Active Revenue</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-label">MRR at Risk</div>
            <div class="hero-stat-value" style="color:#ef4444">${mrr_at_risk:,}</div>
            <div class="hero-stat-delta" style="color:#ef4444">⚠ Churn exposure</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-label">At-Risk Accounts</div>
            <div class="hero-stat-value" style="color:#f59e0b">{int(at_risk_n)}</div>
            <div class="hero-stat-delta" style="color:#f59e0b">Risk score ≥ 50</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-label">Open Tickets</div>
            <div class="hero-stat-value" style="color:#4F8EF7">{int(open_tickets):,}</div>
            <div class="hero-stat-delta" style="color:#64748b">Needs resolution</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-label">Avg Health Score</div>
            <div class="hero-stat-value" style="color:#22c55e">{kpi['avg_health']}</div>
            <div class="hero-stat-delta" style="color:#64748b">out of 100</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-label">Churn Rate</div>
            <div class="hero-stat-value" style="color:#ef4444">{kpi['churn_rate']}%</div>
            <div class="hero-stat-delta" style="color:#ef4444">▼ 2.1% target needed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row ───────────────────────────────────────────────────────────────
    cols = st.columns(6)
    health_pct = float(kpi['avg_health'])
    onb_bar    = float(onb_pct)
    kpi_data = [
        ("ACTIVE CUSTOMERS", f"{int(kpi['active_customers']):,}", "▲ Growing portfolio", "good",   int(kpi['active_customers'])/500*100, "#22c55e"),
        ("TOTAL MRR",        f"${int(kpi['total_mrr']):,}",       "Monthly Recurring Rev",   "neutral", 72, "#4F8EF7"),
        ("TOTAL ARR",        f"${arr:,}",                          "Annualized Run Rate",      "neutral", 72, "#4F8EF7"),
        ("CHURN RATE",       f"{kpi['churn_rate']}%",              "▲ 17% above SaaS avg",    "bad",     min(float(kpi['churn_rate'])*4, 100), "#ef4444"),
        ("AVG HEALTH",       f"{health_pct}/100",                  f"NPS avg: {kpi['avg_nps']}/10","good", health_pct, "#22c55e"),
        ("ONBOARDING",       f"{onb_pct}%",                        f"{open_tickets:,} open tickets","neutral", onb_bar, "#f59e0b"),
    ]
    for col, (label, value, delta, dtype, bar_pct, bar_color) in zip(cols, kpi_data):
        delta_class = f"kpi-delta-{dtype}"
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="prog-bg"><div class="prog-fill" style="width:{min(bar_pct,100):.0f}%;background:{bar_color}"></div></div>
            <div class="{delta_class}">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📈 Overview", "💰 Revenue", "👥 Customer Health", "🎫 Support", "🚀 Onboarding", "📊 Cohort Retention", "🏆 SaaS Benchmarks", "🔍 Anomaly Detector"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — OVERVIEW
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:
            st.markdown('<div class="section-header">Monthly Net Revenue</div>', unsafe_allow_html=True)
            rev = query(f"""
                SELECT strftime('%Y-%m', t.transaction_date) AS month,
                       ROUND(SUM(t.amount),0) AS net_revenue,
                       ROUND(SUM(CASE WHEN t.amount>0 THEN t.amount ELSE 0 END),0) AS gross_revenue
                FROM transactions t JOIN customers c ON t.customer_id=c.customer_id
                WHERE t.status='Completed' {and_clause()}
                GROUP BY month ORDER BY month
            """)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=rev["month"], y=rev["gross_revenue"],
                fill="tozeroy", name="Gross Revenue",
                line=dict(color=PRIMARY, width=2),
                fillcolor="rgba(79,142,247,0.1)",
                hovertemplate="<b>%{x}</b><br>Gross: $%{y:,.0f}<extra></extra>"
            ))
            fig.add_trace(go.Scatter(
                x=rev["month"], y=rev["net_revenue"],
                name="Net Revenue",
                line=dict(color=SUCCESS, width=2, dash="dot"),
                hovertemplate="<b>%{x}</b><br>Net: $%{y:,.0f}<extra></extra>"
            ))
            chart_layout(fig, height=280)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-header">Health Score</div>', unsafe_allow_html=True)
            health_val = float(kpi["avg_health"])
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=health_val,
                delta={"reference": 70, "increasing": {"color": SUCCESS}},
                number={"font": {"size": 36, "color": "#f1f5f9"}, "suffix": "/100"},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": MUTED},
                    "bar": {"color": PRIMARY, "thickness": 0.25},
                    "bgcolor": BG,
                    "bordercolor": "#1e3a5f",
                    "steps": [
                        {"range": [0, 50],   "color": "rgba(239,68,68,0.15)"},
                        {"range": [50, 75],  "color": "rgba(245,158,11,0.15)"},
                        {"range": [75, 100], "color": "rgba(34,197,94,0.15)"},
                    ],
                    "threshold": {"line": {"color": SUCCESS, "width": 3}, "thickness": 0.8, "value": 80},
                },
            ))
            chart_layout(fig_gauge, height=220)
            fig_gauge.update_layout(margin=dict(t=10, b=0, l=20, r=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with c3:
            st.markdown('<div class="section-header">Customer Mix</div>', unsafe_allow_html=True)
            mix = query(f"""
                SELECT plan_type, COUNT(*) AS count, ROUND(SUM(mrr),0) AS mrr
                FROM customers c {where_clause()}
                GROUP BY plan_type
            """)
            fig_donut = go.Figure(go.Pie(
                labels=mix["plan_type"], values=mix["count"],
                hole=0.6,
                marker_colors=[PRIMARY, "#7bb3ff", "#22c55e"],
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Customers: %{value}<br>Share: %{percent}<extra></extra>"
            ))
            fig_donut.add_annotation(text=f"<b>{int(mix['count'].sum())}</b><br>Total", x=0.5, y=0.5,
                                      font_size=14, font_color="#f1f5f9", showarrow=False)
            chart_layout(fig_donut, height=220)
            fig_donut.update_layout(showlegend=False, margin=dict(t=10, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)

        # At-Risk Table
        st.markdown('<div class="section-header">At-Risk Active Customers</div>', unsafe_allow_html=True)
        st.caption("Composite risk score: health score (30pts) + ticket volume (20pts) + low usage (25pts) + incomplete onboarding (15pts) + low NPS (10pts)")

        at_risk = query(f"""
            WITH t AS (
                SELECT customer_id, COUNT(*) AS tickets,
                       COUNT(CASE WHEN priority IN ('High','Critical') THEN 1 END) AS hi_tix
                FROM support_tickets GROUP BY customer_id
            ),
            u AS (SELECT customer_id, COUNT(*) AS sessions FROM product_usage GROUP BY customer_id),
            o AS (SELECT customer_id, completed FROM onboarding)
            SELECT c.company_name AS Company, c.plan_type AS Plan,
                   '$'||CAST(CAST(c.mrr AS INT) AS TEXT) AS MRR,
                   ROUND(c.health_score,0) AS Health,
                   COALESCE(t.tickets,0) AS Tickets,
                   COALESCE(u.sessions,0) AS Sessions,
                   CASE WHEN o.completed=1 THEN 'Yes' ELSE 'No' END AS Onboarded,
                   ROUND(
                       (CASE WHEN c.health_score<60 THEN 30 WHEN c.health_score<75 THEN 15 ELSE 0 END)
                       +(CASE WHEN COALESCE(t.tickets,0)>15 THEN 20 WHEN COALESCE(t.tickets,0)>8 THEN 10 ELSE 0 END)
                       +(CASE WHEN COALESCE(u.sessions,0)<3 THEN 25 WHEN COALESCE(u.sessions,0)<8 THEN 12 ELSE 0 END)
                       +(CASE WHEN COALESCE(o.completed,0)=0 THEN 15 ELSE 0 END)
                       +(CASE WHEN c.nps_score<5 THEN 10 ELSE 0 END)
                   ,0) AS Risk
            FROM customers c
            LEFT JOIN t ON c.customer_id=t.customer_id
            LEFT JOIN u ON c.customer_id=u.customer_id
            LEFT JOIN o ON c.customer_id=o.customer_id
            WHERE c.status='Active' {and_clause()}
            ORDER BY Risk DESC LIMIT 15
        """)

        def style_risk(v):
            if isinstance(v, (int, float)):
                if v >= 50: return "background-color:#3d0f0f;color:#ef4444;font-weight:700"
                if v >= 30: return "background-color:#3d2a0a;color:#f59e0b;font-weight:600"
                return "background-color:#0a2e1a;color:#22c55e"
            return ""

        styled = at_risk.style.map(style_risk, subset=["Risk"]) \
                              .map(lambda v: "color:#ef4444;font-weight:600" if v == "No" else "color:#22c55e", subset=["Onboarded"])

        col_tbl, col_exp = st.columns([5, 1])
        with col_tbl:
            st.dataframe(styled, use_container_width=True, hide_index=True, height=420)
        with col_exp:
            st.download_button(
                label="Export CSV",
                data=at_risk.to_csv(index=False),
                file_name="at_risk_customers.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — REVENUE
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="section-header">Revenue by Plan (Monthly)</div>', unsafe_allow_html=True)
            rev_plan = query(f"""
                SELECT strftime('%Y-%m', t.transaction_date) AS month, c.plan_type,
                       ROUND(SUM(t.amount),0) AS revenue
                FROM transactions t JOIN customers c ON t.customer_id=c.customer_id
                WHERE t.status='Completed' {and_clause()}
                GROUP BY month, c.plan_type ORDER BY month
            """)
            fig = px.area(rev_plan, x="month", y="revenue", color="plan_type",
                          color_discrete_sequence=COLORS,
                          labels={"month": "", "revenue": "Revenue ($)", "plan_type": "Plan"})
            chart_layout(fig, 300)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-header">Revenue by Transaction Type</div>', unsafe_allow_html=True)
            tx_type = query(f"""
                SELECT t.transaction_type, ROUND(SUM(t.amount),0) AS total,
                       COUNT(*) AS count
                FROM transactions t JOIN customers c ON t.customer_id=c.customer_id
                WHERE t.status='Completed' {and_clause()}
                GROUP BY t.transaction_type ORDER BY total DESC
            """)
            fig2 = px.bar(tx_type, x="transaction_type", y="total",
                          color="total", color_continuous_scale=["#1e3a5f", PRIMARY],
                          text="count",
                          labels={"transaction_type": "", "total": "Total Revenue ($)", "count": "Count"})
            fig2.update_traces(texttemplate="%{text} txns", textposition="outside")
            chart_layout(fig2, 300)
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="section-header">Top 10 Customers by Lifetime Value</div>', unsafe_allow_html=True)
            top_cust = query(f"""
                SELECT c.company_name, c.plan_type, ROUND(SUM(t.amount),0) AS ltv,
                       COUNT(t.transaction_id) AS txns, c.status
                FROM customers c JOIN transactions t ON c.customer_id=t.customer_id
                WHERE t.status='Completed' {and_clause()}
                GROUP BY c.customer_id ORDER BY ltv DESC LIMIT 10
            """)
            fig3 = px.bar(top_cust, x="ltv", y="company_name", orientation="h",
                          color="plan_type", color_discrete_sequence=COLORS,
                          text="ltv",
                          labels={"ltv": "Lifetime Value ($)", "company_name": "", "plan_type": "Plan"})
            fig3.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig3.update_layout(yaxis=dict(autorange="reversed"))
            chart_layout(fig3, 340)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.markdown('<div class="section-header">MRR Distribution by Region</div>', unsafe_allow_html=True)
            reg_mrr = query(f"""
                SELECT region, ROUND(SUM(mrr),0) AS total_mrr, COUNT(*) AS customers
                FROM customers c WHERE status='Active' {and_clause()}
                GROUP BY region ORDER BY total_mrr DESC
            """)
            fig4 = px.treemap(reg_mrr, path=["region"], values="total_mrr",
                              color="customers", color_continuous_scale=["#1e3a5f", PRIMARY],
                              hover_data={"customers": True, "total_mrr": ":,.0f"})
            fig4.update_traces(texttemplate="<b>%{label}</b><br>$%{value:,.0f}")
            chart_layout(fig4, 340)
            st.plotly_chart(fig4, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — CUSTOMER HEALTH
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="section-header">Churn Rate by Industry</div>', unsafe_allow_html=True)
            ind_churn = query(f"""
                SELECT industry,
                       COUNT(*) AS total,
                       COUNT(CASE WHEN status='Churned' THEN 1 END) AS churned,
                       ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
                       ROUND(SUM(CASE WHEN status='Churned' THEN mrr ELSE 0 END),0) AS mrr_lost
                FROM customers c {where_clause()}
                GROUP BY industry ORDER BY churn_rate DESC
            """)
            fig = px.bar(ind_churn, x="churn_rate", y="industry", orientation="h",
                         color="churn_rate",
                         color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
                         text="churn_rate",
                         labels={"churn_rate": "Churn Rate (%)", "industry": ""},
                         hover_data={"mrr_lost": ":,.0f", "churned": True, "total": True})
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            chart_layout(fig, 360)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-header">Health Score: Active vs Churned</div>', unsafe_allow_html=True)
            health_df = query(f"SELECT status, health_score FROM customers c {where_clause()}")
            fig2 = go.Figure()
            for status, color in [("Active", PRIMARY), ("Churned", DANGER)]:
                d = health_df[health_df["status"] == status]["health_score"]
                fig2.add_trace(go.Violin(
                    x=[status] * len(d), y=d,
                    name=status, fillcolor=color,
                    line_color=color, opacity=0.7,
                    box_visible=True, meanline_visible=True,
                    hoverinfo="y+name"
                ))
            chart_layout(fig2, 360)
            fig2.update_layout(showlegend=False, violingap=0.3)
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="section-header">Churn by Plan & Region</div>', unsafe_allow_html=True)
            heatmap_df = query(f"""
                SELECT plan_type, region,
                       ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate
                FROM customers c {where_clause()}
                GROUP BY plan_type, region
            """)
            pivot = heatmap_df.pivot(index="plan_type", columns="region", values="churn_rate").fillna(0)
            fig3 = go.Figure(go.Heatmap(
                z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                colorscale=[[0, "#0a2e1a"], [0.5, "#3d2a0a"], [1, "#3d0f0f"]],
                text=pivot.values.round(1), texttemplate="%{text}%",
                hovertemplate="Plan: %{y}<br>Region: %{x}<br>Churn: %{z}%<extra></extra>",
                showscale=False
            ))
            chart_layout(fig3, 280)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.markdown('<div class="section-header">Usage vs Health Score</div>', unsafe_allow_html=True)
            scatter_df = query(f"""
                SELECT c.health_score, c.mrr, c.status, c.plan_type,
                       COALESCE(u.sessions,0) AS sessions
                FROM customers c
                LEFT JOIN (SELECT customer_id, COUNT(*) AS sessions FROM product_usage GROUP BY customer_id) u
                    ON c.customer_id=u.customer_id
                WHERE 1=1 {and_clause()}
            """)
            fig4 = px.scatter(scatter_df, x="sessions", y="health_score",
                              color="status", size="mrr",
                              symbol="plan_type",
                              color_discrete_map={"Active": PRIMARY, "Churned": DANGER},
                              labels={"sessions": "Usage Sessions", "health_score": "Health Score",
                                      "status": "Status", "plan_type": "Plan"},
                              opacity=0.7,
                              trendline="ols",
                              hover_data={"mrr": ":,.0f", "plan_type": True})
            chart_layout(fig4, 280)
            st.plotly_chart(fig4, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — SUPPORT
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        c1, c2 = st.columns([3, 2])

        with c1:
            st.markdown('<div class="section-header">Monthly Ticket Volume & CSAT Trend</div>', unsafe_allow_html=True)
            tix_trend = query("""
                SELECT strftime('%Y-%m', created_date) AS month,
                       COUNT(*) AS tickets,
                       COUNT(CASE WHEN priority IN ('High','Critical') THEN 1 END) AS high_priority,
                       ROUND(AVG(satisfaction_score),2) AS avg_csat
                FROM support_tickets GROUP BY month ORDER BY month
            """)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=tix_trend["month"], y=tix_trend["tickets"],
                                  name="Total Tickets", marker_color=PRIMARY, opacity=0.7), secondary_y=False)
            fig.add_trace(go.Bar(x=tix_trend["month"], y=tix_trend["high_priority"],
                                  name="High Priority", marker_color=DANGER, opacity=0.9), secondary_y=False)
            fig.add_trace(go.Scatter(x=tix_trend["month"], y=tix_trend["avg_csat"],
                                      name="CSAT", line=dict(color=SUCCESS, width=2),
                                      mode="lines+markers"), secondary_y=True)
            chart_layout(fig, 300)
            fig.update_layout(barmode="overlay")
            fig.update_yaxes(title_text="Ticket Count", secondary_y=False, gridcolor="#1e3a5f")
            fig.update_yaxes(title_text="CSAT Score", secondary_y=True, gridcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown('<div class="section-header">SLA Breach Rate by Priority</div>', unsafe_allow_html=True)
            sla = query("""
                SELECT priority,
                       COUNT(*) AS total,
                       COUNT(CASE
                           WHEN priority='Critical' AND resolution_time_hours>8  THEN 1
                           WHEN priority='High'     AND resolution_time_hours>24 THEN 1
                           WHEN priority='Medium'   AND resolution_time_hours>48 THEN 1
                           WHEN priority='Low'      AND resolution_time_hours>96 THEN 1
                       END) AS breaches,
                       ROUND(COUNT(CASE
                           WHEN priority='Critical' AND resolution_time_hours>8  THEN 1
                           WHEN priority='High'     AND resolution_time_hours>24 THEN 1
                           WHEN priority='Medium'   AND resolution_time_hours>48 THEN 1
                           WHEN priority='Low'      AND resolution_time_hours>96 THEN 1
                       END)*100.0/COUNT(*),1) AS breach_pct
                FROM support_tickets GROUP BY priority
                ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END
            """)
            fig2 = go.Figure()
            colors_sla = [DANGER, WARNING, PRIMARY, SUCCESS]
            for i, row in sla.iterrows():
                fig2.add_trace(go.Bar(
                    x=[row["breach_pct"]], y=[row["priority"]],
                    orientation="h", name=row["priority"],
                    marker_color=colors_sla[i % 4],
                    text=f"{row['breach_pct']}%",
                    textposition="outside",
                    hovertemplate=f"<b>{row['priority']}</b><br>Breaches: {row['breaches']}/{row['total']}<extra></extra>"
                ))
            fig2.update_layout(xaxis_range=[0, 70], showlegend=False, barmode="group")
            chart_layout(fig2, 300)
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="section-header">Ticket Category Breakdown</div>', unsafe_allow_html=True)
            cat = query("""
                SELECT category, COUNT(*) AS count,
                       ROUND(AVG(resolution_time_hours),1) AS avg_hrs,
                       ROUND(AVG(satisfaction_score),2) AS avg_csat
                FROM support_tickets GROUP BY category ORDER BY count DESC
            """)
            fig3 = px.bar(cat, x="category", y="count",
                          color="avg_hrs",
                          color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
                          text="avg_hrs",
                          labels={"category": "", "count": "Tickets", "avg_hrs": "Avg Hrs"},
                          hover_data={"avg_csat": True})
            fig3.update_traces(texttemplate="%{text}h avg", textposition="outside")
            fig3.update_layout(coloraxis_showscale=False)
            chart_layout(fig3, 300)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.markdown('<div class="section-header">Resolution Time Distribution</div>', unsafe_allow_html=True)
            res_df = query("SELECT priority, resolution_time_hours FROM support_tickets WHERE resolution_time_hours < 200")
            fig4 = px.box(res_df, x="priority", y="resolution_time_hours",
                          color="priority",
                          color_discrete_map={"Critical": DANGER, "High": WARNING,
                                               "Medium": PRIMARY, "Low": SUCCESS},
                          labels={"priority": "Priority", "resolution_time_hours": "Resolution Time (hrs)"},
                          category_orders={"priority": ["Critical", "High", "Medium", "Low"]})
            chart_layout(fig4, 300)
            fig4.update_layout(showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — ONBOARDING
    # ════════════════════════════════════════════════════════════════════════
    with tab5:
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown('<div class="section-header">Completion Rate</div>', unsafe_allow_html=True)
            onb = query("SELECT completed, COUNT(*) AS count FROM onboarding GROUP BY completed")
            done = int(onb[onb["completed"]==1]["count"].sum()) if 1 in onb["completed"].values else 0
            total_onb = int(onb["count"].sum())
            pct = round(done*100/total_onb, 1)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct,
                number={"suffix": "%", "font": {"size": 40, "color": "#f1f5f9"}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": SUCCESS if pct >= 85 else WARNING, "thickness": 0.3},
                    "bgcolor": BG,
                    "steps": [
                        {"range": [0, 70],   "color": "rgba(239,68,68,0.1)"},
                        {"range": [70, 85],  "color": "rgba(245,158,11,0.1)"},
                        {"range": [85, 100], "color": "rgba(34,197,94,0.1)"},
                    ],
                },
            ))
            chart_layout(fig, 240)
            fig.update_layout(margin=dict(t=10, b=0, l=30, r=30))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f'<div style="text-align:center;color:#64748b;font-size:12px">{done} of {total_onb} customers completed</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="section-header">Blockers (Incomplete)</div>', unsafe_allow_html=True)
            blockers = query("""
                SELECT blocker, COUNT(*) AS count
                FROM onboarding WHERE completed=0 AND blocker!='None'
                GROUP BY blocker ORDER BY count DESC
            """)
            fig2 = px.pie(blockers, values="count", names="blocker",
                          hole=0.5, color_discrete_sequence=COLORS)
            fig2.update_traces(textposition="outside", textinfo="label+percent")
            chart_layout(fig2, 280)
            fig2.update_layout(showlegend=False, margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)

        with c3:
            st.markdown('<div class="section-header">Completion by Plan</div>', unsafe_allow_html=True)
            onb_plan = query(f"""
                SELECT c.plan_type,
                       COUNT(*) AS total,
                       COUNT(CASE WHEN o.completed=1 THEN 1 END) AS done,
                       ROUND(COUNT(CASE WHEN o.completed=1 THEN 1 END)*100.0/COUNT(*),1) AS pct,
                       ROUND(AVG(CASE WHEN o.completed=1 THEN o.days_to_complete END),1) AS avg_days
                FROM onboarding o JOIN customers c ON o.customer_id=c.customer_id
                WHERE 1=1 {and_clause()}
                GROUP BY c.plan_type
            """)
            fig3 = go.Figure()
            for i, row in onb_plan.iterrows():
                fig3.add_trace(go.Bar(
                    x=[row["plan_type"]], y=[row["pct"]],
                    name=row["plan_type"],
                    marker_color=COLORS[i],
                    text=f"{row['pct']}%<br>{row['avg_days']}d avg",
                    textposition="inside",
                    hovertemplate=f"<b>{row['plan_type']}</b><br>Completion: {row['pct']}%<br>Avg Days: {row['avg_days']}<extra></extra>"
                ))
            fig3.update_layout(showlegend=False)
            chart_layout(fig3, 280)
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown('<div class="section-header">Onboarding Impact on Churn</div>', unsafe_allow_html=True)
        impact = query("""
            SELECT o.completed,
                   COUNT(*) AS customers,
                   COUNT(CASE WHEN c.status='Churned' THEN 1 END) AS churned,
                   ROUND(COUNT(CASE WHEN c.status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
                   ROUND(AVG(c.health_score),1) AS avg_health,
                   ROUND(AVG(c.mrr),0) AS avg_mrr
            FROM onboarding o JOIN customers c ON o.customer_id=c.customer_id
            GROUP BY o.completed
        """)
        impact["Onboarding"] = impact["completed"].map({1: "Completed", 0: "Incomplete"})
        col_a, col_b = st.columns(2)
        with col_a:
            fig4 = px.bar(impact, x="Onboarding", y="churn_rate",
                          color="Onboarding",
                          color_discrete_map={"Completed": SUCCESS, "Incomplete": DANGER},
                          text="churn_rate",
                          labels={"churn_rate": "Churn Rate (%)"},
                          title="Churn Rate: Completed vs Incomplete Onboarding")
            fig4.update_traces(texttemplate="%{text}%", textposition="outside")
            fig4.update_layout(showlegend=False)
            chart_layout(fig4, 280)
            st.plotly_chart(fig4, use_container_width=True)
        with col_b:
            fig5 = px.bar(impact, x="Onboarding", y="avg_health",
                          color="Onboarding",
                          color_discrete_map={"Completed": SUCCESS, "Incomplete": DANGER},
                          text="avg_health",
                          labels={"avg_health": "Avg Health Score"},
                          title="Avg Health Score: Completed vs Incomplete")
            fig5.update_traces(texttemplate="%{text}", textposition="outside")
            fig5.update_layout(showlegend=False)
            chart_layout(fig5, 280)
            st.plotly_chart(fig5, use_container_width=True)


    # ════════════════════════════════════════════════════════════════════════
    # TAB 6 — COHORT RETENTION
    # ════════════════════════════════════════════════════════════════════════
    with tab6:
        st.markdown('<div class="section-header">Customer Cohort Retention by Signup Quarter</div>', unsafe_allow_html=True)
        st.caption("Tracks retention of each signup cohort over time — the gold standard metric for B2B SaaS health analysis.")

        cohort = query("""
            WITH cohorts AS (
                SELECT customer_id, mrr, status,
                    strftime('%Y-Q', contract_start) ||
                        CASE
                            WHEN CAST(strftime('%m', contract_start) AS INTEGER) BETWEEN 1 AND 3 THEN '1'
                            WHEN CAST(strftime('%m', contract_start) AS INTEGER) BETWEEN 4 AND 6 THEN '2'
                            WHEN CAST(strftime('%m', contract_start) AS INTEGER) BETWEEN 7 AND 9 THEN '3'
                            ELSE '4'
                        END AS cohort_quarter
                FROM customers
            )
            SELECT cohort_quarter,
                   COUNT(*) AS cohort_size,
                   COUNT(CASE WHEN status='Active' THEN 1 END) AS still_active,
                   COUNT(CASE WHEN status='Churned' THEN 1 END) AS churned,
                   ROUND(COUNT(CASE WHEN status='Active' THEN 1 END)*100.0/COUNT(*),1) AS retention_rate,
                   ROUND(SUM(CASE WHEN status='Active' THEN mrr ELSE 0 END),0) AS retained_mrr
            FROM cohorts GROUP BY cohort_quarter ORDER BY cohort_quarter
        """)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-header">Retention Rate by Cohort</div>', unsafe_allow_html=True)
            fig_c1 = px.bar(cohort, x="cohort_quarter", y="retention_rate",
                            color="retention_rate",
                            color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
                            text="retention_rate",
                            labels={"cohort_quarter": "Signup Cohort", "retention_rate": "Retention (%)"},
                            hover_data={"cohort_size": True, "still_active": True, "churned": True})
            fig_c1.update_traces(texttemplate="%{text}%", textposition="outside")
            fig_c1.update_layout(coloraxis_showscale=False)
            chart_layout(fig_c1, 320)
            st.plotly_chart(fig_c1, use_container_width=True)

        with c2:
            st.markdown('<div class="section-header">Retained MRR by Cohort</div>', unsafe_allow_html=True)
            fig_c2 = go.Figure()
            fig_c2.add_trace(go.Bar(
                x=cohort["cohort_quarter"], y=cohort["retained_mrr"],
                marker_color=PRIMARY, opacity=0.8,
                text=cohort["retained_mrr"].apply(lambda x: f"${x:,.0f}"),
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Retained MRR: $%{y:,.0f}<extra></extra>"
            ))
            fig_c2.add_trace(go.Scatter(
                x=cohort["cohort_quarter"],
                y=cohort["retained_mrr"].rolling(2, min_periods=1).mean(),
                name="Trend", line=dict(color=WARNING, width=2, dash="dot"), mode="lines"
            ))
            chart_layout(fig_c2, 320)
            st.plotly_chart(fig_c2, use_container_width=True)

        st.markdown('<div class="section-header">Average Customer Lifespan Before Churn (by Plan)</div>', unsafe_allow_html=True)
        lifespan = query("""
            SELECT plan_type,
                   ROUND(AVG(julianday(churn_date) - julianday(contract_start)), 0) AS avg_days,
                   ROUND(AVG(julianday(churn_date) - julianday(contract_start)) / 30.0, 1) AS avg_months,
                   COUNT(*) AS churned_count
            FROM customers WHERE status='Churned'
            GROUP BY plan_type ORDER BY avg_days DESC
        """)
        ls_cols = st.columns(len(lifespan))
        for col, (_, row) in zip(ls_cols, lifespan.iterrows()):
            lc = SUCCESS if row["avg_months"] > 12 else WARNING
            col.markdown(f"""
            <div class="kpi-card" style="border-left-color:{lc}">
                <div class="kpi-label">{row['plan_type']} Plan</div>
                <div class="kpi-value">{row['avg_months']}mo</div>
                <div class="kpi-delta-neutral">avg lifespan · {int(row['churned_count'])} lost</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Cohort Summary Table</div>', unsafe_allow_html=True)
        cohort_display = cohort.rename(columns={
            "cohort_quarter": "Cohort", "cohort_size": "Started",
            "still_active": "Active", "churned": "Churned",
            "retention_rate": "Retention %", "retained_mrr": "Retained MRR ($)"
        })

        def style_retention(v):
            if isinstance(v, (int, float)):
                if v >= 85: return "color:#22c55e;font-weight:700"
                if v >= 70: return "color:#f59e0b;font-weight:600"
                return "color:#ef4444;font-weight:600"
            return ""

        st.dataframe(cohort_display.style.map(style_retention, subset=["Retention %"]),
                     use_container_width=True, hide_index=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 7 — SAAS BENCHMARKS
    # ════════════════════════════════════════════════════════════════════════
    with tab7:
        st.markdown('<div class="section-header">Apex Solutions vs SaaS Industry Benchmarks</div>', unsafe_allow_html=True)
        st.caption("Benchmarks sourced from Baremetrics, Gainsight, Zendesk, Totango, and SaaStr annual reports (2024). Shows where Apex stands vs market expectations.")

        live_bm = query("""
            SELECT
                ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
                ROUND(AVG(CASE WHEN status='Active' THEN nps_score END)*10,1) AS nps_norm,
                ROUND(AVG(CASE WHEN status='Active' THEN health_score END),1) AS avg_health
            FROM customers
        """).iloc[0]

        supp_bm = query("""
            SELECT ROUND(AVG(resolution_time_hours),1) AS avg_res,
                   ROUND(AVG(satisfaction_score),2) AS avg_csat,
                   ROUND(COUNT(CASE WHEN priority='Critical' AND resolution_time_hours>8 THEN 1 END)*100.0/
                         COUNT(CASE WHEN priority='Critical' THEN 1 END),1) AS crit_breach
            FROM support_tickets
        """).iloc[0]

        onb_bm = query("""
            SELECT ROUND(COUNT(CASE WHEN completed=1 THEN 1 END)*100.0/COUNT(*),1) AS completion
            FROM onboarding
        """).iloc[0]

        benchmarks = [
            {"metric": "Annual Churn Rate", "apex": float(live_bm["churn_rate"]), "apex_str": f"{live_bm['churn_rate']}%",
             "good": 5.0, "good_str": "< 5%", "avg_str": "5–10%", "dir": "lower", "source": "Baremetrics 2024"},
            {"metric": "NPS Score", "apex": float(live_bm["nps_norm"]), "apex_str": f"{live_bm['nps_norm']}",
             "good": 40.0, "good_str": "> 40", "avg_str": "20–40", "dir": "higher", "source": "Satmetrix 2024"},
            {"metric": "Avg Resolution Time", "apex": float(supp_bm["avg_res"]), "apex_str": f"{supp_bm['avg_res']}h",
             "good": 8.0, "good_str": "< 8h", "avg_str": "8–24h", "dir": "lower", "source": "Zendesk 2024"},
            {"metric": "CSAT Score", "apex": float(supp_bm["avg_csat"]), "apex_str": f"{supp_bm['avg_csat']}/5",
             "good": 4.5, "good_str": "> 4.5/5", "avg_str": "3.5–4.5/5", "dir": "higher", "source": "Gainsight 2024"},
            {"metric": "Onboarding Completion", "apex": float(onb_bm["completion"]), "apex_str": f"{onb_bm['completion']}%",
             "good": 85.0, "good_str": "> 85%", "avg_str": "70–85%", "dir": "higher", "source": "Totango 2024"},
            {"metric": "Critical SLA Breach Rate", "apex": float(supp_bm["crit_breach"]), "apex_str": f"{supp_bm['crit_breach']}%",
             "good": 5.0, "good_str": "< 5%", "avg_str": "5–15%", "dir": "lower", "source": "PagerDuty 2024"},
        ]

        bm_cols = st.columns(3)
        for i, bm in enumerate(benchmarks):
            col = bm_cols[i % 3]
            v, g = bm["apex"], bm["good"]
            if bm["dir"] == "lower":
                ok = v <= g
                near = v <= g * 2
            else:
                ok = v >= g
                near = v >= g * 0.7
            color = SUCCESS if ok else (WARNING if near else DANGER)
            icon = "✓" if ok else ("△" if near else "✕")
            label = "MEETS BENCHMARK" if ok else ("NEAR BENCHMARK" if near else "BELOW BENCHMARK")
            col.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-left:4px solid {color};border-radius:12px;padding:16px;margin-bottom:12px">
                <div style="font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#64748b;margin-bottom:8px">{bm['metric']}</div>
                <div style="font-size:28px;font-weight:700;color:#f1f5f9;margin-bottom:4px">{bm['apex_str']}</div>
                <div style="font-size:12px;color:{color};font-weight:600;margin-bottom:4px">{icon} {label}</div>
                <div style="font-size:11px;color:#64748b">Good: {bm['good_str']} · Avg: {bm['avg_str']}</div>
                <div style="font-size:10px;color:#374151;margin-top:4px">Source: {bm['source']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Gap Analysis & Priority Actions</div>', unsafe_allow_html=True)
        gaps = [bm for bm in benchmarks if
                (bm["dir"] == "lower" and bm["apex"] > bm["good"]) or
                (bm["dir"] == "higher" and bm["apex"] < bm["good"])]

        if gaps:
            st.markdown(f'<div class="alert-critical"><b>⚠ {len(gaps)} metric(s) below benchmark</b> — these are the highest-priority process improvement areas</div>', unsafe_allow_html=True)
            for g in gaps:
                gap_val = abs(g["apex"] - g["good"])
                st.markdown(f'<div class="alert-warning" style="margin-top:6px"><b>{g["metric"]}</b>: Apex at <b>{g["apex_str"]}</b> vs target <b>{g["good_str"]}</b> — gap of {gap_val:.1f}. Immediate action required.</div>', unsafe_allow_html=True)
        else:
            st.success("All metrics meet or exceed industry benchmarks.")

        ok_metrics = [bm for bm in benchmarks if
                      (bm["dir"] == "lower" and bm["apex"] <= bm["good"]) or
                      (bm["dir"] == "higher" and bm["apex"] >= bm["good"])]
        if ok_metrics:
            st.markdown(f'<div style="background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.2);border-radius:8px;padding:12px;margin-top:8px"><b style="color:#22c55e">✓ {len(ok_metrics)} metric(s) meet or exceed benchmark:</b> <span style="color:#64748b">{", ".join([m["metric"] for m in ok_metrics])}</span></div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 8 — ANOMALY DETECTOR
    # ════════════════════════════════════════════════════════════════════════
    with tab8:
        st.markdown('<div class="section-header">Statistical Anomaly Detection</div>', unsafe_allow_html=True)
        st.caption("Identifies unusual patterns in churn, support, usage, and billing data — statistical outliers vs baseline. One-click AI root cause diagnosis.")

        churn_by_ind = query("""
            SELECT industry, COUNT(*) AS total,
                   COUNT(CASE WHEN status='Churned' THEN 1 END) AS churned,
                   ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate
            FROM customers GROUP BY industry ORDER BY churn_rate DESC
        """)
        avg_churn_a = float(churn_by_ind["churn_rate"].mean())
        std_churn_a = float(churn_by_ind["churn_rate"].std())
        outlier_inds = churn_by_ind[churn_by_ind["churn_rate"] > avg_churn_a + std_churn_a]

        ticket_monthly_a = query("""
            SELECT strftime('%Y-%m', created_date) AS month, COUNT(*) AS tickets
            FROM support_tickets GROUP BY month ORDER BY month
        """)
        avg_tix = float(ticket_monthly_a["tickets"].mean())
        std_tix = float(ticket_monthly_a["tickets"].std())
        spike_months_a = ticket_monthly_a[ticket_monthly_a["tickets"] > avg_tix + std_tix]

        low_usage_a = query("""
            WITH uc AS (SELECT customer_id, COUNT(*) AS sessions FROM product_usage GROUP BY customer_id)
            SELECT c.company_name, c.plan_type, c.mrr, c.health_score, COALESCE(u.sessions,0) AS sessions
            FROM customers c LEFT JOIN uc u ON c.customer_id=u.customer_id
            WHERE c.status='Active' ORDER BY sessions ASC LIMIT 15
        """)
        sla_by_cat_a = query("""
            SELECT category,
                   COUNT(CASE WHEN priority='Critical' AND resolution_time_hours>8 THEN 1 END) AS crit_breach,
                   COUNT(CASE WHEN priority='High' AND resolution_time_hours>24 THEN 1 END) AS high_breach,
                   COUNT(*) AS total
            FROM support_tickets GROUP BY category ORDER BY crit_breach DESC
        """)

        anomalies_a = []
        for _, row in outlier_inds.iterrows():
            anomalies_a.append({
                "severity": "HIGH", "type": "Churn Spike", "color": DANGER,
                "title": f"{row['industry']} — {row['churn_rate']}% churn (avg: {avg_churn_a:.1f}%)",
                "detail": f"{row['churned']} of {row['total']} customers lost · {(row['churn_rate']-avg_churn_a):.1f}% above dataset average",
                "action": "Segment deep-dive required. Analyze shared attributes of churned accounts in this vertical."
            })
        for _, row in spike_months_a.iterrows():
            anomalies_a.append({
                "severity": "MEDIUM", "type": "Ticket Volume Spike", "color": WARNING,
                "title": f"{row['month']} — {int(row['tickets'])} tickets (avg: {avg_tix:.0f}/month)",
                "detail": f"+{int(row['tickets']-avg_tix)} above baseline · {round((row['tickets']-avg_tix)/avg_tix*100)}% spike",
                "action": "Investigate what changed: product release, pricing update, or seasonal pattern?"
            })
        hv_low = low_usage_a[low_usage_a["mrr"] > low_usage_a["mrr"].quantile(0.5)]
        if not hv_low.empty:
            anomalies_a.append({
                "severity": "HIGH", "type": "Ghost Accounts", "color": DANGER,
                "title": f"{len(hv_low)} high-MRR active accounts with near-zero product usage",
                "detail": f"Avg MRR: ${hv_low['mrr'].mean():,.0f} · Avg sessions: {hv_low['sessions'].mean():.0f} · 3× churn risk",
                "action": "Proactive CSM outreach required. Low-usage customers churn at 3× the rate of engaged accounts."
            })
        if not sla_by_cat_a.empty:
            top_cat = sla_by_cat_a.iloc[0]
            if int(top_cat["crit_breach"]) > 0:
                anomalies_a.append({
                    "severity": "MEDIUM", "type": "SLA Breach Concentration", "color": WARNING,
                    "title": f"{top_cat['category']} — {int(top_cat['crit_breach'])} critical SLA breaches",
                    "detail": f"Highest-failure category · {int(top_cat['high_breach'])} High-priority breaches too",
                    "action": "Assign dedicated SLA owner for this category. Set queue alert at 6-hour mark."
                })

        st.markdown(f'<div class="alert-critical" style="margin-bottom:16px"><b>🔍 {len(anomalies_a)} anomaly pattern(s) detected</b> — statistical outliers identified vs baseline expectations</div>', unsafe_allow_html=True)

        for a in anomalies_a:
            sev_bg = "rgba(239,68,68,0.15)" if a["severity"] == "HIGH" else "rgba(245,158,11,0.15)"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-left:4px solid {a['color']};border-radius:12px;padding:16px;margin-bottom:10px">
                <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
                    <span style="background:{sev_bg};color:{a['color']};font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px">{a['severity']}</span>
                    <span style="background:#1e3a5f;color:#64748b;font-size:10px;padding:2px 8px;border-radius:4px">{a['type']}</span>
                </div>
                <div style="font-size:14px;font-weight:600;color:#f1f5f9;margin-bottom:4px">{a['title']}</div>
                <div style="font-size:12px;color:#94a3b8;margin-bottom:8px">{a['detail']}</div>
                <div style="font-size:12px;color:#64748b"><b>Recommended action:</b> {a['action']}</div>
            </div>
            """, unsafe_allow_html=True)

        c_anom1, c_anom2 = st.columns(2)
        with c_anom1:
            st.markdown('<div class="section-header">Churn Rate by Industry (Outliers Flagged)</div>', unsafe_allow_html=True)
            bar_colors_a = [DANGER if v > avg_churn_a + std_churn_a else (WARNING if v > avg_churn_a else SUCCESS)
                            for v in churn_by_ind["churn_rate"]]
            fig_anom1 = go.Figure()
            fig_anom1.add_trace(go.Bar(x=churn_by_ind["industry"], y=churn_by_ind["churn_rate"],
                                        marker_color=bar_colors_a, text=churn_by_ind["churn_rate"],
                                        texttemplate="%{text}%", textposition="outside"))
            fig_anom1.add_hline(y=avg_churn_a, line_dash="dot", line_color=WARNING,
                                 annotation_text=f"Avg {avg_churn_a:.1f}%", annotation_position="right")
            fig_anom1.add_hline(y=avg_churn_a + std_churn_a, line_dash="dash", line_color=DANGER,
                                 annotation_text="Outlier threshold", annotation_position="right")
            chart_layout(fig_anom1, 320)
            fig_anom1.update_layout(xaxis=dict(tickangle=30))
            st.plotly_chart(fig_anom1, use_container_width=True)

        with c_anom2:
            st.markdown('<div class="section-header">Monthly Ticket Volume (Spikes Highlighted)</div>', unsafe_allow_html=True)
            spike_flags_a = ticket_monthly_a["tickets"] > avg_tix + std_tix
            fig_anom2 = go.Figure()
            fig_anom2.add_trace(go.Bar(x=ticket_monthly_a["month"], y=ticket_monthly_a["tickets"],
                                        marker_color=[DANGER if s else PRIMARY for s in spike_flags_a],
                                        text=ticket_monthly_a["tickets"], texttemplate="%{text}", textposition="outside"))
            fig_anom2.add_hline(y=avg_tix + std_tix, line_dash="dash", line_color=DANGER,
                                 annotation_text="Spike threshold", annotation_position="right")
            chart_layout(fig_anom2, 320)
            fig_anom2.update_layout(xaxis=dict(tickangle=30))
            st.plotly_chart(fig_anom2, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate AI Root Cause Analysis", type="primary", key="anomaly_ai_btn"):
            if not API_KEY:
                st.error("ANTHROPIC_API_KEY not configured.")
            else:
                anom_summary = "\n".join([f"- [{a['severity']}] {a['type']}: {a['title']}. {a['detail']}" for a in anomalies_a])
                with st.spinner("Claude is diagnosing root causes..."):
                    try:
                        anom_msg = anthropic.Anthropic(api_key=API_KEY).messages.create(
                            model="claude-haiku-4-5-20251001", max_tokens=1500,
                            messages=[{"role": "user", "content": f"""You are a Senior Business Analyst analyzing data anomalies in a B2B SaaS company (Apex Solutions).

ANOMALIES DETECTED:
{anom_summary}

CONTEXT: 500 customers, 22% annual churn, 28hr avg ticket resolution, 82% onboarding completion.

## ROOT CAUSE ANALYSIS
For each anomaly: symptom → cause → root cause (2 levels deep).

## INTERCONNECTIONS
How are these anomalies driving each other?

## PRIORITY FIX ORDER
Which should leadership address first? Why?

## QUICK WINS (next 30 days)
3 immediate actions that begin to reverse these trends. Be specific."""}]
                        )
                        st.markdown("### AI Root Cause Analysis")
                        st.markdown(anom_msg.content[0].text)
                    except Exception as e:
                        st.error(f"API Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — AI FEEDBACK ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Feedback Analyzer":
    st.markdown('<div class="page-title">AI Feedback Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Paste raw customer feedback → Claude AI generates structured BA analysis + user stories in seconds</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        feedback_input = st.text_area("Customer Feedback / Support Tickets", height=260,
            placeholder="Paste customer complaints, support ticket descriptions, survey responses, NPS comments...\n\nExample:\n- 'Dashboard takes forever to load with 3+ filters'\n- 'Charged twice in March, no response from billing for 5 days'\n- 'Salesforce sync broke after last update, contacts duplicating'")

    with col_b:
        st.markdown("#### What Claude will generate")
        for item in ["Sentiment breakdown with %", "Pain points ranked by business impact",
                     "Root cause categories", "4-6 sprint-ready user stories",
                     "Recommended process changes", "Prioritized BA action items"]:
            st.markdown(f"✦ {item}")
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("Analyze with Claude AI", type="primary", use_container_width=True)

    if analyze_btn:
        if not feedback_input.strip():
            st.warning("Paste some feedback first.")
        elif not API_KEY:
            st.error("ANTHROPIC_API_KEY not configured.")
        else:
            with st.spinner("Claude is analyzing..."):
                client = anthropic.Anthropic(api_key=API_KEY)
                prompt = f"""You are a Senior Technical Business Analyst analyzing customer feedback for Apex Solutions, a B2B SaaS company.

Analyze the feedback below and produce a structured BA analysis report.

CUSTOMER FEEDBACK:
{feedback_input}

Structure your output with these exact headers:

## SENTIMENT SUMMARY
Overall sentiment with positive/neutral/negative % breakdown.

## TOP PAIN POINTS (ranked by business impact)
For each: Issue | Impact (High/Medium/Low) | Affected Area | Frequency Signal

## ROOT CAUSE CATEGORIES
Table: Category | Issues | Severity

## AUTO-GENERATED USER STORIES
4-6 stories in format: As a [user], I want [feature], so that [benefit].
Include Acceptance Criteria (Given/When/Then) for each.

## RECOMMENDED PROCESS CHANGES
3-5 specific, actionable changes with: Current State → Change → Expected Outcome.

## BA ACTION ITEMS
4-6 next steps with priority, owner, and deliverable."""

                try:
                    message = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=2500,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    result = message.content[0].text
                    st.markdown("---")
                    st.markdown("### Analysis Report")
                    st.markdown(result)
                    st.download_button("Download Report (.txt)", data=result,
                                       file_name="feedback_analysis_report.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"API Error: {e}")

    with st.expander("Load sample high-priority tickets from the database"):
        sample = query("""
            SELECT t.description, t.category, t.priority, c.company_name
            FROM support_tickets t JOIN customers c ON t.customer_id=c.customer_id
            WHERE t.priority IN ('High','Critical') ORDER BY RANDOM() LIMIT 8
        """)
        st.dataframe(sample, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI REQUIREMENTS GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 AI Requirements Generator":
    st.markdown('<div class="page-title">AI Requirements Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Describe a business problem → Claude AI generates a complete requirements package in seconds</div>', unsafe_allow_html=True)

    col_x, col_y = st.columns([3, 2])
    with col_x:
        problem_statement = st.text_area("Business Problem Statement", height=180,
            placeholder="Example: Our customer success team manually checks health scores every Monday (4 hours). By the time they reach out, customers have already decided to leave. We need an automated early warning system.")

    with col_y:
        stakeholder = st.selectbox("Primary Stakeholder",
            ["Customer Success Manager", "Product Manager", "CTO / Engineering Lead",
             "VP Sales", "CFO / Finance", "Operations Manager"])
        priority_level = st.selectbox("Priority", ["High", "Medium", "Low"])
        output_type = st.multiselect("Generate",
            ["BRD Excerpt", "User Stories", "Acceptance Criteria", "UAT Test Cases", "Risk Register"],
            default=["BRD Excerpt", "User Stories", "Acceptance Criteria", "UAT Test Cases"])

    generate_btn = st.button("Generate Requirements Package", type="primary")

    if generate_btn:
        if not problem_statement.strip():
            st.warning("Describe the business problem first.")
        elif not output_type:
            st.warning("Select at least one output type.")
        elif not API_KEY:
            st.error("ANTHROPIC_API_KEY not configured.")
        else:
            with st.spinner("Generating requirements package..."):
                client = anthropic.Anthropic(api_key=API_KEY)
                outputs = ", ".join(output_type)
                prompt = f"""You are a Senior Technical Business Analyst at Apex Solutions, a B2B SaaS company.

PROBLEM STATEMENT: {problem_statement}
PRIMARY STAKEHOLDER: {stakeholder}
PRIORITY: {priority_level}

Generate the following BA deliverables: {outputs}

{"## BRD EXCERPT\nInclude: Problem Statement, Business Objectives (3-4), Scope (In/Out), Assumptions, Constraints, Success Metrics KPI table." if "BRD Excerpt" in output_type else ""}
{"## USER STORIES\n5-7 stories: As a [persona], I want [feature], so that [benefit]. Include Story Points and MoSCoW priority." if "User Stories" in output_type else ""}
{"## ACCEPTANCE CRITERIA\nGiven/When/Then format, 2-4 criteria per story." if "Acceptance Criteria" in output_type else ""}
{"## UAT TEST CASES\n5-6 test cases: Test ID | Scenario | Steps | Expected Result | Pass/Fail Criteria." if "UAT Test Cases" in output_type else ""}
{"## RISK REGISTER\n5 risks: Risk | Probability | Impact | Mitigation Strategy." if "Risk Register" in output_type else ""}

Be specific, professional, and grounded in real BA practice."""

                try:
                    message = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=3000,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    result = message.content[0].text
                    st.markdown("---")
                    st.markdown("### Requirements Package")
                    st.markdown(result)
                    st.download_button("Download Package (.txt)", data=result,
                                       file_name="requirements_package.txt", mime="text/plain")
                except Exception as e:
                    st.error(f"API Error: {e}")

    with st.expander("Quick-load example problems"):
        examples = {
            "Automated Churn Early Warning": "Our CS team manually checks health scores every Monday (4 hrs). No automated alerts exist. By the time they reach out, customers have decided to leave. We need automated risk detection with Slack alerts.",
            "Self-Service Onboarding Portal": "New customers rely on CS for every onboarding step, taking 30-60 days. 60% of support tickets are onboarding-related. We need a self-service portal with guided checklists and progress tracking.",
            "Unified Support Dashboard": "Support team uses 3 separate tools. Context switching causes delays and SLA breaches. We need a unified dashboard with SLA alerts, escalation workflows, and automated CSAT surveys.",
        }
        for title, text in examples.items():
            if st.button(f"Load: {title}"):
                st.info(f"Copy into the text box above:\n\n{text}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — AI INSIGHTS ENGINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧠 AI Insights Engine":
    st.markdown('<div class="page-title">AI Insights Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Claude AI reads the live business data and generates a real executive intelligence brief — just like a McKinsey consultant would</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        focus_area = st.selectbox("Focus Area", [
            "Full Business Health Review",
            "Churn Risk & Revenue Impact",
            "Customer Success Performance",
            "Support Operations Analysis",
            "Onboarding Process Effectiveness",
        ])
    with col2:
        audience = st.selectbox("Report For", ["CEO / Board", "VP Customer Success", "Product Manager", "Operations Manager"])

    generate_insights = st.button("Generate AI Executive Brief", type="primary", use_container_width=False)

    if generate_insights:
        if not API_KEY:
            st.error("ANTHROPIC_API_KEY not configured.")
        else:
            with st.spinner("Claude is analyzing your business data..."):

                # Pull live metrics
                kpi = query("""
                    SELECT
                        COUNT(CASE WHEN status='Active' THEN 1 END) AS active,
                        COUNT(CASE WHEN status='Churned' THEN 1 END) AS churned,
                        ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
                        ROUND(SUM(CASE WHEN status='Active' THEN mrr ELSE 0 END),0) AS mrr,
                        ROUND(AVG(CASE WHEN status='Active' THEN health_score END),1) AS avg_health,
                        ROUND(AVG(CASE WHEN status='Active' THEN nps_score END),1) AS avg_nps
                    FROM customers
                """).iloc[0]

                churn_by_plan = query("""
                    SELECT plan_type,
                           ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
                           ROUND(SUM(CASE WHEN status='Churned' THEN mrr ELSE 0 END),0) AS mrr_lost
                    FROM customers GROUP BY plan_type ORDER BY churn_rate DESC
                """).to_string(index=False)

                top_industries = query("""
                    SELECT industry,
                           ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate
                    FROM customers GROUP BY industry ORDER BY churn_rate DESC LIMIT 5
                """).to_string(index=False)

                support = query("""
                    SELECT COUNT(*) AS total_tickets,
                           COUNT(CASE WHEN status IN ('Open','In Progress') THEN 1 END) AS open_tickets,
                           ROUND(AVG(resolution_time_hours),1) AS avg_resolution_hrs,
                           ROUND(AVG(satisfaction_score),2) AS avg_csat,
                           COUNT(CASE WHEN priority='Critical' AND resolution_time_hours>8 THEN 1 END) AS sla_breaches
                    FROM support_tickets
                """).iloc[0]

                onboarding = query("""
                    SELECT ROUND(COUNT(CASE WHEN completed=1 THEN 1 END)*100.0/COUNT(*),1) AS completion_rate,
                           COUNT(CASE WHEN completed=0 THEN 1 END) AS incomplete_count,
                           ROUND(AVG(CASE WHEN completed=1 THEN days_to_complete END),1) AS avg_days
                    FROM onboarding
                """).iloc[0]

                top_blockers = query("""
                    SELECT blocker, COUNT(*) AS count FROM onboarding
                    WHERE completed=0 AND blocker!='None'
                    GROUP BY blocker ORDER BY count DESC LIMIT 3
                """).to_string(index=False)

                at_risk_count = query("""
                    SELECT COUNT(*) AS cnt FROM (
                        WITH t AS (SELECT customer_id, COUNT(*) AS tickets FROM support_tickets GROUP BY customer_id),
                             u AS (SELECT customer_id, COUNT(*) AS sessions FROM product_usage GROUP BY customer_id),
                             o AS (SELECT customer_id, completed FROM onboarding)
                        SELECT c.customer_id,
                            (CASE WHEN c.health_score<60 THEN 30 WHEN c.health_score<75 THEN 15 ELSE 0 END)
                            +(CASE WHEN COALESCE(t.tickets,0)>15 THEN 20 WHEN COALESCE(t.tickets,0)>8 THEN 10 ELSE 0 END)
                            +(CASE WHEN COALESCE(u.sessions,0)<3 THEN 25 WHEN COALESCE(u.sessions,0)<8 THEN 12 ELSE 0 END)
                            +(CASE WHEN COALESCE(o.completed,0)=0 THEN 15 ELSE 0 END)
                            +(CASE WHEN c.nps_score<5 THEN 10 ELSE 0 END) AS risk_score
                        FROM customers c
                        LEFT JOIN t ON c.customer_id=t.customer_id
                        LEFT JOIN u ON c.customer_id=u.customer_id
                        LEFT JOIN o ON c.customer_id=o.customer_id
                        WHERE c.status='Active'
                    ) WHERE risk_score >= 50
                """).iloc[0]["cnt"]

                data_summary = f"""
LIVE BUSINESS DATA — APEX SOLUTIONS B2B SAAS:

CUSTOMER METRICS:
- Active customers: {int(kpi['active'])}
- Churned customers: {int(kpi['churned'])}
- Overall churn rate: {kpi['churn_rate']}%
- Total MRR: ${int(kpi['mrr']):,}
- Total ARR: ${int(kpi['mrr'])*12:,}
- Avg customer health score: {kpi['avg_health']}/100
- Avg NPS score: {kpi['avg_nps']}/10
- At-risk customers (score ≥50): {int(at_risk_count)} active accounts

CHURN BY PLAN:
{churn_by_plan}

TOP CHURNING INDUSTRIES:
{top_industries}

SUPPORT OPERATIONS:
- Total tickets: {int(support['total_tickets']):,}
- Open/In-Progress tickets: {int(support['open_tickets']):,}
- Avg resolution time: {support['avg_resolution_hrs']} hours
- Avg CSAT score: {support['avg_csat']}/5
- Critical SLA breaches: {int(support['sla_breaches'])}

ONBOARDING:
- Completion rate: {onboarding['completion_rate']}%
- Incomplete onboardings: {int(onboarding['incomplete_count'])}
- Avg days to complete: {onboarding['avg_days']} days
- Top blockers: {top_blockers}
"""

                client = anthropic.Anthropic(api_key=API_KEY)
                prompt = f"""You are a Principal Business Analyst and Strategy Consultant preparing an executive intelligence brief for {audience} at Apex Solutions, a B2B SaaS company.

Focus Area: {focus_area}

{data_summary}

Write a sharp, data-driven executive brief. No fluff. Think McKinsey slide narrative meets BA precision.

Structure:
## EXECUTIVE SUMMARY
2-3 sentences. The single most important thing leadership needs to know RIGHT NOW.

## KEY FINDINGS
5-7 specific, numbered findings. Each must cite an actual number from the data. Bold the metric.

## ROOT CAUSE ANALYSIS
What's actually driving these numbers? Go 2 levels deep. Don't just describe symptoms.

## BUSINESS IMPACT QUANTIFICATION
Calculate the real dollar/business impact of the top 2-3 problems. Show your math.
Example: "22% churn rate on ${int(kpi['mrr']):,} MRR = $X ARR at risk annually."

## STRATEGIC RECOMMENDATIONS
4-5 prioritized recommendations. For each: action, owner, timeline, expected outcome with metric.
Format: Priority (P1/P2/P3) | Action | Owner | Timeline | Expected Impact

## EARLY WARNING SIGNALS
What leading indicators should {audience} watch weekly? List 4-5 specific metrics with thresholds.

Write with authority. Use active voice. Every sentence must earn its place."""

                try:
                    message = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=3000,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    result = message.content[0].text

                    st.markdown("---")
                    st.markdown(f"### Executive Intelligence Brief — {focus_area}")
                    st.caption(f"Generated for: {audience} · Based on live data from {int(kpi['active'])} active customers")
                    st.markdown(result)

                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.download_button("Download Brief (.txt)", data=result,
                                           file_name="executive_brief.txt", mime="text/plain", use_container_width=True)
                    with col_dl2:
                        linkedin_prompt = f"Write a short LinkedIn post (150 words max) announcing an insight from this analysis. Make it professional, data-driven, and end with a question to drive engagement:\n\n{result[:1000]}"
                        st.session_state["linkedin_prompt"] = linkedin_prompt
                        st.info("Tip: Use this brief in your next interview. Say: 'Here's the kind of insight I'd deliver in week one.'")
                except Exception as e:
                    st.error(f"API Error: {e}")
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#051525 0%,#0d1b2a 40%,#1a2d40 100%);
             border:1px solid #1e3a5f;border-radius:16px;padding:48px 32px;text-align:center;margin-top:20px;
             position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                 background:linear-gradient(90deg,transparent,#4F8EF7,#22c55e,#4F8EF7,transparent)"></div>
            <div class="float-icon">🧠</div>
            <div style="font-size:24px;font-weight:800;color:#f1f5f9;margin:16px 0 8px;letter-spacing:-0.5px">
                AI reads your data. You present the insight.
            </div>
            <div style="font-size:13px;color:#64748b;max-width:480px;margin:0 auto 24px;line-height:1.8">
                Select a focus area, choose your audience, and Claude analyzes 16,000+ rows of live data —
                churn signals, support failures, onboarding gaps — and writes the brief a McKinsey consultant would charge $50K for.
            </div>
            <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap">
                <span class="badge badge-blue">500 Customers Analyzed</span>
                <span class="badge badge-green">Live SQLite Data</span>
                <span class="badge badge-purple">Claude Sonnet Powered</span>
                <span class="badge badge-yellow">Executive Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — INTERVIEW SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Interview Simulator":
    st.markdown('<div class="page-title">Interview Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Paste any Technical BA job description → Claude generates tailored talking points, likely questions, and rehearsal answers — all grounded in BridgeIQ</div>', unsafe_allow_html=True)

    st.markdown("---")

    jd_input = st.text_area("Paste the Job Description here", height=250,
        placeholder="Paste the full job description from LinkedIn, Indeed, or any job board...\n\nExample:\nWe are looking for a Technical Business Analyst with 3-5 years of experience...\nRequirements: SQL, Agile, stakeholder management, process mapping, Jira...\nNice to have: Power BI, AI/ML familiarity, Salesforce...")

    col_a, col_b = st.columns(2)
    with col_a:
        company_name = st.text_input("Company Name (optional)", placeholder="e.g. Goldman Sachs, Stripe, Uber")
    with col_b:
        role_title = st.text_input("Role Title (optional)", placeholder="e.g. Technical Business Analyst")

    simulate_btn = st.button("Simulate Interview with Claude", type="primary")

    if simulate_btn:
        if not jd_input.strip():
            st.warning("Paste a job description first.")
        elif not API_KEY:
            st.error("ANTHROPIC_API_KEY not configured.")
        else:
            with st.spinner("Claude is preparing your interview prep..."):
                client = anthropic.Anthropic(api_key=API_KEY)

                project_summary = """
CANDIDATE'S PROJECT — BRIDGEIQ:
- Built end-to-end AI-powered BI platform for a fictional B2B SaaS company (Apex Solutions)
- Designed 6-table data model from scratch, generated 16,000+ rows synthetic data
- Wrote 10 SQL queries covering: churn analysis, revenue trends, SLA compliance, cohort retention, at-risk scoring (CTEs + window functions)
- Built 3-page Streamlit app with Plotly dashboards deployed live on Streamlit Cloud
- Integrated Claude AI API for: feedback analysis (→ user stories), requirements generation (→ BRD + UAT), executive intelligence briefs
- Delivered full BA artifact suite: BRD (11 sections), 15 Agile user stories, AS-IS/TO-BE process maps, risk register, data dictionary (48 columns), RACI matrix, 10-slide exec deck
- Stack: Python 3.11, SQLite, Anthropic Claude API, Streamlit, Plotly, pandas, Git/GitHub
- Background: CS Bachelor's + CS Master's, IEEE-published researcher in AI/ML
"""

                prompt = f"""You are a senior interview coach preparing a Technical BA candidate for a specific job interview.

JOB DESCRIPTION:
{jd_input}

COMPANY: {company_name or 'the company'}
ROLE: {role_title or 'Technical Business Analyst'}

{project_summary}

Generate a complete interview preparation guide. Be specific. Tie EVERYTHING back to the BridgeIQ project.

## JD MATCH ANALYSIS
Score the candidate's fit: X/10. List top 5 matching skills with evidence from the project. List 1-2 gaps and how to address them.

## 5 KILLER TALKING POINTS
For each JD requirement, craft a 2-3 sentence talking point that connects BridgeIQ to that requirement.
Format: **JD Requirement** → Talking Point

## 8 LIKELY INTERVIEW QUESTIONS
Mix of: behavioral (Tell me about a time...), technical (How would you...), and situational (What would you do if...).
For each: the question + a 3-4 sentence model answer grounded in BridgeIQ.

## KEYWORDS TO WEAVE IN
15 keywords/phrases from the JD that the candidate should naturally use in their answers.

## OPENING PITCH (60 seconds)
Write the candidate's opening "Tell me about yourself" answer tailored to THIS specific role and company.

## QUESTIONS TO ASK THE INTERVIEWER
5 smart questions that show strategic thinking. Avoid generic questions.

Be direct, specific, and brutally useful."""

                try:
                    message = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=4000,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    result = message.content[0].text

                    st.markdown("---")
                    st.markdown(f"### Interview Prep — {role_title or 'Technical BA'} at {company_name or 'the company'}")
                    st.markdown(result)

                    st.download_button("Download Interview Prep (.txt)", data=result,
                                       file_name=f"interview_prep_{company_name or 'company'}.txt",
                                       mime="text/plain", use_container_width=False)
                except Exception as e:
                    st.error(f"API Error: {e}")
    else:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#051525 0%,#0d1b2a 40%,#1a2d40 100%);
             border:1px solid #1e3a5f;border-radius:16px;padding:48px 32px;text-align:center;margin-top:20px;
             position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;
                 background:linear-gradient(90deg,transparent,#f59e0b,#ef4444,#f59e0b,transparent)"></div>
            <div class="float-icon">🎯</div>
            <div style="font-size:24px;font-weight:800;color:#f1f5f9;margin:16px 0 8px;letter-spacing:-0.5px">
                Walk into every interview overprepared.
            </div>
            <div style="font-size:13px;color:#64748b;max-width:480px;margin:0 auto 24px;line-height:1.8">
                Paste any BA job description. Claude matches it to BridgeIQ, generates tailored talking points,
                8 likely interview questions with model answers, and your 60-second pitch. Specific to that role and company.
            </div>
            <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap">
                <span class="badge badge-yellow">JD Match Score</span>
                <span class="badge badge-blue">Tailored Talking Points</span>
                <span class="badge badge-green">Model Answers</span>
                <span class="badge badge-red">60-Second Pitch</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — CUSTOMER 360
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Customer 360":
    st.markdown('<div class="page-title">Customer 360</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Full account intelligence in one view — what every CSM needs before any customer interaction</div>', unsafe_allow_html=True)
    st.markdown("---")

    customers_list = query("SELECT customer_id, company_name, plan_type, status FROM customers ORDER BY company_name")
    options = {f"{r['company_name']} ({r['plan_type']}) — {r['status']}": r['customer_id']
               for _, r in customers_list.iterrows()}
    selected_label = st.selectbox("Search & Select Customer", list(options.keys()))
    sid = options[selected_label]

    cust = query(f"SELECT * FROM customers WHERE customer_id='{sid}'").iloc[0]
    txns = query(f"SELECT transaction_date, transaction_type, amount, status, payment_method FROM transactions WHERE customer_id='{sid}' ORDER BY transaction_date DESC LIMIT 20")
    tickets = query(f"SELECT ticket_id, category, priority, status, created_date, resolution_time_hours, satisfaction_score FROM support_tickets WHERE customer_id='{sid}' ORDER BY created_date DESC LIMIT 15")
    usage = query(f"SELECT feature, COUNT(*) AS sessions, ROUND(AVG(session_minutes),1) AS avg_mins, SUM(actions_count) AS total_actions FROM product_usage WHERE customer_id='{sid}' GROUP BY feature ORDER BY sessions DESC")
    onb = query(f"SELECT * FROM onboarding WHERE customer_id='{sid}'")

    risk_data = query(f"""
        WITH t AS (SELECT COUNT(*) AS tickets FROM support_tickets WHERE customer_id='{sid}'),
             u AS (SELECT COUNT(*) AS sessions FROM product_usage WHERE customer_id='{sid}'),
             o AS (SELECT completed FROM onboarding WHERE customer_id='{sid}')
        SELECT
            (CASE WHEN {float(cust['health_score'])}<60 THEN 30 WHEN {float(cust['health_score'])}<75 THEN 15 ELSE 0 END) AS hp,
            (CASE WHEN t.tickets>15 THEN 20 WHEN t.tickets>8 THEN 10 ELSE 0 END) AS tp,
            (CASE WHEN u.sessions<3 THEN 25 WHEN u.sessions<8 THEN 12 ELSE 0 END) AS up,
            (CASE WHEN o.completed=0 THEN 15 ELSE 0 END) AS op,
            (CASE WHEN {int(cust['nps_score'])}<5 THEN 10 ELSE 0 END) AS np,
            t.tickets, u.sessions
        FROM t, u, o
    """).iloc[0]
    risk_total = int(risk_data["hp"] + risk_data["tp"] + risk_data["up"] + risk_data["op"] + risk_data["np"])
    risk_color = DANGER if risk_total >= 50 else (WARNING if risk_total >= 30 else SUCCESS)
    risk_label = "CRITICAL RISK" if risk_total >= 50 else ("HIGH RISK" if risk_total >= 30 else "LOW RISK")

    c1, c2, c3, c4, c5 = st.columns(5)
    mrr_val = int(cust["mrr"])
    health = float(cust["health_score"])
    hc = SUCCESS if health >= 75 else (WARNING if health >= 55 else DANGER)
    sc = DANGER if cust["status"] == "Churned" else SUCCESS
    for col, (lbl, val, sub, border) in zip([c1,c2,c3,c4,c5], [
        ("Company",    cust["company_name"],     f"{cust['plan_type']} · {cust['industry']}", PRIMARY),
        ("MRR",        f"${mrr_val:,}",          f"ARR: ${mrr_val*12:,}", PRIMARY),
        ("Health",     f"{health}/100",           f"NPS: {cust['nps_score']}/10", hc),
        ("Risk Score", f"{risk_total}/100",       risk_label, risk_color),
        ("Status",     cust["status"],            f"Since {cust['contract_start']}", sc),
    ]):
        col.markdown(f"""<div class="kpi-card" style="border-left-color:{border}">
            <div class="kpi-label">{lbl}</div>
            <div class="kpi-value" style="font-size:18px;color:{border}">{val}</div>
            <div class="kpi-delta-neutral">{sub}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown('<div class="section-header">Risk Factor Breakdown</div>', unsafe_allow_html=True)
        rf_names = ["Health Score", "Ticket Volume", "Low Usage", "Onboarding", "NPS Score"]
        rf_vals  = [int(risk_data["hp"]), int(risk_data["tp"]), int(risk_data["up"]), int(risk_data["op"]), int(risk_data["np"])]
        fig_rf = go.Figure(go.Bar(
            x=rf_vals, y=rf_names, orientation="h",
            marker_color=[DANGER if v >= 20 else WARNING if v >= 10 else SUCCESS for v in rf_vals],
            text=[f"{v}pts" for v in rf_vals], textposition="outside",
        ))
        chart_layout(fig_rf, 260)
        fig_rf.update_layout(xaxis_range=[0, 35], margin=dict(t=10, b=10, l=10, r=50))
        st.plotly_chart(fig_rf, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Product Usage by Feature</div>', unsafe_allow_html=True)
        if not usage.empty:
            fig_u = px.bar(usage, x="feature", y="sessions",
                           color="sessions", color_continuous_scale=["#1e3a5f", PRIMARY],
                           text="avg_mins",
                           labels={"feature": "", "sessions": "Sessions"},
                           hover_data={"total_actions": True, "avg_mins": True})
            fig_u.update_traces(texttemplate="%{text}m avg", textposition="outside")
            fig_u.update_layout(coloraxis_showscale=False)
            chart_layout(fig_u, 260)
            st.plotly_chart(fig_u, use_container_width=True)
        else:
            st.info("No usage data recorded for this customer.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">Transaction History</div>', unsafe_allow_html=True)
        if not txns.empty:
            txns["amount"] = txns["amount"].apply(lambda x: f"${x:,.0f}")
            st.dataframe(txns, use_container_width=True, hide_index=True, height=280)
        else:
            st.info("No transactions found.")

    with col_b:
        st.markdown('<div class="section-header">Support Ticket History</div>', unsafe_allow_html=True)
        if not tickets.empty:
            def style_prio(v):
                if v == "Critical": return "color:#ef4444;font-weight:700"
                if v == "High": return "color:#f59e0b;font-weight:600"
                return ""
            st.dataframe(tickets.style.map(style_prio, subset=["priority"]),
                         use_container_width=True, hide_index=True, height=280)
        else:
            st.info("No support tickets found.")

    st.markdown("---")
    if not onb.empty:
        ob = onb.iloc[0]
        oc = SUCCESS if ob["completed"] == 1 else DANGER
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-left:4px solid {oc};border-radius:12px;padding:20px">
            <div style="font-size:14px;font-weight:600;color:#f1f5f9;margin-bottom:12px">Onboarding Status</div>
            <div style="display:flex;gap:32px;flex-wrap:wrap">
                <div><div style="font-size:11px;color:#64748b">STATUS</div><div style="font-size:16px;font-weight:700;color:{oc}">{'COMPLETED' if ob['completed']==1 else 'INCOMPLETE'}</div></div>
                <div><div style="font-size:11px;color:#64748b">STAGE</div><div style="font-size:16px;color:#f1f5f9">{ob['stage']}</div></div>
                <div><div style="font-size:11px;color:#64748b">STARTED</div><div style="font-size:16px;color:#f1f5f9">{ob['start_date']}</div></div>
                <div><div style="font-size:11px;color:#64748b">DAYS TO COMPLETE</div><div style="font-size:16px;color:#f1f5f9">{int(ob['days_to_complete']) if ob['days_to_complete'] else 'N/A'}</div></div>
                <div><div style="font-size:11px;color:#64748b">BLOCKER</div><div style="font-size:16px;color:{'#ef4444' if ob['blocker']!='None' else '#22c55e'}">{ob['blocker']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generate AI Account Intelligence Summary", type="primary"):
        if not API_KEY:
            st.error("ANTHROPIC_API_KEY not configured.")
        else:
            with st.spinner("Claude is analyzing this account..."):
                acct_data = f"""
CUSTOMER: {cust['company_name']} | Plan: {cust['plan_type']} | Industry: {cust['industry']} | Region: {cust['region']}
MRR: ${mrr_val:,} | ARR: ${mrr_val*12:,} | Health: {cust['health_score']}/100 | NPS: {cust['nps_score']}/10
Status: {cust['status']} | Risk Score: {risk_total}/100 ({risk_label})
Risk breakdown — Health: {int(risk_data['hp'])}pts, Tickets: {int(risk_data['tp'])}pts ({int(risk_data['tickets'])} total), Usage: {int(risk_data['up'])}pts ({int(risk_data['sessions'])} sessions), Onboarding: {int(risk_data['op'])}pts, NPS: {int(risk_data['np'])}pts
Product usage: {usage.to_string(index=False) if not usage.empty else 'No usage data'}
Tickets: {len(tickets)} recent | Transactions: {len(txns)} recent
"""
                try:
                    msg = anthropic.Anthropic(api_key=API_KEY).messages.create(
                        model="claude-haiku-4-5-20251001", max_tokens=1200,
                        messages=[{"role": "user", "content": f"""You are a CSM reviewing an account 5 minutes before a call.

{acct_data}

## ACCOUNT SITUATION (2-3 sentences)
Current state. Be direct.

## TOP 3 RISK SIGNALS
Signal → what it means → what to do

## RECOMMENDED NEXT ACTIONS (next 7 days)
3 specific actions.

## TALKING POINTS FOR THE CALL
2-3 starters based on their data. Be sharp."""}]
                    )
                    st.markdown("### Account Intelligence Summary")
                    st.markdown(msg.content[0].text)
                except Exception as e:
                    st.error(f"API Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — BA ARTIFACTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📐 BA Artifacts":
    st.markdown('<div class="page-title">BA Artifacts Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Every deliverable from the BridgeIQ engagement — live in the app, not buried in a PDF</div>', unsafe_allow_html=True)

    art_tab1, art_tab2, art_tab3, art_tab4, art_tab5 = st.tabs(["📋 User Stories", "⚠️ Risk Register", "👥 RACI Matrix", "🗺️ Process Maps", "🔗 Traceability"])

    with art_tab1:
        st.markdown('<div class="section-header">15 Sprint-Ready User Stories</div>', unsafe_allow_html=True)
        st.caption("MoSCoW prioritized · Story points estimated · Jira-importable")

        fa, fb = st.columns(2)
        with fa:
            f_pri = st.multiselect("Priority", ["Must Have", "Should Have", "Could Have"],
                                   default=["Must Have", "Should Have", "Could Have"], key="us_pri")
        with fb:
            f_epc = st.multiselect("Epic", ["Customer Health","Onboarding","Support","Analytics","AI Features"],
                                   default=["Customer Health","Onboarding","Support","Analytics","AI Features"], key="us_epc")

        stories = [
            ("US-01","Customer Health","Customer Success Manager","see a real-time composite risk score for each active customer","immediately identify which accounts need attention without manual data pulling","Must Have",8,"In Progress","Dashboard shows risk 0-100 · Updates within 24hrs · Color coded · Click opens detail profile"),
            ("US-02","Customer Health","Customer Success Manager","receive a Slack alert when risk score jumps 15+ points in 7 days","proactively reach out before the customer decides to cancel","Must Have",5,"To Do","Slack sent within 1hr · Includes name/plan/MRR/top 3 factors · No duplicate alerts in 24hrs"),
            ("US-03","Onboarding","Customer Success Manager","see which onboarding stage each customer is in and how long they've been stuck","intervene early when customers hit blockers","Must Have",5,"To Do","All 5 stages shown · Days-in-stage counter · Red flag if stuck >5 days · Blocker field visible"),
            ("US-04","Onboarding","New Customer","receive a guided onboarding checklist immediately after account creation","set up the platform without waiting for a CS call","Must Have",8,"To Do","Checklist emailed within 1hr · 5 stages with time estimates · Customer marks steps complete"),
            ("US-05","Support","Support Team Lead","view a live dashboard of open tickets, SLA compliance, and avg resolution by category","allocate team resources proactively and prevent SLA breaches","Must Have",8,"To Do","Refreshes every 15min · SLA breach indicator per ticket · Escalated tickets highlighted"),
            ("US-06","Support","Customer","receive automated ticket status updates on assignment and resolution","know my issue is being handled without following up manually","Should Have",3,"To Do","Email on status change · Resolution includes fix summary + KB link · CSAT survey included"),
            ("US-07","Analytics","VP Customer Success","see a monthly executive report with churn trend, onboarding completion, and MRR at risk","present accurate metrics to the board without manual data compilation","Must Have",5,"To Do","Auto-generated 1st of month · MoM delta · Downloadable · Prior 6 months trend"),
            ("US-08","AI Features","Business Analyst","paste raw customer feedback and receive structured pain point analysis + user stories","translate unstructured feedback into backlog-ready requirements 10x faster","Should Have",8,"To Do","AI returns within 15s · Sentiment % + ranked pain points + 4-6 user stories · Download option"),
            ("US-09","AI Features","Business Analyst","input a business problem and auto-generate a BRD excerpt with user stories and UAT test cases","produce first-draft requirements 5x faster","Should Have",8,"To Do","Output within 20s · BRD includes objectives/scope/assumptions · Min 5 user stories + 5 UAT cases"),
            ("US-10","Analytics","CSM","filter the customer dashboard by plan, region, and industry","focus analysis on my segment without irrelevant data","Should Have",3,"To Do","Filter panel with dropdowns · All charts update dynamically · Filter persists during session"),
            ("US-11","Customer Health","Data Engineer","have all health signals in a SQL schema with a documented data dictionary","build reliable pipelines without reverse-engineering undocumented tables","Should Have",5,"To Do","Schema documented · ERD published · FK relationships enforced · Data dictionary as CSV"),
            ("US-12","Onboarding","CS Director","receive a weekly automated report on onboarding completion and top 3 blockers","identify systemic onboarding failures and prioritize fixes","Could Have",3,"To Do","Emailed every Monday 9AM · Completion rate by plan · Top 3 blockers · 4-week trend"),
            ("US-13","Support","Support Agent","see all previous tickets for a customer before responding to a new one","provide context-aware responses without asking customers to repeat","Could Have",3,"To Do","History accessible from ticket detail · Sorted by date desc · Loads in <2s"),
            ("US-14","Analytics","CFO","see projected MRR at risk based on at-risk cohort and historical churn","make informed decisions on CS resourcing and retention budget","Could Have",5,"To Do","MRR at risk = sum of MRR for risk≥50 · Shown as $ and % · Daily update"),
            ("US-15","AI Features","Product Manager","have AI-generated stories auto-tagged with story points and MoSCoW priority","import them into Jira with minimal manual editing","Could Have",3,"To Do","Story points by complexity · MoSCoW tag applied · Formatted for Jira CSV import"),
        ]
        pc = {"Must Have": PRIMARY, "Should Have": WARNING, "Could Have": MUTED}
        sc2 = {"In Progress": SUCCESS, "To Do": MUTED}
        filtered = [s for s in stories if s[5] in f_pri and s[1] in f_epc]
        st.caption(f"Showing {len(filtered)} of 15 stories")
        for s in filtered:
            sid2, epic, persona, want, benefit, pri, pts, stat, ac = s
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-left:4px solid {pc[pri]};border-radius:12px;padding:16px;margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                    <div style="display:flex;gap:8px;align-items:center">
                        <span style="background:#1e3a5f;color:#4F8EF7;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px">{sid2}</span>
                        <span style="background:rgba(100,116,139,0.15);color:#94a3b8;font-size:11px;padding:2px 8px;border-radius:4px">{epic}</span>
                        <span style="color:{pc[pri]};font-size:11px;font-weight:600">{pri}</span>
                    </div>
                    <div style="display:flex;gap:12px">
                        <span style="color:#64748b;font-size:11px">{pts} pts</span>
                        <span style="color:{sc2[stat]};font-size:11px;font-weight:600">{stat}</span>
                    </div>
                </div>
                <div style="font-size:13px;color:#f1f5f9;margin-bottom:6px">
                    <span style="color:#64748b">As a</span> <b style="color:#4F8EF7">{persona}</b><span style="color:#64748b">, I want to</span> {want}, <span style="color:#64748b">so that</span> {benefit}.
                </div>
                <div style="font-size:11px;color:#64748b"><b>AC:</b> {ac}</div>
            </div>
            """, unsafe_allow_html=True)

    with art_tab2:
        st.markdown('<div class="section-header">Risk Register — 6 Identified Risks</div>', unsafe_allow_html=True)
        st.caption("Probability × Impact scoring · Mitigation strategies · Owners assigned")
        risks = [
            ("R-01","Low CSM adoption of new platform","Organizational","High","High",9,
             "Dedicated onboarding (2 sessions), 30-day success metrics, executive sponsorship from VP CS","VP Customer Success","Open"),
            ("R-02","Data quality issues in legacy systems","Technical","Medium","High",6,
             "Data audit before migration, validation rules at ETL layer, fallback to manual override","Data Engineering Lead","Open"),
            ("R-03","Risk score misclassifies healthy customers","Model Accuracy","Medium","Medium",4,
             "Back-test against 6-month churn history, set threshold conservatively, monthly calibration review","Business Analyst","Mitigating"),
            ("R-04","Scope creep from stakeholder requests","Scope","High","Medium",6,
             "MoSCoW prioritization enforced, formal change request via Jira, weekly sprint review to guard scope","Project Manager","Open"),
            ("R-05","API rate limits during high usage","Technical","Low","Medium",2,
             "Implement request throttling, cache common AI responses 1hr, fallback message if API unavailable","Engineering Lead","Mitigated"),
            ("R-06","Customer data privacy / GDPR gap","Compliance","Low","High",3,
             "Legal review of data storage and AI processing, anonymization for AI prompts, data retention policy","Legal / Compliance","Mitigating"),
        ]
        sco_c = {9: DANGER, 6: WARNING, 4: PRIMARY, 3: PRIMARY, 2: SUCCESS}
        prob_c = {"High": DANGER, "Medium": WARNING, "Low": SUCCESS}
        for r in risks:
            rid, name, cat, prob, imp, score, mit, owner, stat2 = r
            sc_col = sco_c.get(score, MUTED)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-left:4px solid {sc_col};border-radius:12px;padding:16px;margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
                    <div>
                        <span style="background:#1e3a5f;color:#4F8EF7;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;margin-right:8px">{rid}</span>
                        <span style="font-size:14px;font-weight:600;color:#f1f5f9">{name}</span>
                        <span style="background:rgba(100,116,139,0.15);color:#64748b;font-size:11px;padding:2px 8px;border-radius:4px;margin-left:8px">{cat}</span>
                    </div>
                    <div style="display:flex;gap:8px;align-items:center">
                        <span style="font-size:11px;color:{prob_c[prob]}">P: {prob}</span>
                        <span style="font-size:11px;color:{prob_c[imp]}">I: {imp}</span>
                        <span style="background:{sc_col};color:#fff;font-size:12px;font-weight:700;padding:2px 10px;border-radius:20px">Score: {score}</span>
                    </div>
                </div>
                <div style="font-size:12px;color:#94a3b8;margin-bottom:6px"><b>Mitigation:</b> {mit}</div>
                <div style="font-size:11px;color:#64748b"><b>Owner:</b> {owner} &nbsp;·&nbsp; <b>Status:</b> {stat2}</div>
            </div>
            """, unsafe_allow_html=True)

    with art_tab3:
        st.markdown('<div class="section-header">RACI Matrix</div>', unsafe_allow_html=True)
        st.caption("R = Responsible · A = Accountable · C = Consulted · I = Informed")
        raci = pd.DataFrame({
            "Activity": ["Define business requirements","Design data model","Develop ETL pipeline",
                         "Build dashboard","Define risk scoring logic","Write user stories",
                         "Approve BRD","UAT sign-off","Deploy to production","Train CSM team",
                         "Monitor system health","Post-launch review"],
            "Business Analyst": ["R","C","I","C","R","R","C","R","I","C","I","R"],
            "Engineering Lead":  ["C","R","R","R","C","I","I","C","R","I","R","C"],
            "VP Customer Success":["A","I","I","I","A","A","A","A","I","A","A","A"],
            "Data Engineer":      ["C","R","R","I","C","I","I","C","C","I","R","C"],
            "Product Manager":    ["C","C","I","C","C","C","C","C","I","I","I","C"],
            "CS Manager":         ["I","I","I","I","I","C","I","R","I","R","I","R"],
        })
        def style_raci(v):
            if v == "R": return f"background-color:#1e3a5f;color:{PRIMARY};font-weight:700"
            if v == "A": return "background-color:#3d2a0a;color:#f59e0b;font-weight:700"
            if v == "C": return "background-color:#0a2e1a;color:#22c55e;font-weight:600"
            if v == "I": return "color:#64748b"
            return ""
        rcols = ["Business Analyst","Engineering Lead","VP Customer Success","Data Engineer","Product Manager","CS Manager"]
        st.dataframe(raci.style.map(style_raci, subset=rcols), use_container_width=True, hide_index=True, height=450)
        st.markdown("""<div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap">
            <span style="font-size:12px"><span style="background:#1e3a5f;color:#4F8EF7;padding:1px 8px;border-radius:3px;font-weight:700">R</span> Does the work</span>
            <span style="font-size:12px"><span style="background:#3d2a0a;color:#f59e0b;padding:1px 8px;border-radius:3px;font-weight:700">A</span> Owns the outcome</span>
            <span style="font-size:12px"><span style="background:#0a2e1a;color:#22c55e;padding:1px 8px;border-radius:3px;font-weight:700">C</span> Provides input</span>
            <span style="font-size:12px;color:#64748b"><b>I</b> Kept informed</span>
        </div>""", unsafe_allow_html=True)

    with art_tab4:
        st.markdown('<div class="section-header">AS-IS vs TO-BE Process Maps</div>', unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("""<div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-top:3px solid #ef4444;border-radius:12px;padding:20px">
                <div style="font-size:14px;font-weight:600;color:#f1f5f9;margin-bottom:4px">AS-IS — Manual Churn Detection</div>
                <div style="font-size:11px;color:#64748b;margin-bottom:14px">Current state: manual, reactive, error-prone</div>
                <div style="font-size:12px;color:#94a3b8;line-height:2.2">
                    📅 Mon 9AM: CSM opens Spreadsheet 1 (Usage)<br>
                    → Opens Spreadsheet 2 (Billing)<br>
                    → Opens Spreadsheet 3 (Support tickets)<br>
                    → ⏱ 2hrs manual cross-reference<br>
                    → Gut-feel risk assessment (no scoring)<br>
                    → Email to CS Director (if concerned)<br>
                    → ⏳ Director reviews in 1-2 days<br>
                    → Manual outreach to customer<br>
                    → Customer may already have decided to leave
                </div>
                <div style="margin-top:14px;padding-top:12px;border-top:1px solid #1e3a5f">
                    <div style="font-size:11px;color:#ef4444;font-weight:700;margin-bottom:6px">PAIN POINTS</div>
                    <div style="font-size:12px;color:#94a3b8">• 4 hrs/week manual labor &nbsp;• No SLA on escalation<br>• Gut feel, no consistent scoring &nbsp;• Reactive — too late</div>
                </div>
            </div>""", unsafe_allow_html=True)
        with col_m2:
            st.markdown("""<div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-top:3px solid #22c55e;border-radius:12px;padding:20px">
                <div style="font-size:14px;font-weight:600;color:#f1f5f9;margin-bottom:4px">TO-BE — BridgeIQ Automated</div>
                <div style="font-size:11px;color:#64748b;margin-bottom:14px">Future state: automated, proactive, data-driven</div>
                <div style="font-size:12px;color:#94a3b8;line-height:2.2">
                    ⚡ 6AM: Automated pipeline triggers<br>
                    → Pulls 5 signals simultaneously (usage/billing/tickets/onboarding/NPS)<br>
                    → Composite risk score computed per customer<br>
                    → Score &lt;30: No action (monitored daily)<br>
                    → Score 30-49: Flagged on CSM dashboard<br>
                    → Score 50-79: 🔔 Slack alert → CSM (≤1hr)<br>
                    → Score ≥80: 🚨 Immediate CSM + Director alert<br>
                    → CSM reviews, selects intervention strategy<br>
                    → Intervention logged with timestamp + owner
                </div>
                <div style="margin-top:14px;padding-top:12px;border-top:1px solid #1e3a5f">
                    <div style="font-size:11px;color:#22c55e;font-weight:700;margin-bottom:6px">IMPROVEMENTS</div>
                    <div style="font-size:12px;color:#94a3b8">• 97% faster detection (7d → &lt;6hrs)<br>• 88% CSM time saved &nbsp;• Consistent auditable scoring &nbsp;• Full audit trail</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        imp_df = pd.DataFrame([
            ["Detection time", "7 days (weekly review)", "< 6 hours (automated)", "97% faster"],
            ["Data sources", "3 manual spreadsheets", "5 integrated signals", "Complete & unified"],
            ["Risk assessment", "Gut feel", "Composite scoring algorithm", "Consistent & auditable"],
            ["Alert mechanism", "Email chain (1-2 day delay)", "Slack + in-app (≤1hr)", "Instant & trackable"],
            ["Intervention logging", "None", "Timestamped in BridgeIQ", "Full audit trail"],
            ["CSM weekly time", "4 hrs manual review", "< 30 min (review alerts)", "88% time saved"],
        ], columns=["Dimension", "AS-IS (Current)", "TO-BE (BridgeIQ)", "Improvement"])
        st.dataframe(imp_df, use_container_width=True, hide_index=True)

    with art_tab5:
        st.markdown('<div class="section-header">Requirements Traceability Matrix</div>', unsafe_allow_html=True)
        st.caption("Maps each user story → business objective → data source → dashboard metric. Demonstrates governance maturity — a 2025 hiring differentiator.")

        trace = pd.DataFrame([
            ["US-01","Reduce churn rate by 15%","customers, product_usage, support_tickets","Health Score gauge · At-Risk table"],
            ["US-02","Reduce churn rate by 15%","customers (risk score delta)","Alert trigger logic (not yet built)"],
            ["US-03","Reduce onboarding failure to <10%","onboarding (stage, blocker)","Onboarding tab · Blocker pie chart"],
            ["US-04","Reduce onboarding failure to <10%","onboarding (completed flag)","Onboarding Completion gauge"],
            ["US-05","Resolve 95% of tickets within SLA","support_tickets (resolution_time_hours)","SLA Breach Rate chart · Resolution Time box"],
            ["US-06","Improve CSAT to >4.5/5","support_tickets (satisfaction_score)","Monthly CSAT trend line"],
            ["US-07","Achieve 360° executive visibility","All 6 tables","Executive Dashboard KPI row"],
            ["US-08","10x requirements velocity","support_tickets (description)","AI Feedback Analyzer → user stories"],
            ["US-09","5x documentation velocity","business problem input","AI Requirements Generator → BRD"],
            ["US-10","Enable segment-level analysis","customers (plan_type, region, industry)","Sidebar global filters → all charts"],
            ["US-11","Enable reliable data pipelines","All tables (schema design)","ERD · Data Dictionary (48 columns)"],
            ["US-14","Quantify MRR at financial risk","customers (mrr, risk score)","About page ROI calculator"],
        ], columns=["Story ID", "Business Objective", "Primary Data Source(s)", "Dashboard / Artifact"])

        def style_trace(v):
            if isinstance(v, str) and v.startswith("US-0"):
                return f"color:{PRIMARY};font-weight:700"
            return ""

        st.dataframe(trace.style.map(style_trace, subset=["Story ID"]),
                     use_container_width=True, hide_index=True, height=450)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-left:4px solid #a78bfa;border-radius:10px;padding:14px;margin-top:12px">
            <div style="font-size:12px;font-weight:600;color:#a78bfa;margin-bottom:6px">Why Traceability Matters</div>
            <div style="font-size:12px;color:#94a3b8">
                Requirement traceability ensures every feature built connects back to a business objective and can be validated against real data.
                It prevents scope creep, supports impact analysis when requirements change, and satisfies governance/compliance requirements.
                Most junior BAs skip this — it signals senior-level thinking.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — WHAT-IF REVENUE SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💡 What-If Simulator":
    st.markdown('<div class="page-title">What-If Revenue Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Move the sliders — see the live dollar impact of fixing Apex Solutions\' three biggest problems</div>', unsafe_allow_html=True)
    st.markdown("---")

    base_sim = query("""
        SELECT ROUND(SUM(CASE WHEN status='Active' THEN mrr ELSE 0 END),0) AS total_mrr,
               ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
               COUNT(*) AS total_cust,
               ROUND(AVG(CASE WHEN status='Active' THEN mrr END),0) AS avg_mrr
        FROM customers
    """).iloc[0]
    onb_sim = query("SELECT ROUND(COUNT(CASE WHEN completed=1 THEN 1 END)*100.0/COUNT(*),1) AS pct, COUNT(CASE WHEN completed=0 THEN 1 END) AS incomplete FROM onboarding").iloc[0]
    supp_sim = query("SELECT ROUND(AVG(resolution_time_hours),1) AS avg_res FROM support_tickets").iloc[0]

    curr_mrr_s = int(base_sim["total_mrr"])
    curr_arr_s = curr_mrr_s * 12
    curr_churn_s = float(base_sim["churn_rate"])
    curr_onb_s = float(onb_sim["pct"])
    curr_res_s = float(supp_sim["avg_res"])
    avg_mrr_s = float(base_sim["avg_mrr"])
    incomplete_s = int(onb_sim["incomplete"])
    total_cust_s = int(base_sim["total_cust"])

    st.markdown('<div class="section-header">Current Baseline — Apex Solutions</div>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    for col, (lbl, val, color) in zip([b1,b2,b3,b4], [
        ("Current ARR", f"${curr_arr_s:,}", PRIMARY),
        ("Annual Churn Rate", f"{curr_churn_s}%", DANGER),
        ("Onboarding Completion", f"{curr_onb_s}%", WARNING),
        ("Avg Resolution Time", f"{curr_res_s}h", WARNING),
    ]):
        col.markdown(f"""<div class="kpi-card" style="border-left-color:{color}">
            <div class="kpi-label">{lbl}</div>
            <div class="kpi-value" style="color:{color}">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Intervention Controls — Drag to model the impact</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f'<div style="font-size:12px;font-weight:600;color:{DANGER};margin-bottom:6px">CHURN RATE TARGET (%)</div>', unsafe_allow_html=True)
        target_churn_s = st.slider("Target Churn Rate", min_value=2.0, max_value=float(curr_churn_s),
                                    value=round(curr_churn_s * 0.6, 1), step=0.5, key="sim_churn",
                                    help="Industry best: <5% annually")
    with s2:
        st.markdown(f'<div style="font-size:12px;font-weight:600;color:{WARNING};margin-bottom:6px">ONBOARDING COMPLETION TARGET (%)</div>', unsafe_allow_html=True)
        target_onb_s = st.slider("Target Onboarding %", min_value=float(curr_onb_s), max_value=100.0,
                                  value=min(curr_onb_s + 12.0, 95.0), step=1.0, key="sim_onb",
                                  help="Industry best: >85%")
    with s3:
        st.markdown(f'<div style="font-size:12px;font-weight:600;color:{WARNING};margin-bottom:6px">AVG RESOLUTION TIME TARGET (hrs)</div>', unsafe_allow_html=True)
        target_res_s = st.slider("Target Resolution (hrs)", min_value=4.0, max_value=float(curr_res_s),
                                  value=max(curr_res_s * 0.5, 8.0), step=1.0, key="sim_res",
                                  help="SLA target: <8h for critical")

    # Calculations
    churn_delta = curr_churn_s - target_churn_s
    arr_from_churn = round(total_cust_s * churn_delta / 100 * avg_mrr_s)

    onb_delta = target_onb_s - curr_onb_s
    newly_done = round(incomplete_s * onb_delta / 100)
    arr_from_onb = round(newly_done * avg_mrr_s * 0.35)

    res_pct_improve = (curr_res_s - target_res_s) / curr_res_s
    arr_from_res = round(curr_arr_s * res_pct_improve * 0.05)
    cs_hrs_saved = round((curr_res_s - target_res_s) * 8)

    total_arr_gain = arr_from_churn + arr_from_onb + arr_from_res
    new_arr_s = curr_arr_s + total_arr_gain
    roi_pct_s = round(total_arr_gain / curr_arr_s * 100, 1)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Live Impact Calculation</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    for col, (lbl, val, sub, color) in zip([i1,i2,i3,i4], [
        ("Churn Fix ARR Recovery", f"${arr_from_churn:,}", f"↓ {churn_delta:.1f}% reduction", SUCCESS),
        ("Onboarding Fix Recovery", f"${arr_from_onb:,}", f"{newly_done} more completions", SUCCESS),
        ("Resolution Time Savings", f"${arr_from_res:,}", f"{cs_hrs_saved}h CS time saved/week", SUCCESS),
        ("TOTAL ARR OPPORTUNITY", f"${total_arr_gain:,}", f"+{roi_pct_s}% revenue growth", PRIMARY),
    ]):
        col.markdown(f"""<div class="kpi-card" style="border-left-color:{color}">
            <div class="kpi-label">{lbl}</div>
            <div class="kpi-value" style="color:{color}">{val}</div>
            <div class="kpi-delta-good">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c_wf, c_roi = st.columns([2, 1])

    with c_wf:
        st.markdown('<div class="section-header">ARR Waterfall — Before vs After BridgeIQ</div>', unsafe_allow_html=True)
        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=["Current ARR", "Churn Fix", "Onboarding Fix", "Resolution Fix", "New ARR"],
            y=[curr_arr_s, arr_from_churn, arr_from_onb, arr_from_res, new_arr_s],
            connector={"line": {"color": "#1e3a5f"}},
            decreasing={"marker": {"color": DANGER}},
            increasing={"marker": {"color": SUCCESS}},
            totals={"marker": {"color": PRIMARY}},
            text=[f"${v:,.0f}" for v in [curr_arr_s, arr_from_churn, arr_from_onb, arr_from_res, new_arr_s]],
            textposition="outside",
        ))
        chart_layout(fig_wf, 380)
        st.plotly_chart(fig_wf, use_container_width=True)

    with c_roi:
        st.markdown('<div class="section-header">ROI Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#051525,#0d1b2a);border:1px solid #1e3a5f;border-left:4px solid {PRIMARY};border-radius:12px;padding:20px">
            <div style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #1e3a5f">
                <div style="font-size:11px;color:#64748b">Current ARR</div>
                <div style="font-size:22px;font-weight:700;color:{DANGER}">${curr_arr_s:,}</div>
            </div>
            <div style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #1e3a5f">
                <div style="font-size:11px;color:#64748b">Projected ARR (with fixes)</div>
                <div style="font-size:22px;font-weight:700;color:{SUCCESS}">${new_arr_s:,}</div>
            </div>
            <div style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #1e3a5f">
                <div style="font-size:11px;color:#64748b">Net ARR Gain</div>
                <div style="font-size:28px;font-weight:800;color:{PRIMARY}">+${total_arr_gain:,}</div>
                <div style="font-size:12px;color:{SUCCESS};margin-top:2px">+{roi_pct_s}% revenue growth</div>
            </div>
            <div>
                <div style="font-size:11px;color:#64748b">CS Hours Saved / Week</div>
                <div style="font-size:18px;font-weight:700;color:#f59e0b">{cs_hrs_saved}h</div>
                <div style="font-size:11px;color:#64748b">= {cs_hrs_saved*52:,} hrs/year</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="alert-warning">
            <div style="font-size:11px;font-weight:700;color:#f59e0b;margin-bottom:6px">BA INSIGHT</div>
            <div style="font-size:12px;color:#94a3b8">Fixing churn from <b>{curr_churn_s}% → {target_churn_s}%</b> alone recovers <b style="color:{SUCCESS}">${arr_from_churn:,} ARR</b>. Combined interventions unlock <b style="color:{PRIMARY}">${total_arr_gain:,}</b> — justifying significant CS tooling investment.</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — ABOUT THE ANALYST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 About the Analyst":
    st.markdown('<div class="page-title">About the Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">The person behind BridgeIQ — bridging computer science and business strategy</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Stats at a glance strip
    st.markdown("""
    <div class="hero-strip">
        <div style="display:flex;align-items:center;gap:8px;padding-right:24px;border-right:1px solid #1e3a5f;white-space:nowrap">
            <span style="font-size:10px;font-weight:800;color:#4F8EF7;letter-spacing:2px">BRIDGEIQ BY THE NUMBERS</span>
        </div>
        <div class="hero-stat"><div class="hero-stat-label">Data Rows</div><div class="hero-stat-value">16K+</div></div>
        <div class="hero-stat"><div class="hero-stat-label">SQL Tables</div><div class="hero-stat-value">6</div></div>
        <div class="hero-stat"><div class="hero-stat-label">SQL Queries</div><div class="hero-stat-value">10</div></div>
        <div class="hero-stat"><div class="hero-stat-label">AI Features</div><div class="hero-stat-value">6</div></div>
        <div class="hero-stat"><div class="hero-stat-label">User Stories</div><div class="hero-stat-value">15</div></div>
        <div class="hero-stat"><div class="hero-stat-label">BA Deliverables</div><div class="hero-stat-value">14</div></div>
        <div class="hero-stat"><div class="hero-stat-label">App Pages</div><div class="hero-stat-value">9</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:28px;margin-bottom:16px">
            <div style="font-size:24px;font-weight:700;color:#f1f5f9;margin-bottom:4px">Sai Hemanth</div>
            <div style="font-size:13px;color:#4F8EF7;margin-bottom:16px">Technical Business Analyst · AI/ML Researcher · IEEE-Published Author</div>
            <div style="font-size:14px;color:#94a3b8;line-height:1.8">
                I hold a Bachelor's and Master's degree in Computer Science — which means I've spent years
                thinking like an engineer. But what I discovered is that the hardest problems in tech aren't
                technical. They're translational. Getting a data engineer and a VP of Sales to agree on what
                "customer health" means. Getting a product team to build the right thing instead of the easy thing.
                Turning messy data into a decision a CFO will act on.
                <br><br>
                That's what I do. And BridgeIQ is how I prove it.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:28px;margin-bottom:16px">
            <div style="font-size:16px;font-weight:600;color:#f1f5f9;margin-bottom:16px">Why I Built BridgeIQ</div>
            <div style="font-size:14px;color:#94a3b8;line-height:1.8">
                Most BA portfolios are PDFs. A BRD written in isolation, user stories no one will implement,
                process maps that live in a Confluence page nobody reads.
                <br><br>
                I wanted to build something a recruiter could <em>click</em>. Something that shows — not tells —
                that I can take a business problem, go deep on the data, design a solution, spec it in Agile,
                and deliver a live working product. All of it. Not just one piece.
                <br><br>
                BridgeIQ is that proof. It's a fake company with real problems. And I solved them end-to-end.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:24px;margin-bottom:16px">
            <div style="font-size:13px;font-weight:600;color:#64748b;letter-spacing:1px;text-transform:uppercase;margin-bottom:16px">Education</div>
            <div style="margin-bottom:12px">
                <div style="font-size:13px;font-weight:600;color:#f1f5f9">M.S. Computer Science</div>
                <div style="font-size:12px;color:#64748b">Graduate · AI/ML Specialization</div>
            </div>
            <div>
                <div style="font-size:13px;font-weight:600;color:#f1f5f9">B.S. Computer Science</div>
                <div style="font-size:12px;color:#64748b">Undergraduate</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:24px;margin-bottom:16px">
            <div style="font-size:13px;font-weight:600;color:#64748b;letter-spacing:1px;text-transform:uppercase;margin-bottom:16px">Research</div>
            <div style="font-size:13px;color:#f1f5f9;margin-bottom:4px">IEEE-Published Researcher</div>
            <div style="font-size:12px;color:#64748b">AI/ML · Computer Vision · Data Science</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:24px">
            <div style="font-size:13px;font-weight:600;color:#64748b;letter-spacing:1px;text-transform:uppercase;margin-bottom:16px">Contact</div>
            <div style="font-size:13px;color:#4F8EF7;margin-bottom:8px">gtrhemanth14@gmail.com</div>
            <div style="font-size:13px;color:#4F8EF7">github.com/gtrhemanth</div>
        </div>
        """, unsafe_allow_html=True)

    # Skills grid
    st.markdown("---")
    st.markdown('<div class="section-header">What BridgeIQ Demonstrates</div>', unsafe_allow_html=True)

    skills = {
        "Business Analysis": ["Business Requirements Document (BRD)", "Agile User Stories + Acceptance Criteria",
                               "AS-IS / TO-BE Process Mapping", "Stakeholder Analysis + RACI Matrix",
                               "Risk Register", "UAT Test Framework", "Data Dictionary (48 columns)"],
        "Technical Skills": ["6-table relational data model (ERD)", "10 SQL queries — CTEs, window functions, cohort analysis",
                              "Python 3.11 — data generation, API integration", "Streamlit multi-page web application",
                              "Plotly — interactive charts, gauges, treemaps", "Git / GitHub version control"],
        "AI Integration": ["Anthropic Claude API (Sonnet + Haiku)", "Structured prompt engineering",
                            "AI Feedback Analyzer — feedback → user stories", "AI Requirements Generator — problem → BRD",
                            "AI Insights Engine — data → executive brief", "Interview Simulator — JD → tailored prep"],
    }

    cols = st.columns(3)
    skill_colors = [PRIMARY, "#22c55e", "#a78bfa"]
    for col, (category, items), color in zip(cols, skills.items(), skill_colors):
        items_html = "".join([f'<div style="padding:6px 0;border-bottom:1px solid #1e3a5f;font-size:13px;color:#94a3b8">→ {item}</div>' for item in items])
        col.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-top:3px solid {color};border-radius:12px;padding:20px">
            <div style="font-size:14px;font-weight:700;color:#f1f5f9;margin-bottom:12px">{category}</div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    # ROI section
    st.markdown("---")
    st.markdown('<div class="section-header">Business Impact — If BridgeIQ Were Real</div>', unsafe_allow_html=True)

    impact_data = query("""
        SELECT
            ROUND(SUM(CASE WHEN status='Active' THEN mrr ELSE 0 END),0) AS mrr,
            COUNT(CASE WHEN status='Churned' THEN 1 END) AS churned,
            ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate
        FROM customers
    """).iloc[0]

    mrr = int(impact_data["mrr"])
    churn = float(impact_data["churn_rate"])
    arr = mrr * 12
    mrr_at_risk = round(mrr * churn / 100)
    potential_save = round(mrr_at_risk * 0.35)

    impact_cards = [
        ("Current ARR", f"${arr:,}", "Active customer base"),
        ("MRR at Churn Risk", f"${mrr_at_risk:,}/mo", f"{churn}% churn rate"),
        ("Recoverable with BridgeIQ", f"${potential_save:,}/mo", "35% early intervention success rate"),
        ("Annual ROI", f"${potential_save*12:,}", "If deployed for 12 months"),
    ]

    cols = st.columns(4)
    for col, (label, value, sub) in zip(cols, impact_cards):
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta-neutral">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # Project timeline
    st.markdown("---")
    st.markdown('<div class="section-header">How BridgeIQ Was Built — Project Timeline</div>', unsafe_allow_html=True)
    tl_items = [
        ("Week 1", "Discovery & Data Engineering", "Designed 6-table relational schema, defined 48-column data dictionary, generated 16,000+ rows of synthetic data with realistic business patterns using Faker + NumPy.", "#4F8EF7"),
        ("Week 2", "SQL Analytics Layer", "Wrote 10 SQL query files covering churn analysis, revenue trends, cohort retention, SLA compliance, and composite risk scoring — using CTEs, window functions, and multi-table joins.", "#22c55e"),
        ("Week 3", "Streamlit Application", "Built 9-page interactive Streamlit app with Plotly dashboards, dark theme, custom CSS animations, responsive layout, and global filter system.", "#a78bfa"),
        ("Week 4", "Claude AI Integration", "Integrated Anthropic Claude API for 6 AI features: feedback analyzer, requirements generator, insights engine, interview simulator, account intelligence, and anomaly root cause analysis.", "#f59e0b"),
        ("Week 5", "BA Deliverables Suite", "Produced BRD (11 sections), 15 Agile user stories with AC, AS-IS/TO-BE process maps, risk register, RACI matrix, requirements traceability matrix, and 10-slide executive deck.", "#ef4444"),
        ("Shipped", "Live on Streamlit Cloud", "Deployed publicly. 16K+ rows of data, 6 AI features, 9 interactive pages — all running live. GitHub repository published and documented.", "#22c55e"),
    ]
    tl_rows = ""
    for week, title, desc, color in tl_items:
        tl_rows += f"""
        <div style="display:flex;gap:16px;margin-bottom:12px;align-items:flex-start">
            <div style="min-width:72px;text-align:right;padding-top:2px">
                <span style="background:{color};color:#000;font-size:10px;font-weight:800;padding:3px 8px;border-radius:20px;white-space:nowrap">{week}</span>
            </div>
            <div style="width:2px;background:linear-gradient(180deg,{color},transparent);min-height:48px;flex-shrink:0;border-radius:2px;margin-top:6px"></div>
            <div style="flex:1;padding-bottom:12px;border-bottom:1px solid #1e3a5f">
                <div style="font-size:13px;font-weight:600;color:#f1f5f9;margin-bottom:3px">{title}</div>
                <div style="font-size:12px;color:#64748b;line-height:1.6">{desc}</div>
            </div>
        </div>"""
    st.markdown(f'<div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:24px 28px">{tl_rows}</div>', unsafe_allow_html=True)

    # Strong CTA section
    st.markdown("---")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#051525,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:16px;
         padding:48px 40px;text-align:center;position:relative;overflow:hidden;animation:border-glow 4s ease-in-out infinite">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#4F8EF7,#22c55e,#4F8EF7,transparent)"></div>
        <div style="font-size:32px;font-weight:800;color:#f1f5f9;margin-bottom:8px;letter-spacing:-0.5px;
             background:linear-gradient(270deg,#4F8EF7,#7bb3ff,#a5f3fc,#4F8EF7);background-size:300% 300%;
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradient-x 5s ease infinite">
            Ready to bring this to your team?
        </div>
        <div style="font-size:14px;color:#64748b;max-width:520px;margin:0 auto 28px;line-height:1.8">
            BridgeIQ shows what a Technical BA delivers when given real problems and the right tools —
            end-to-end, from stakeholder interviews to a live AI-powered product. Let's talk.
        </div>
        <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-bottom:20px">
            <a href="mailto:gtrhemanth14@gmail.com"
               style="background:linear-gradient(135deg,#4F8EF7,#3b82f6);color:#fff;text-decoration:none;
                      padding:14px 32px;border-radius:10px;font-weight:700;font-size:14px;display:inline-flex;align-items:center;gap:8px;
                      box-shadow:0 4px 15px rgba(79,142,247,0.3)">
                ✉ Email Me
            </a>
            <a href="https://github.com/gtrhemanth/BridgeIQ"
               style="background:transparent;color:#4F8EF7;text-decoration:none;
                      padding:14px 32px;border-radius:10px;font-weight:700;font-size:14px;border:1px solid #4F8EF7;display:inline-flex;align-items:center;gap:8px">
                ⭐ View on GitHub
            </a>
        </div>
        <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap">
            <span class="badge badge-blue">Open to BA roles</span>
            <span class="badge badge-green">Available for interviews</span>
            <span class="badge badge-purple">IEEE-Published Researcher</span>
            <span class="badge badge-yellow">3–4yr BA experience level</span>
        </div>
        <div style="font-size:11px;color:#374151;margin-top:20px">gtrhemanth14@gmail.com · github.com/gtrhemanth</div>
    </div>
    """, unsafe_allow_html=True)
