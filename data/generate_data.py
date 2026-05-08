"""
BridgeIQ — Synthetic Data Generator
Generates realistic business data for Apex Solutions (fictional B2B SaaS company)
"""

import pandas as pd
import numpy as np
import random
import sqlite3
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(OUTPUT_DIR, "bridgeiq.db")

# ── Constants ──────────────────────────────────────────────────────────────────
INDUSTRIES = ["Healthcare", "Finance", "Retail", "Manufacturing", "Education",
              "Logistics", "Real Estate", "Legal", "Technology", "Consulting"]
PLANS = ["Starter", "Growth", "Enterprise"]
PLAN_MRR = {"Starter": (299, 499), "Growth": (999, 2499), "Enterprise": (4999, 12999)}
REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
COMPANY_SIZES = ["1-50", "51-200", "201-500", "501-1000", "1000+"]
TICKET_CATEGORIES = ["Billing", "Technical Issue", "Feature Request", "Onboarding", "Integration", "Performance", "Account Management"]
TICKET_PRIORITIES = ["Low", "Medium", "High", "Critical"]
FEATURES = ["Dashboard", "Reporting", "Integrations", "Automation", "User Management",
            "API Access", "Analytics", "Notifications", "Bulk Import", "Audit Logs"]
ONBOARDING_STAGES = ["Account Setup", "Data Migration", "User Training", "Integration Config", "Go-Live"]
DEPARTMENTS = ["Sales", "Customer Success", "Engineering", "Product", "Marketing", "Finance", "HR", "Operations"]
ROLES = {
    "Sales": ["Sales Rep", "Account Executive", "Sales Manager", "VP Sales"],
    "Customer Success": ["CSM", "Senior CSM", "CS Manager", "VP Customer Success"],
    "Engineering": ["Junior Dev", "Software Engineer", "Senior Engineer", "Tech Lead", "Engineering Manager"],
    "Product": ["Product Analyst", "Product Manager", "Senior PM", "VP Product"],
    "Marketing": ["Marketing Analyst", "Marketing Manager", "Growth Manager"],
    "Finance": ["Financial Analyst", "Senior Analyst", "Finance Manager", "CFO"],
    "HR": ["HR Coordinator", "HR Manager", "People Ops Lead"],
    "Operations": ["Operations Analyst", "Ops Manager", "COO"],
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def rand_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2025, 12, 31)

# ── 1. Customers (500 rows) ────────────────────────────────────────────────────
def generate_customers(n=500):
    records = []
    for i in range(1, n + 1):
        plan = random.choice(PLANS)
        mrr_min, mrr_max = PLAN_MRR[plan]
        mrr = round(random.uniform(mrr_min, mrr_max), 2)
        contract_start = rand_date(START_DATE, datetime(2025, 6, 30))

        # 22% churn rate
        churned = random.random() < 0.22
        if churned:
            churn_date = rand_date(
                contract_start + timedelta(days=30),
                min(contract_start + timedelta(days=730), END_DATE)
            )
            status = "Churned"
        else:
            churn_date = None
            status = "Active"

        records.append({
            "customer_id": f"CUST{i:04d}",
            "company_name": fake.company(),
            "industry": random.choice(INDUSTRIES),
            "plan_type": plan,
            "mrr": mrr,
            "region": random.choice(REGIONS),
            "company_size": random.choice(COMPANY_SIZES),
            "contract_start": contract_start.strftime("%Y-%m-%d"),
            "churn_date": churn_date.strftime("%Y-%m-%d") if churn_date else None,
            "status": status,
            "health_score": round(random.gauss(68 if churned else 82, 12), 1),
            "nps_score": random.randint(0, 6) if churned else random.randint(6, 10),
        })
    return pd.DataFrame(records)

