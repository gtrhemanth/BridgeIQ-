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
import streamlit.components.v1 as components
components.html("""
<script>
setTimeout(function() {
    var btn = window.parent.document.querySelector('[data-testid="stSidebarCollapsedControl"] button');
    if (!btn) btn = window.parent.document.querySelector('[data-testid="collapsedControl"] button');
    if (btn) btn.click();
}, 300);
</script>
""", height=0)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide Streamlit chrome — header stays visible so sidebar toggle always works */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { background: #0f1117 !important; }
header * { color: #0f1117 !important; }
[data-testid="stToolbar"] { opacity: 0 !important; pointer-events: none; }

/* Hide the collapse arrow inside sidebar — sidebar stays permanently open */
[data-testid="stSidebar"] button[data-testid="stBaseButton-header"],
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
[data-testid="stSidebarNavCloseButton"],
[data-testid="stSidebar"] button[kind="header"] {
    display: none !important;
}

/* Main background */
.stApp { background-color: #0f1117; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1a2d40 100%);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a2d40 100%);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #4F8EF7;
    border-radius: 12px;
    padding: 20px 24px;
    margin: 4px 0;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(79, 142, 247, 0.15);
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #64748b !important;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #f1f5f9 !important;
    line-height: 1;
}
.kpi-delta-good { font-size: 12px; color: #22c55e !important; margin-top: 6px; font-weight: 500; }
.kpi-delta-bad  { font-size: 12px; color: #ef4444 !important; margin-top: 6px; font-weight: 500; }
.kpi-delta-neutral { font-size: 12px; color: #94a3b8 !important; margin-top: 6px; font-weight: 500; }

/* Section headers */
.section-header {
    font-size: 18px;
    font-weight: 600;
    color: #f1f5f9;
    margin: 24px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e3a5f;
}

/* Page title */
.page-title {
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(135deg, #4F8EF7, #7bb3ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.page-subtitle { font-size: 13px; color: #64748b; margin-bottom: 24px; }

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

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-title">BridgeIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-subtitle">AI-POWERED BUSINESS INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    page = st.radio("", [
        "📊 Executive Dashboard",
        "🧠 AI Insights Engine",
        "🤖 AI Feedback Analyzer",
        "📋 AI Requirements Generator",
        "🎯 Interview Simulator",
        "🔍 Customer 360",
        "📐 BA Artifacts",
        "👤 About the Analyst",
    ], label_visibility="collapsed")

    if page == "📊 Executive Dashboard":
        st.markdown("---")
        st.markdown('<div class="filter-label">Global Filters</div>', unsafe_allow_html=True)

        all_plans      = ["All", "Starter", "Growth", "Enterprise"]
        all_regions    = ["All", "North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
        all_industries = ["All", "Healthcare", "Finance", "Retail", "Manufacturing", "Education",
                          "Logistics", "Real Estate", "Legal", "Technology", "Consulting"]

        sel_plans  = st.multiselect("Plan Type", all_plans, default=["All"], key="plan")
        sel_region = st.multiselect("Region",    all_regions, default=["All"], key="region")
        sel_ind    = st.multiselect("Industry",  all_industries, default=["All"], key="ind")
        st.markdown("---")

    st.markdown("**Apex Solutions**")
    st.markdown("B2B SaaS · 500 Customers · Fictional Demo")
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

    # ── KPI Row ───────────────────────────────────────────────────────────────
    cols = st.columns(6)
    kpi_data = [
        ("ACTIVE CUSTOMERS", f"{int(kpi['active_customers']):,}", "▲ vs last quarter", "good"),
        ("TOTAL MRR",        f"${int(kpi['total_mrr']):,}", "Monthly Recurring Revenue", "neutral"),
        ("TOTAL ARR",        f"${int(kpi['total_mrr'])*12:,}", "Annualized Run Rate", "neutral"),
        ("CHURN RATE",       f"{kpi['churn_rate']}%", "▼ 2.1% from last quarter", "bad"),
        ("AVG HEALTH SCORE", f"{kpi['avg_health']}/100", f"NPS: {kpi['avg_nps']}", "good"),
        ("ONBOARDING",       f"{onb_pct}%", f"{open_tickets:,} open tickets", "neutral"),
    ]
    for col, (label, value, delta, dtype) in zip(cols, kpi_data):
        delta_class = f"kpi-delta-{dtype}"
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_class}">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📈 Overview", "💰 Revenue", "👥 Customer Health", "🎫 Support", "🚀 Onboarding", "📊 Cohort Retention", "🏆 SaaS Benchmarks"])

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
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:32px;text-align:center;margin-top:20px">
            <div style="font-size:48px;margin-bottom:16px">🧠</div>
            <div style="font-size:18px;font-weight:600;color:#f1f5f9;margin-bottom:8px">AI reads your data. You present the insight.</div>
            <div style="font-size:13px;color:#64748b;max-width:500px;margin:0 auto">
                Select a focus area, choose your audience, and Claude will analyze the live database —
                customer health, churn signals, support performance, onboarding gaps —
                and produce an executive brief you can present in any interview or boardroom.
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
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a2d40);border:1px solid #1e3a5f;border-radius:12px;padding:32px;text-align:center;margin-top:20px">
            <div style="font-size:48px;margin-bottom:16px">🎯</div>
            <div style="font-size:18px;font-weight:600;color:#f1f5f9;margin-bottom:8px">Walk into every interview prepared.</div>
            <div style="font-size:13px;color:#64748b;max-width:520px;margin:0 auto">
                Paste any BA job description. Claude analyzes the requirements, matches them to your BridgeIQ project,
                and generates tailored talking points, model answers, and a 60-second pitch — specific to that company and role.
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
# PAGE 8 — ABOUT THE ANALYST
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 About the Analyst":
    st.markdown('<div class="page-title">About the Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">The person behind BridgeIQ — bridging computer science and business strategy</div>', unsafe_allow_html=True)
    st.markdown("---")

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
