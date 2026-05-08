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

# ── Config ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BridgeIQ",
    page_icon="assets/logo.png" if os.path.exists("assets/logo.png") else "📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bridgeiq.db")
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── DB Helper ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## BridgeIQ")
    st.markdown("*AI-Powered Business Intelligence*")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Executive Dashboard", "AI Feedback Analyzer", "AI Requirements Generator"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Apex Solutions**")
    st.markdown("B2B SaaS | 500 Customers")
    st.markdown("*Fictional company — demo data*")
    st.markdown("---")
    st.caption("Built by Sai Hemanth | Technical BA Portfolio")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Executive Dashboard":
    st.title("Executive Dashboard")
    st.markdown("**Apex Solutions** · Real-time business health metrics · Apex Solutions B2B SaaS Platform")
    st.markdown("---")

    # ── KPI Row ───────────────────────────────────────────────────────────────
    kpi = query("""
        SELECT
            (SELECT COUNT(*) FROM customers WHERE status='Active') AS active_customers,
            (SELECT ROUND(SUM(mrr),2) FROM customers WHERE status='Active') AS total_mrr,
            (SELECT ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),2) FROM customers) AS churn_rate,
            (SELECT ROUND(AVG(health_score),1) FROM customers WHERE status='Active') AS avg_health,
            (SELECT COUNT(*) FROM support_tickets WHERE status IN ('Open','In Progress')) AS open_tickets,
            (SELECT ROUND(COUNT(CASE WHEN completed=1 THEN 1 END)*100.0/COUNT(*),2) FROM onboarding) AS onboarding_pct
    """).iloc[0]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Active Customers", f"{int(kpi['active_customers']):,}")
    c2.metric("Total MRR", f"${kpi['total_mrr']:,.0f}")
    c3.metric("Churn Rate", f"{kpi['churn_rate']}%", delta="-2.1%", delta_color="normal")
    c4.metric("Avg Health Score", f"{kpi['avg_health']}/100")
    c5.metric("Open Tickets", f"{int(kpi['open_tickets']):,}", delta="+12", delta_color="inverse")
    c6.metric("Onboarding Complete", f"{kpi['onboarding_pct']}%")

    st.markdown("---")

    # ── Row 1: Revenue Trend + Churn by Plan ──────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Monthly Net Revenue")
        rev = query("""
            SELECT strftime('%Y-%m', transaction_date) AS month,
                   ROUND(SUM(amount),2) AS net_revenue
            FROM transactions WHERE status='Completed'
            GROUP BY month ORDER BY month
        """)
        fig = px.area(rev, x="month", y="net_revenue",
                      color_discrete_sequence=["#4F8EF7"],
                      labels={"month": "Month", "net_revenue": "Net Revenue ($)"})
        fig.update_layout(margin=dict(t=10, b=10), height=280, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Churn Rate by Plan")
        churn_plan = query("""
            SELECT plan_type,
                   COUNT(*) AS total,
                   COUNT(CASE WHEN status='Churned' THEN 1 END) AS churned,
                   ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate
            FROM customers GROUP BY plan_type
        """)
        fig2 = px.bar(churn_plan, x="plan_type", y="churn_rate",
                      color="plan_type",
                      color_discrete_sequence=["#4F8EF7", "#F7844F", "#4FF7A0"],
                      labels={"plan_type": "Plan", "churn_rate": "Churn Rate (%)"},
                      text="churn_rate")
        fig2.update_traces(texttemplate="%{text}%", textposition="outside")
        fig2.update_layout(margin=dict(t=10, b=10), height=280, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Support Tickets + Feature Usage ────────────────────────────────
    col3, col4 = st.columns([2, 3])

    with col3:
        st.subheader("Tickets by Category")
        tix = query("""
            SELECT category, COUNT(*) AS tickets,
                   ROUND(AVG(resolution_time_hours),1) AS avg_resolution_hrs
            FROM support_tickets GROUP BY category ORDER BY tickets DESC
        """)
        fig3 = px.bar(tix, x="tickets", y="category", orientation="h",
                      color="avg_resolution_hrs",
                      color_continuous_scale="RdYlGn_r",
                      labels={"tickets": "Ticket Count", "category": "",
                              "avg_resolution_hrs": "Avg Hrs"},
                      text="tickets")
        fig3.update_traces(textposition="outside")
        fig3.update_layout(margin=dict(t=10, b=10), height=300, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Feature Adoption")
        usage = query("""
            SELECT feature, COUNT(DISTINCT customer_id) AS unique_users,
                   ROUND(AVG(session_minutes),1) AS avg_mins
            FROM product_usage GROUP BY feature ORDER BY unique_users DESC
        """)
        fig4 = px.scatter(usage, x="unique_users", y="avg_mins", text="feature",
                          size="unique_users",
                          color="avg_mins",
                          color_continuous_scale="Blues",
                          labels={"unique_users": "Unique Users", "avg_mins": "Avg Session (min)"})
        fig4.update_traces(textposition="top center")
        fig4.update_layout(margin=dict(t=10, b=10), height=300)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: At-Risk Customers Table ────────────────────────────────────────
    st.subheader("At-Risk Active Customers (Top 10)")
    st.caption("Composite risk score based on health score, ticket volume, usage, and onboarding status")
    at_risk = query("""
        WITH t AS (
            SELECT customer_id, COUNT(*) AS tickets,
                   COUNT(CASE WHEN priority IN ('High','Critical') THEN 1 END) AS hi_tix
            FROM support_tickets GROUP BY customer_id
        ),
        u AS (
            SELECT customer_id, COUNT(*) AS sessions
            FROM product_usage GROUP BY customer_id
        ),
        o AS (SELECT customer_id, completed FROM onboarding)
        SELECT c.company_name, c.plan_type, c.mrr,
               ROUND(c.health_score,0) AS health_score,
               COALESCE(t.tickets,0) AS tickets,
               COALESCE(u.sessions,0) AS sessions,
               CASE WHEN o.completed=1 THEN 'Yes' ELSE 'No' END AS onboarding_done,
               ROUND(
                   (CASE WHEN c.health_score<60 THEN 30 WHEN c.health_score<75 THEN 15 ELSE 0 END)
                   +(CASE WHEN COALESCE(t.tickets,0)>15 THEN 20 WHEN COALESCE(t.tickets,0)>8 THEN 10 ELSE 0 END)
                   +(CASE WHEN COALESCE(u.sessions,0)<3 THEN 25 WHEN COALESCE(u.sessions,0)<8 THEN 12 ELSE 0 END)
                   +(CASE WHEN COALESCE(o.completed,0)=0 THEN 15 ELSE 0 END)
                   +(CASE WHEN c.nps_score<5 THEN 10 ELSE 0 END)
               ,0) AS risk_score
        FROM customers c
        LEFT JOIN t ON c.customer_id=t.customer_id
        LEFT JOIN u ON c.customer_id=u.customer_id
        LEFT JOIN o ON c.customer_id=o.customer_id
        WHERE c.status='Active'
        ORDER BY risk_score DESC LIMIT 10
    """)

    def color_risk(val):
        if val >= 50:
            return "background-color: #FFCCCC; color: #CC0000; font-weight: bold"
        elif val >= 30:
            return "background-color: #FFF3CC; color: #996600"
        return "background-color: #CCFFCC; color: #006600"

    styled = at_risk.style.applymap(color_risk, subset=["risk_score"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Row 4: Churn by Industry + Health Distribution ─────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Churn Rate by Industry")
        ind_churn = query("""
            SELECT industry,
                   ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END)*100.0/COUNT(*),1) AS churn_rate,
                   COUNT(*) AS customers
            FROM customers GROUP BY industry ORDER BY churn_rate DESC
        """)
        fig5 = px.bar(ind_churn, x="churn_rate", y="industry", orientation="h",
                      color="churn_rate", color_continuous_scale="RdYlGn_r",
                      text="churn_rate",
                      labels={"churn_rate": "Churn Rate (%)", "industry": ""})
        fig5.update_traces(texttemplate="%{text}%", textposition="outside")
        fig5.update_layout(margin=dict(t=10, b=10), height=350, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.subheader("Health Score Distribution")
        health = query("SELECT status, health_score FROM customers")
        fig6 = px.histogram(health, x="health_score", color="status", nbins=20,
                            barmode="overlay", opacity=0.75,
                            color_discrete_map={"Active": "#4F8EF7", "Churned": "#F7504F"},
                            labels={"health_score": "Health Score", "count": "Customers"})
        fig6.update_layout(margin=dict(t=10, b=10), height=350)
        st.plotly_chart(fig6, use_container_width=True)

    # ── Onboarding bottleneck ─────────────────────────────────────────────────
    st.subheader("Onboarding Bottlenecks")
    blockers = query("""
        SELECT blocker, COUNT(*) AS count
        FROM onboarding WHERE completed=0 AND blocker != 'None'
        GROUP BY blocker ORDER BY count DESC
    """)
    fig7 = px.pie(blockers, values="count", names="blocker",
                  hole=0.45,
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig7.update_layout(margin=dict(t=20, b=10), height=300)
    st.plotly_chart(fig7, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — AI FEEDBACK ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "AI Feedback Analyzer":
    st.title("AI Feedback Analyzer")
    st.markdown(
        "Paste raw customer feedback, support ticket logs, or survey responses. "
        "Claude AI will analyze it and generate BA-ready insights and user stories."
    )
    st.markdown("---")

    col_a, col_b = st.columns([2, 1])

    with col_a:
        feedback_input = st.text_area(
            "Paste customer feedback / support tickets here",
            height=280,
            placeholder=(
                "Example:\n"
                "- 'The dashboard takes forever to load when I have more than 3 filters on.'\n"
                "- 'We got charged twice in March. Still waiting for the refund.'\n"
                "- 'Our Salesforce sync broke after the last update. Support took 3 days to respond.'\n"
                "- 'Love the reporting feature but really need a Slack integration.'\n"
                "- 'Onboarding was confusing. No one told us about the data migration step.'"
            ),
        )

    with col_b:
        st.markdown("#### What you'll get")
        st.markdown("""
        - Sentiment breakdown
        - Top pain points ranked by business impact
        - Root cause categories
        - Auto-generated user stories
        - Recommended process changes
        - BA action items
        """)
        analyze_btn = st.button("Analyze with Claude AI", type="primary", use_container_width=True)

    if analyze_btn:
        if not feedback_input.strip():
            st.warning("Please paste some feedback first.")
        elif not API_KEY:
            st.error("ANTHROPIC_API_KEY not set. Add it to your .env file.")
        else:
            with st.spinner("Claude is analyzing your feedback..."):
                client = anthropic.Anthropic(api_key=API_KEY)
                prompt = f"""You are a Senior Technical Business Analyst analyzing customer feedback for Apex Solutions, a B2B SaaS company selling project management software.

Analyze the following customer feedback and produce a structured BA analysis report.

CUSTOMER FEEDBACK:
{feedback_input}

Produce your analysis in this exact structure:

## SENTIMENT SUMMARY
One paragraph summarizing overall sentiment (positive/neutral/negative split with %).

## TOP PAIN POINTS (ranked by business impact)
List each pain point with:
- Issue: [clear description]
- Impact: [High/Medium/Low]
- Affected Area: [Product/Support/Billing/Onboarding/Integration]
- Frequency Signal: [how many customers seem affected]

## ROOT CAUSE CATEGORIES
Group pain points into root cause categories (e.g., Performance, Process Gap, Communication Failure, Product Gap).

## AUTO-GENERATED USER STORIES
Write 4-6 Agile user stories in format:
As a [user type], I want [feature/improvement], so that [business outcome].
Include Acceptance Criteria (2-3 bullet points each).

## RECOMMENDED PROCESS CHANGES
List 3-5 specific, actionable changes to business processes or workflows.

## BA ACTION ITEMS
List 4-6 next steps a BA should take (e.g., "Schedule stakeholder interview with CS team", "Map current onboarding flow").

Keep the language precise and professional. Focus on business value, not just technical fixes."""

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

                    st.download_button(
                        label="Download Report as .txt",
                        data=result,
                        file_name="feedback_analysis_report.txt",
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"API Error: {e}")

    # ── Sample feedback loader ─────────────────────────────────────────────────
    with st.expander("Load sample feedback from the database"):
        sample = query("""
            SELECT t.description, t.category, t.priority, c.company_name, c.plan_type
            FROM support_tickets t
            JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.priority IN ('High','Critical')
            ORDER BY RANDOM() LIMIT 10
        """)
        st.dataframe(sample, use_container_width=True, hide_index=True)
        if st.button("Use these tickets as input"):
            tickets_text = "\n".join(
                [f"[{r['priority']} | {r['category']}] {r['description']}" for _, r in sample.iterrows()]
            )
            st.session_state["prefill"] = tickets_text
            st.info("Copy the text above and paste it into the feedback box.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI REQUIREMENTS GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "AI Requirements Generator":
    st.title("AI Requirements Generator")
    st.markdown(
        "Describe a business problem or a feature request in plain English. "
        "Claude AI will generate a complete requirements package — BRD excerpt, user stories, acceptance criteria, and UAT cases."
    )
    st.markdown("---")

    col_x, col_y = st.columns([3, 2])

    with col_x:
        problem_statement = st.text_area(
            "Business Problem / Feature Request",
            height=160,
            placeholder=(
                "Example: Our customer success team manually checks each customer's health score "
                "every week by pulling data from three separate spreadsheets. This takes 4 hours per week "
                "and errors are common. We need an automated early warning system that flags at-risk customers "
                "and sends alerts to the CS team in Slack."
            ),
        )

    with col_y:
        st.markdown("#### Configuration")
        stakeholder = st.selectbox(
            "Primary Stakeholder",
            ["Customer Success Manager", "Product Manager", "Sales Manager",
             "CTO / Engineering Lead", "CFO / Finance", "Operations Manager"],
        )
        priority_level = st.selectbox("Priority", ["High", "Medium", "Low"])
        output_type = st.multiselect(
            "What to generate",
            ["BRD Excerpt", "User Stories", "Acceptance Criteria", "UAT Test Cases", "Risk Register"],
            default=["BRD Excerpt", "User Stories", "Acceptance Criteria", "UAT Test Cases"],
        )

    generate_btn = st.button("Generate Requirements with Claude AI", type="primary")

    if generate_btn:
        if not problem_statement.strip():
            st.warning("Please describe the business problem first.")
        elif not output_type:
            st.warning("Select at least one output type.")
        elif not API_KEY:
            st.error("ANTHROPIC_API_KEY not set. Add it to your .env file.")
        else:
            with st.spinner("Claude is generating your requirements package..."):
                client = anthropic.Anthropic(api_key=API_KEY)

                outputs_requested = ", ".join(output_type)
                prompt = f"""You are a Senior Technical Business Analyst at Apex Solutions, a B2B SaaS company.

A stakeholder has raised the following business problem / feature request:

PROBLEM STATEMENT:
{problem_statement}

PRIMARY STAKEHOLDER: {stakeholder}
PRIORITY: {priority_level}

Generate the following BA deliverables: {outputs_requested}

Format your response with clear headers for each deliverable.

{"## BRD EXCERPT" if "BRD Excerpt" in output_type else ""}
{"Write a professional BRD excerpt including: Problem Statement, Business Objectives (3-4), Scope (In-Scope / Out-of-Scope), Assumptions, Constraints, and Success Metrics (KPIs)." if "BRD Excerpt" in output_type else ""}

{"## USER STORIES" if "User Stories" in output_type else ""}
{"Write 5-7 Agile user stories. Format: As a [persona], I want [feature], so that [benefit]. Include story points (1/2/3/5/8) and priority (Must Have / Should Have / Could Have)." if "User Stories" in output_type else ""}

{"## ACCEPTANCE CRITERIA" if "Acceptance Criteria" in output_type else ""}
{"For each user story above, write 2-4 Given/When/Then acceptance criteria." if "Acceptance Criteria" in output_type else ""}

{"## UAT TEST CASES" if "UAT Test Cases" in output_type else ""}
{"Write 5-6 UAT test cases. Format: Test ID | Test Scenario | Steps | Expected Result | Pass/Fail criteria." if "UAT Test Cases" in output_type else ""}

{"## RISK REGISTER" if "Risk Register" in output_type else ""}
{"Identify 4-5 project risks. Format: Risk | Probability (H/M/L) | Impact (H/M/L) | Mitigation Strategy." if "Risk Register" in output_type else ""}

Be specific, professional, and grounded in real BA practice. Avoid generic filler."""

                try:
                    message = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=3000,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    result = message.content[0].text
                    st.markdown("---")
                    st.markdown("### Generated Requirements Package")
                    st.markdown(result)

                    st.download_button(
                        label="Download Requirements Package as .txt",
                        data=result,
                        file_name="requirements_package.txt",
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"API Error: {e}")

    # ── Quick examples ─────────────────────────────────────────────────────────
    with st.expander("Quick-load example problem statements"):
        examples = {
            "Automated Churn Early Warning System": (
                "Our customer success team manually checks each customer's health score every week "
                "by pulling data from three separate spreadsheets. This takes 4 hours per week and errors are common. "
                "We need an automated early warning system that flags at-risk customers and sends Slack alerts."
            ),
            "Self-Service Onboarding Portal": (
                "New customers currently rely on our CS team for every step of onboarding, which takes 30-60 days. "
                "60% of support tickets come from onboarding issues. We need a self-service portal where customers "
                "can complete setup, data migration, and training at their own pace with guided checklists."
            ),
            "Unified Support Dashboard": (
                "Our support team uses three separate tools to manage tickets, track SLA compliance, and report CSAT. "
                "Context switching causes delays and tickets are falling through the cracks. "
                "We need a unified dashboard with SLA alerts, escalation workflows, and automated CSAT surveys."
            ),
        }
        for title, text in examples.items():
            if st.button(f"Load: {title}"):
                st.session_state["example_problem"] = text
                st.info(f"Copy this into the text box above:\n\n{text}")
