# Master Architecture Diagram

## Summary

This diagram represents the mission-critical Areos target architecture.

- Areos = **Assurance, Reliability, Efficiency Operating System**
- system of assurance, not system of record
- **Do not sell monitoring; sell proof.**
- Existing systems monitor signals; Areos connects signals to validated state, product impact, and audit evidence.
- Utility event → area → batch/product/material → quality risk → evidence → decision.
- AWS Greengrass V2 only at the site edge; local sandbox is developer/test harness only.

## Mermaid diagram

```mermaid
flowchart LR
    subgraph Personas[User personas]
        QA[QA]
        ENG[Engineering]
        PH[Plant Head]
        VA[Validation / Audit]
        ITOT[IT / OT]
    end

    subgraph Sources[Source systems]
        PLC[PLC / equipment]
        SCADA[SCADA / DCS / BMS / EMS]
        HIST[Historian]
        MES[MES / eBR]
        QMS[QMS]
        CMMS[CMMS]
        ERP[ERP]
        LIMS[LIMS]
        DMS[DMS / SOPs]
    end

    subgraph Edge[Site edge security boundary]
        GG[Greengrass V2 core device]
        RO[Read-only connectors]
        BUF[Local buffer / replay]
        UNS[UNS / lineage normalizer]
    end

    subgraph Ingest[AWS ingestion]
        IOT[IoT Core]
        RULES[IoT Rules]
        EB[EventBridge]
        SQS[SQS / DLQ]
        SW[AWS IoT SiteWise]
    end

    subgraph Backbone[Enterprise data backbone]
        S3B[S3 bronze]
        S3S[S3 silver]
        S3G[S3 gold]
        S3A[S3 audit]
        GLUE[Glue Data Catalog]
        LF[Lake Formation]
        STATE[DynamoDB / Aurora PostgreSQL]
        NEP[Amazon Neptune]
        SEARCH[OpenSearch / Bedrock KB]
    end

    subgraph Deterministic[Deterministic processing layer]
        ALG[Versioned deterministic algorithms]
        IDEMP[Fingerprinting + idempotency]
        IMPACT[Event-to-impact + evidence packaging]
    end

    subgraph Control[Control plane]
        APIGW[API Gateway]
        APP[Lambda / ECS]
        COG[Cognito]
    end

    subgraph Bedrock[Bedrock runtime]
        TOOLS[Deterministic tool registry]
        AGENT[Bedrock Agent]
        GUARD[Guardrails]
        ANSWER[Deterministic answer object]
    end

    subgraph Gov[Governance]
        KMS[KMS]
        CT[CloudTrail]
        CW[CloudWatch]
        CFG[AWS Config]
        GD[GuardDuty / Security Hub]
    end

    PLC --> RO
    SCADA --> RO
    HIST --> RO
    MES --> RO
    QMS --> RO
    CMMS --> RO
    ERP --> RO
    LIMS --> RO
    DMS --> RO

    RO --> GG --> BUF --> UNS
    UNS --> IOT
    UNS --> EB
    UNS --> SW
    IOT --> RULES --> SQS
    EB --> SQS
    SW --> S3B
    SQS --> S3B
    S3B --> S3S --> S3G
    S3B --> S3A
    S3S --> ALG
    S3S --> NEP
    S3S --> SEARCH
    ALG --> IMPACT --> S3G
    IDEMP --> STATE
    ALG --> STATE
    IMPACT --> S3A
    S3B --> GLUE
    S3S --> GLUE
    S3G --> GLUE
    S3A --> GLUE
    GLUE --> LF
    NEP --> ANSWER
    STATE --> ANSWER
    S3G --> ANSWER
    SEARCH --> AGENT
    ANSWER --> TOOLS --> AGENT --> GUARD
    COG --> APIGW --> APP --> TOOLS
    GUARD --> QA
    GUARD --> ENG
    GUARD --> PH
    GUARD --> VA
    GUARD --> ITOT

    KMS -.-> Ingest
    KMS -.-> Backbone
    KMS -.-> Control
    CT -.-> Ingest
    CT -.-> Backbone
    CT -.-> Control
    CW -.-> Ingest
    CW -.-> Backbone
    CW -.-> Control
    CFG -.-> Control
    GD -.-> Edge
    GD -.-> Ingest
    GD -.-> Backbone
```

## Interpretation notes

- The source estate stays in place. Areos does not replace MES, QMS, BMS, EMS, SCADA, historians, CMMS, LIMS, ERP, OEE, or enterprise lakehouse platforms.
- Greengrass V2 establishes the site-edge runtime boundary.
- SiteWise provides hot/warm industrial time-series and asset context.
- S3 + Glue + Lake Formation provide governed lakehouse persistence.
- Neptune stores evidence and provenance relationships.
- DynamoDB / Aurora PostgreSQL store workflow and idempotent processing state.
- OpenSearch / Bedrock KB support retrieval only.
- Deterministic algorithms produce regulated conclusions; Bedrock only renders or explains them.
