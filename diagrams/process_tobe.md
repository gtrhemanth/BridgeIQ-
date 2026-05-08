# TO-BE Process: Automated Customer Health & Churn Prevention

> Future state with BridgeIQ — automated, proactive, data-driven

```mermaid
flowchart TD
    A([Daily 6:00 AM\nAutomated pipeline runs]) --> B[BridgeIQ pulls data\nfrom all sources\n⚡ Automated]

    B --> B1[Usage Events]
    B --> B2[Billing Transactions]
    B --> B3[Support Tickets]
    B --> B4[Onboarding Status]
    B --> B5[NPS Scores]

    B1 & B2 & B3 & B4 & B5 --> C[Composite Risk Score\ncomputed per customer\n0-100 scale]

    C --> D{Risk Score\nThreshold?}

    D -- Score < 30\nLow Risk --> E([Green — no action\nMonitored daily])
    D -- Score 30-49\nMedium Risk --> F[Flagged on dashboard\nCSM reviews weekly]
    D -- Score 50-79\nHigh Risk --> G[🔔 Slack alert sent\nto CSM automatically\n⏱ within 1 hour]
    D -- Score ≥ 80\nCritical Risk --> H[🚨 Immediate alert\nCSM + CS Director\nnotified in parallel]

    F --> I[CSM reviews\nrisk detail page\nSees exact factors]
    G --> I
    H --> I

    I --> J[CSM selects\nintervention strategy\nbased on risk factors]

    J --> J1[Billing issue?\nRoute to Finance]
    J --> J2[Usage drop?\nOffer training session]
    J --> J3[Support frustration?\nEscalate & expedite]
    J --> J4[Onboarding stuck?\nAssign dedicated CSM]

    J1 & J2 & J3 & J4 --> K[Log intervention\nin BridgeIQ\nTimestamp + owner]

    K --> L[Monitor risk score\nover next 14 days]

    L --> M{Score improving?}
    M -- Yes --> N([✅ Account stabilised\nIntervention logged\nPattern learned])
    M -- No --> O[Escalate to\nVP Customer Success]
    O --> P[Executive outreach\n+ retention offer]
    P --> Q{Outcome?}
    Q -- Retained --> N
    Q -- Churned --> R([❌ Churn recorded\nPost-mortem triggered\nModel updated])

    style A fill:#1a3a5c,color:#fff
    style C fill:#1a2d40,color:#4F8EF7
    style E fill:#0a2e1a,color:#22c55e
    style N fill:#0a2e1a,color:#22c55e
    style R fill:#3d0f0f,color:#ef4444

    classDef auto fill:#1a3a5c,stroke:#4F8EF7,color:#4F8EF7
    classDef alert fill:#3d2a0a,stroke:#f59e0b,color:#f59e0b
    classDef critical fill:#3d0f0f,stroke:#ef4444,color:#ef4444
    class B,B1,B2,B3,B4,B5,C auto
    class G alert
    class H,R critical
```

## Improvements Over AS-IS

| Dimension | AS-IS | TO-BE | Improvement |
|---|---|---|---|
| Detection time | 7 days (weekly review) | < 6 hours (automated) | **97% faster** |
| Data sources | 3 manual spreadsheets | 5 integrated signals | **Unified & complete** |
| Risk assessment | Gut feel | Composite scoring algorithm | **Consistent & auditable** |
| Alert mechanism | Email chain | Slack + in-app notification | **Instant & trackable** |
| Intervention logging | None | Timestamped in BridgeIQ | **Full audit trail** |
| CSM time spent | 4 hrs/week manual review | < 30 min/week (review alerts only) | **88% time saved** |
| Outreach timing | Reactive (after decision) | Proactive (before decision) | **Prevention vs cure** |