# ── 2. Transactions (3000 rows) ────────────────────────────────────────────────
def generate_transactions(customers_df):
    records = []
    tx_types = ["Subscription", "Renewal", "Upgrade", "Downgrade", "One-time Add-on", "Refund"]
    payment_methods = ["Credit Card", "ACH", "Wire Transfer", "Invoice"]
    tx_id = 1

    for _, cust in customers_df.iterrows():
        start = datetime.strptime(cust["contract_start"], "%Y-%m-%d")
        end = datetime.strptime(cust["churn_date"], "%Y-%m-%d") if cust["churn_date"] else END_DATE
        num_tx = random.randint(4, 12)
        for _ in range(num_tx):
            tx_date = rand_date(start, end)
            tx_type = random.choice(tx_types)
            base = cust["mrr"]
            if tx_type == "Refund":
                amount = -round(random.uniform(50, base * 0.5), 2)
            elif tx_type == "Upgrade":
                amount = round(random.uniform(base * 0.1, base * 0.5), 2)
            elif tx_type == "Downgrade":
                amount = -round(random.uniform(base * 0.05, base * 0.3), 2)
            else:
                amount = round(random.uniform(base * 0.8, base * 1.2), 2)

            records.append({
                "transaction_id": f"TXN{tx_id:05d}",
                "customer_id": cust["customer_id"],
                "amount": amount,
                "transaction_date": tx_date.strftime("%Y-%m-%d"),
                "transaction_type": tx_type,
                "status": random.choices(["Completed", "Pending", "Failed"], weights=[88, 8, 4])[0],
                "payment_method": random.choice(payment_methods),
            })
            tx_id += 1

    return pd.DataFrame(records)

# ── 3. Support Tickets (4000 rows) ─────────────────────────────────────────────
SAMPLE_DESCRIPTIONS = {
    "Billing": [
        "I was charged twice this month for my subscription.",
        "My invoice doesn't match the amount on my credit card.",
        "Requesting a refund for unused seats on our plan.",
        "The upgrade price shown in the app is different from what I was charged.",
        "Can you clarify the pricing for adding more users?",
    ],
    "Technical Issue": [
        "The dashboard is not loading — getting a 504 error.",
        "Our data sync stopped working after the last update.",
        "Export to CSV is producing empty files.",
        "Login page throws an error when using SSO.",
        "Notifications are not being delivered to our team emails.",
    ],
    "Feature Request": [
        "We'd love a Slack integration for real-time alerts.",
        "Can you add a bulk user import via CSV?",
        "Please add a dark mode option to the dashboard.",
        "We need custom date range filters in the reports section.",
        "Would be great to have a mobile app version.",
    ],
    "Onboarding": [
        "We are stuck on the data migration step — need guidance.",
        "Our team hasn't received the onboarding training invite.",
        "The setup wizard keeps freezing at Step 3.",
        "Can someone walk us through connecting our CRM?",
        "We need help setting up user roles and permissions.",
    ],
    "Integration": [
        "The Salesforce integration is not syncing contacts properly.",
        "Zapier connection keeps timing out.",
        "Our API key stopped working after a password reset.",
        "We need help setting up the webhook for order updates.",
        "HubSpot integration is duplicating records.",
    ],
    "Performance": [
        "Reports are taking over 2 minutes to load.",
        "The platform is very slow during peak hours (9-11am EST).",
        "Bulk data export is timing out for large datasets.",
        "Dashboard charts lag when we have more than 5 filters active.",
        "API response times have increased significantly this week.",
    ],
    "Account Management": [
        "We need to add 10 more user seats to our plan.",
        "Can we change the primary account admin?",
        "We'd like to upgrade from Growth to Enterprise plan.",
        "Please help us set up SSO for our organization.",
        "We need to update our billing contact information.",
    ],
}

def generate_support_tickets(customers_df, n=4000):
    records = []
    cust_ids = customers_df["customer_id"].tolist()
    churned_ids = set(customers_df[customers_df["status"] == "Churned"]["customer_id"])

    for i in range(1, n + 1):
        cust_id = random.choice(cust_ids)
        category = random.choice(TICKET_CATEGORIES)
        priority = random.choices(TICKET_PRIORITIES, weights=[30, 45, 20, 5])[0]
        created = rand_date(START_DATE, END_DATE)

        base_resolution = {"Low": (24, 96), "Medium": (8, 48), "High": (2, 24), "Critical": (1, 8)}
        lo, hi = base_resolution[priority]
        # churned customers had worse resolution times
        multiplier = 1.6 if cust_id in churned_ids else 1.0
        resolution_hours = round(random.uniform(lo, hi) * multiplier, 1)
        resolved_date = created + timedelta(hours=resolution_hours)
        if resolved_date > END_DATE:
            resolved_date = END_DATE

        sat_score = None
        if random.random() > 0.3:
            sat_score = random.randint(1, 4) if cust_id in churned_ids else random.randint(3, 5)

        description = random.choice(SAMPLE_DESCRIPTIONS[category])

        records.append({
            "ticket_id": f"TKT{i:05d}",
            "customer_id": cust_id,
            "category": category,
            "priority": priority,
            "status": random.choices(["Resolved", "Open", "In Progress", "Escalated"],
                                     weights=[70, 10, 15, 5])[0],
            "created_date": created.strftime("%Y-%m-%d"),
            "resolved_date": resolved_date.strftime("%Y-%m-%d"),
            "resolution_time_hours": resolution_hours,
            "satisfaction_score": sat_score,
            "description": description,
        })

    return pd.DataFrame(records)

