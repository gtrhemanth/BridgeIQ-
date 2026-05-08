# BridgeIQ — AI-Powered Business Intelligence & Process Transformation

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=flat&logo=plotly&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude_AI-Sonnet_4.6-D97757?style=flat)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat)

> A Technical Business Analyst portfolio project demonstrating end-to-end BA capabilities — from data modeling and SQL analytics to AI-powered requirements generation, anomaly detection, and live interactive dashboards.

---

## Live Demo

**[Launch BridgeIQ App](https://komhjq3bxsukmilc5tcjgp.streamlit.app/)** ← Click to explore the live platform

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

## App Pages (12 total)

| Page | What It Shows |
|---|---|
| 🏠 Home | Landing page: scenario context, 3 business problems, feature grid with navigation |
| 📊 Executive Dashboard | 9-tab BI dashboard: KPIs, revenue, churn, support, onboarding, cohort retention, SaaS benchmarks, anomaly detection, **capacity planning** · PDF export · inline filters |
| 🧠 AI Insights Engine | Claude Sonnet reads live data → generates executive intelligence brief (McKinsey-style) |
| 🤖 AI Feedback Analyzer | Paste customer feedback → structured pain points + auto-generated user stories |
| 📋 AI Requirements Generator | Describe a business problem → BRD + user stories + UAT cases + risk register |
| 🎯 Interview Simulator | Paste any BA job description → tailored talking points + 8 likely questions + 60-second pitch |
| 🔍 Customer 360 | Full account intelligence: risk score, usage, tickets, **customer journey timeline**, AI account summary |
| 📐 BA Artifacts | Live in-app: 15 user stories, risk register, RACI matrix, process maps, traceability matrix |
| 💡 What-If Simulator | Move sliders (churn %, onboarding %, resolution time) → see live ARR impact waterfall |
| 🔮 Churn Predictor | **ML model** (Logistic Regression) trained on live data → churn probability per customer + feature importances + risk table |
| 💻 SQL Playground | Live SQL editor against the SQLite DB — 5 example queries, schema reference, CSV export |
| 👤 About the Analyst | Project timeline, stats, skills grid, ROI calculator, CTA |

---

## Screenshots

### Executive Dashboard
![Executive Dashboard](https://via.placeholder.com/800x400/0d1b2a/4F8EF7?text=Executive+Dashboard+—+KPIs+%2B+Live+Hero+Strip)

### AI Insights Engine
![AI Insights Engine](https://via.placeholder.com/800x400/0d1b2a/22c55e?text=AI+Insights+Engine+—+Claude+reads+your+data)

### What-If Revenue Simulator
![What-If Simulator](https://via.placeholder.com/800x400/0d1b2a/f59e0b?text=What-If+Simulator+—+Live+ARR+Waterfall)

### Customer 360
![Customer 360](https://via.placeholder.com/800x400/0d1b2a/a78bfa?text=Customer+360+—+Full+Account+Intelligence)

---

## Three-Layer Capability Stack

### Layer 1 — Business Analysis
- **BRD** — 11-section Business Requirements Document (Word .docx)
- **User Stories** — 15 sprint-ready stories with Acceptance Criteria, Story Points, MoSCoW priority
- **Process Maps** — AS-IS / TO-BE churn detection workflow
- **Stakeholder Analysis** — RACI matrix, engagement strategies
- **Risk Register** — 6 identified risks with mitigation strategies
- **Requirements Traceability Matrix** — stories → objectives → data → metrics
- **UAT Framework** — test cases per user story
- **Executive Deck** — 10-slide PowerPoint presentation

### Layer 2 — Data & Analytics
- **Data Model** — 6-table schema designed from scratch; ERD documented
- **Synthetic Data** — 16,000+ rows generated with realistic business patterns (Faker + NumPy)
- **SQL Analytics** — 10 query files: KPIs, churn, revenue trends, SLA compliance, cohort retention, at-risk scoring
- **Composite Risk Score** — multi-signal customer risk scoring logic (SQL CTE)
- **Cohort Retention Analysis** — signup quarter retention and MRR tracking
- **SaaS Benchmarks** — live data vs Baremetrics, Gainsight, Zendesk, Totango

### Layer 3 — Live AI Application
- **Executive Dashboard** — 9-tab Plotly dashboard with inline filters, PDF export, capacity planning
- **Statistical Anomaly Detector** — identifies churn spikes, ticket surges, ghost accounts, SLA concentration
- **Ticket Sentiment Analysis** — TextBlob NLP on 4,000 ticket descriptions → polarity by category + priority
- **3D Customer Segmentation** — Plotly 3D scatter: MRR × Health × Usage, colored by risk tier
- **Capacity Planning** — headcount gap analysis, 12-month CSM hire forecast from cohort growth
- **What-If Revenue Simulator** — interactive ARR impact model (churn × onboarding × resolution)
- **AI Feedback Analyzer** — Claude API → structured pain points + user stories
- **AI Requirements Generator** — Claude API → BRD + user stories + UAT + risk register
- **AI Insights Engine** — Claude Sonnet → McKinsey-style executive intelligence brief
- **Interview Simulator** — JD → tailored prep, talking points, 8 questions + model answers
- **Churn Predictor** — Logistic Regression trained on live data → per-customer churn probability + feature importances
- **SQL Playground** — live SQL editor on SQLite DB with schema reference + CSV export
- **Customer Journey Timeline** — Plotly Gantt per customer: contract → onboarding → transactions → support
- **PDF Executive Report** — one-click styled PDF of KPIs + business summary + recommendations
- **Deep Links** — every page URL-addressable via `?page=` query param

---

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11 |
| Web App | Streamlit |
| Charts | Plotly (bar, area, scatter, waterfall, violin, heatmap, treemap, gauge) |
| AI API | Anthropic Claude (Sonnet 4.6 + Haiku 4.5) |
| Database | SQLite |
| Data Generation | Faker, NumPy, Pandas |
| Documents | python-docx, python-pptx |
| Version Control | Git / GitHub |

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
│   ├── app.py                  # Streamlit multi-page app (9 pages, ~2,600 lines)
│   ├── .env.example            # API key template
│   └── .env                    # Your API key (gitignored)
│
├── docs/
│   ├── build_brd.py            # BRD generator script
│   ├── BridgeIQ_BRD.docx       # Business Requirements Document (generated)
│   ├── data_dictionary.csv     # 48 columns documented
│   └── user_stories.csv        # 15 Jira-importable user stories
│
├── presentation/
│   ├── build_deck.py           # Presentation generator script
│   └── BridgeIQ_Executive_Presentation.pptx
│
└── diagrams/
    ├── erd.md                  # Entity Relationship Diagram (Mermaid)
    ├── process_asis.md         # AS-IS process flow
    └── process_tobe.md         # TO-BE process flow
```

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
- [x] Risk Register (6 risks, scored)
- [x] Requirements Traceability Matrix
- [x] Success Metrics & KPIs
- [x] Entity Relationship Diagram (ERD)
- [x] Data Dictionary (48 columns)
- [x] SQL Analytics Layer (10 queries)
- [x] Executive Dashboard (8 tabs, live)
- [x] Statistical Anomaly Detector (live)
- [x] What-If Revenue Simulator (live)
- [x] Customer 360 View (live)
- [x] AI Feedback Analysis Tool (live)
- [x] AI Requirements Generator (live)
- [x] AI Executive Intelligence Engine (live)
- [x] Interview Simulator (live)
- [x] Executive Presentation Deck

---

## Process Documentation

| Diagram | Description |
|---|---|
| [AS-IS Process Flow](diagrams/process_asis.md) | Current manual churn detection — pain points mapped |
| [TO-BE Process Flow](diagrams/process_tobe.md) | BridgeIQ automated churn prevention workflow |
| [Entity Relationship Diagram](diagrams/erd.md) | Full data model with relationships |
| [Data Dictionary](docs/data_dictionary.csv) | 48 columns documented with types, rules, examples |

---

## About

**Sai Hemanth** — Technical Business Analyst | AI/ML & Data Science | IEEE-Published Researcher

- GitHub: [github.com/gtrhemanth](https://github.com/gtrhemanth)
- Email: gtrhemanth14@gmail.com

> This project demonstrates the ability to operate across the full BA spectrum — from stakeholder interviews and requirements documentation to SQL analytics, AI integration, anomaly detection, and live application delivery. Designed for Technical BA roles requiring both business acumen and technical depth.
