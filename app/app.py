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

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

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

    page = st.radio("", ["📊 Executive Dashboard", "🤖 AI Feedback Analyzer", "📋 AI Requirements Generator"],
                    label_visibility="collapsed")

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "💰 Revenue", "👥 Customer Health", "🎫 Support", "🚀 Onboarding"])

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
