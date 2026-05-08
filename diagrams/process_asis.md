# AS-IS Process: Customer Churn Detection & Response

> Current state at Apex Solutions — manual, reactive, error-prone

```mermaid
flowchart TD
    A([Monday 9:00 AM\nCSM starts work]) --> B[Open Spreadsheet 1\nUsage Data]
    B --> C[Open Spreadsheet 2\nBilling Data]
    C --> D[Open Spreadsheet 3\nSupport Tickets]
    D --> E[Manually cross-reference\n3 spreadsheets\n⏱ ~2 hours]
    E --> F{Any red flags\nspotted?}

    F -- No --> G([End — no action taken\nRisk: missed signals])
    F -- Yes --> H[CSM uses gut feel\nto assess severity]

    H --> I{How serious?}
    I -- Seems OK --> G
    I -- Concerned --> J[Send email to\nCS Director]

    J --> K{Director\navailable?}
    K -- No --> L([Ticket sits in inbox\n⚠ No SLA enforced])
    K -- Yes --> M[Director reviews\n⏱ +1-2 days later]

    M --> N[CSM manually reaches\nout to customer]
    N --> O{Customer\nresponse?}
    O -- Responds --> P[Try to retain\ncustomer]
    O -- No response --> Q([Customer churns\n❌ Revenue lost])
    P --> R{Retained?}
    R -- Yes --> S([Account saved\nbut process was slow])
    R -- No --> Q

    style A fill:#1a3a5c,color:#fff
    style G fill:#3d0f0f,color:#ef4444
    style L fill:#3d2a0a,color:#f59e0b
    style Q fill:#3d0f0f,color:#ef4444
    style S fill:#0a2e1a,color:#22c55e

    classDef pain fill:#3d0f0f,stroke:#ef4444,color:#ef4444
    classDef warn fill:#3d2a0a,stroke:#f59e0b,color:#f59e0b
    class E,H pain
    class J,K warn
```

## Pain Points Identified

| Step | Issue | Time Lost | Business Impact |
|---|---|---|---|
| Spreadsheet cross-reference | 3 separate data sources, no automation | 2-4 hrs/week | High — data gaps and errors |
| Risk assessment | Gut feel, no scoring criteria | Variable | High — inconsistent decisions |
| Escalation | Email chain, no SLA | 1-2 days | High — slow response |
| Customer outreach | Reactive — customer already decided | Too late | Critical — churn already decided |
| Audit trail | None | — | Medium — no learning loop |

**Root Cause:** No integrated data layer, no alerting system, fully manual and reactive process.
