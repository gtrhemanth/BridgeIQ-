# BridgeIQ — Entity Relationship Diagram

## Mermaid ERD (paste at mermaid.live to render)

```mermaid
erDiagram
    CUSTOMERS {
        string customer_id PK
        string company_name
        string industry
        string plan_type
        float  mrr
        string region
        string company_size
        date   contract_start
        date   churn_date
        string status
        float  health_score
        int    nps_score
    }

    TRANSACTIONS {
        string transaction_id PK
        string customer_id   FK
        float  amount
        date   transaction_date
        string transaction_type
        string status
        string payment_method
    }

    SUPPORT_TICKETS {
        string ticket_id PK
        string customer_id       FK
        string category
        string priority
        string status
        date   created_date
        date   resolved_date
        float  resolution_time_hours
        int    satisfaction_score
        string description
    }

    PRODUCT_USAGE {
        string usage_id PK
        string customer_id  FK
        date   usage_date
        string feature
        float  session_minutes
        int    actions_count
    }

    ONBOARDING {
        string onboarding_id PK
        string customer_id   FK
        string stage
        date   start_date
        date   completion_date
        bool   completed
        int    days_to_complete
        string blocker
    }

    EMPLOYEES {
        string employee_id PK
        string name
        string department
        string role
        date   hire_date
        float  salary
        string location
    }

    CUSTOMERS ||--o{ TRANSACTIONS    : "has"
    CUSTOMERS ||--o{ SUPPORT_TICKETS : "raises"
    CUSTOMERS ||--o{ PRODUCT_USAGE   : "generates"
    CUSTOMERS ||--|| ONBOARDING      : "undergoes"
```

---

## Table Descriptions

| Table | Rows | Purpose |
|---|---|---|
| `customers` | 500 | Core customer entity — plan, MRR, health, status |
| `transactions` | ~3,978 | All billing events — subscriptions, upgrades, refunds |
| `support_tickets` | 4,000 | Customer support history with resolution times and CSAT |
| `product_usage` | 8,000 | Feature-level engagement tracking per session |
| `onboarding` | 500 | One-to-one with customers — tracks onboarding stage & blockers |
| `employees` | 120 | Internal workforce data for HR analytics |

---

## Key Relationships

- `customers` → `transactions`: One customer can have many transactions (subscription, renewal, upgrade, refund)
- `customers` → `support_tickets`: One customer can raise many support tickets over their lifecycle
- `customers` → `product_usage`: One customer generates many usage events across features
- `customers` → `onboarding`: Each customer has exactly one onboarding record (one-to-one)
- `employees` is standalone — no FK to customers (internal HR dataset)

---

## Render Instructions

1. Go to **https://mermaid.live**
2. Paste the Mermaid code block above
3. Export as SVG or PNG
4. Add to GitHub repo as `diagrams/erd.svg`
