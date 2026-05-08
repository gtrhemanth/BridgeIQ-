# BridgeIQ — AI-Powered Business Intelligence & Process Transformation

> A Technical Business Analyst portfolio project demonstrating end-to-end BA capabilities — from data modeling and SQL analytics to AI-powered requirements generation and live interactive dashboards.

---

## Live Demo

**[Launch BridgeIQ App](https://share.streamlit.io/gtrhemanth/bridgeiq)** ← Click to explore the live platform

---

## What Is BridgeIQ?

BridgeIQ simulates a real-world Technical BA engagement at **Apex Solutions**, a fictional B2B SaaS company facing three critical business problems:

| Problem | Data Signal | Business Impact |
|---|---|---|
| 22% annual churn rate | 110 of 500 customers lost | ~$1.8M ARR at risk |
| 18% onboarding failure | 90 customers stuck mid-process | 2.4x higher churn probability |
| 28hr avg ticket resolution | 35% SLA breach on critical tickets | CSAT declining, support costs rising |

As the Technical BA, I diagnosed these problems using data analysis, redesigned the processes, specified AI-integrated solutions, and delivered a complete set of BA artifacts — all documented and built in this repository.

---

## Project Structure

```
BridgeIQ/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── generate_data.py        # Synthetic data generator (Faker + business logic)
│   ├── customers.csv           # 500 customers
│   ├── transactions.csv        # ~4,000 billing events
│   ├── support_tickets.csv     # 4,000 tickets with descriptions
│   ├── product_usage.csv       # 8,000 usage events
│   ├── onboarding.csv          # 500 onboarding records
│   ├── employees.csv           # 120 employees
│   └── bridgeiq.db             # SQLite database (all tables)
│
├── sql/
│   ├── 01_kpi_overview.sql
│   ├── 02_churn_analysis.sql
│   ├── 03_revenue_trends.sql
│   ├── 04_support_ticket_analysis.sql
│   ├── 05_product_usage_analysis.sql
│   ├── 06_onboarding_analysis.sql
│   ├── 07_at_risk_customers.sql
│   ├── 08_cohort_retention.sql
│   ├── 09_employee_workforce.sql
│   └── 10_executive_summary_view.sql
│
├── app/
│   ├── app.py                  # Streamlit multi-page app
│   ├── .env.example            # API key template
│   └── .env                    # Your API key (gitignored)
│
├── docs/
│   ├── build_brd.py            # BRD generator script
│   ├── BridgeIQ_BRD.docx       # Business Requirements Document (generated)
│   └── user_stories.csv        # 15 Jira-importable user stories
│
├── presentation/
│   ├── build_deck.py           # Presentation generator script
│   └── BridgeIQ_Executive_Presentation.pptx
│
└── diagrams/
    └── erd.md                  # Entity Relationship Diagram (Mermaid)
```

---

## Three-Layer Capability Stack

### Layer 1 — Business Analysis (for every BA hiring manager)
- **BRD** — 11-section Business Requirements Document (Word .docx)
- **User Stories** — 15 sprint-ready stories with Acceptance Criteria, Story Points, MoSCoW priority
- **Process Maps** — AS-IS / TO-BE churn detection workflow
- **Stakeholder Analysis** — RACI matrix, engagement strategies
- **Risk Register** — 6 identified risks with mitigation strategies
- **UAT Framework** — test cases per user story
- **Executive Deck** — 10-slide PowerPoint presentation

### Layer 2 — Data & Analytics (for technical interviewers)
- **Data Model** — 6-table schema designed from scratch; ERD documented
- **Synthetic Data** — 16,000+ rows generated with realistic business patterns (Faker + NumPy)
- **SQL Analytics** — 10 query files covering: KPIs, churn analysis, revenue trends, SLA compliance, cohort retention, at-risk scoring, feature adoption
- **Composite Risk Score** — multi-signal customer risk scoring logic (SQL CTE)

### Layer 3 — Live AI Application (what nobody else has)
- **Executive Dashboard** — Plotly charts with real data: revenue trend, churn by plan/industry, feature adoption, at-risk customer table
- **AI Feedback Analyzer** — paste customer feedback → Claude API → structured pain points + auto-generated user stories
- **AI Requirements Generator** — describe a business problem → Claude API → BRD excerpt + user stories + acceptance criteria + UAT cases + risk register

---

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11 |
| Web App | Streamlit |
| Charts | Plotly |
| AI API | Anthropic Claude (claude-haiku-4-5) |
| Database | SQLite |
| Data Generation | Faker, NumPy, Pandas |
| Documents | python-docx, python-pptx |
| Version Control | Git / GitHub |

---

## Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/gtrhemanth/BridgeIQ.git
cd BridgeIQ
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate the data
```bash
cd data
python generate_data.py
cd ..
```

### 4. Add your API key
```bash
cp app/.env.example app/.env
# Edit app/.env and add your Anthropic API key
```

### 5. Run the app
```bash
cd app
streamlit run app.py
```

### 6. (Optional) Regenerate documents
```bash
cd docs && python build_brd.py
cd ../presentation && python build_deck.py
```

---

## BA Deliverables Checklist

- [x] Business Requirements Document (BRD)
- [x] Stakeholder Analysis & RACI Matrix
- [x] AS-IS / TO-BE Process Maps
- [x] 15 User Stories with Acceptance Criteria
- [x] Risk Register
- [x] Success Metrics & KPIs
- [x] Entity Relationship Diagram (ERD)
- [x] Data Dictionary
- [x] SQL Analytics Layer (10 queries)
- [x] Executive Dashboard (live)
- [x] AI Feedback Analysis Tool (live)
- [x] AI Requirements Generator (live)
- [x] Executive Presentation Deck
- [x] UAT Test Framework

---

## About

**Sai Hemanth** — Technical Business Analyst | AI/ML & Data Science | IEEE-Published Researcher

- GitHub: [github.com/gtrhemanth](https://github.com/gtrhemanth)
- Email: gtrhemanth14@gmail.com

> This project demonstrates the ability to operate across the full BA spectrum — from stakeholder interviews and requirements documentation to SQL analytics, AI integration, and live application delivery. Designed for Technical BA roles requiring both business acumen and technical depth.