# ── 4. Product Usage (8000 rows) ───────────────────────────────────────────────
def generate_product_usage(customers_df, n=8000):
    records = []
    active_custs = customers_df[customers_df["status"] == "Active"]["customer_id"].tolist()
    all_custs = customers_df["customer_id"].tolist()

    for i in range(1, n + 1):
        cust_id = random.choices(active_custs + all_custs, weights=[0.7] * len(active_custs) + [0.3] * len(all_custs))[0] \
                  if active_custs else random.choice(all_custs)
        usage_date = rand_date(START_DATE, END_DATE)
        feature = random.choice(FEATURES)
        session_minutes = round(random.expovariate(1/18), 1)
        session_minutes = min(session_minutes, 120)
        actions = random.randint(1, 80)

        records.append({
            "usage_id": f"USG{i:05d}",
            "customer_id": cust_id,
            "usage_date": usage_date.strftime("%Y-%m-%d"),
            "feature": feature,
            "session_minutes": session_minutes,
            "actions_count": actions,
        })

    return pd.DataFrame(records)

# ── 5. Onboarding (500 rows — one per customer) ────────────────────────────────
def generate_onboarding(customers_df):
    records = []
    for _, cust in customers_df.iterrows():
        start = datetime.strptime(cust["contract_start"], "%Y-%m-%d")
        blockers = ["None", "IT approval delay", "Data quality issues", "Stakeholder unavailability",
                    "Integration complexity", "Resource constraints", "Scope changes"]

        completed = random.random() > 0.18
        if completed:
            completion_date = start + timedelta(days=random.randint(14, 60))
            blocker = "None"
        else:
            completion_date = None
            blocker = random.choice(blockers[1:])

        records.append({
            "onboarding_id": f"ONB{_+1:04d}",
            "customer_id": cust["customer_id"],
            "stage": random.choice(ONBOARDING_STAGES) if not completed else "Go-Live",
            "start_date": start.strftime("%Y-%m-%d"),
            "completion_date": completion_date.strftime("%Y-%m-%d") if completion_date else None,
            "completed": completed,
            "days_to_complete": (completion_date - start).days if completion_date else None,
            "blocker": blocker,
        })
    return pd.DataFrame(records)

# ── 6. Employees (120 rows) ────────────────────────────────────────────────────
def generate_employees(n=120):
    records = []
    for i in range(1, n + 1):
        dept = random.choice(DEPARTMENTS)
        role = random.choice(ROLES[dept])
        hire_date = rand_date(datetime(2018, 1, 1), datetime(2025, 6, 30))
        records.append({
            "employee_id": f"EMP{i:04d}",
            "name": fake.name(),
            "department": dept,
            "role": role,
            "hire_date": hire_date.strftime("%Y-%m-%d"),
            "salary": round(random.uniform(55000, 180000), 2),
            "location": random.choice(["New York", "San Francisco", "Austin", "Chicago", "Remote", "London", "Toronto"]),
        })
    return pd.DataFrame(records)

# ── Save to CSV + SQLite ───────────────────────────────────────────────────────
def save_all():
    print("Generating data...")

    customers   = generate_customers(500)
    transactions = generate_transactions(customers)
    tickets     = generate_support_tickets(customers, 4000)
    usage       = generate_product_usage(customers, 8000)
    onboarding  = generate_onboarding(customers)
    employees   = generate_employees(120)

    dfs = {
        "customers":    customers,
        "transactions": transactions,
        "support_tickets": tickets,
        "product_usage": usage,
        "onboarding":   onboarding,
        "employees":    employees,
    }

    # Save CSVs
    for name, df in dfs.items():
        path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  [OK] {name}.csv - {len(df):,} rows")

    # Save SQLite
    conn = sqlite3.connect(DB_PATH)
    for name, df in dfs.items():
        df.to_sql(name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"  [OK] bridgeiq.db (SQLite) - all tables loaded")

    print(f"\nDone. Files saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    save_all()
