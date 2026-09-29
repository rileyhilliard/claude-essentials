# Mermaid Diagram Pattern Examples

This file contains detailed examples of common Mermaid diagram patterns referenced from the main skill.

The examples use the light-mode palette. The skill's default is dark mode, so swap in the Dark Mode values from [color-palettes.md](color-palettes.md) unless the diagram will render on a light background.

## Contents

- [Pattern 1: Three-Tier Architecture](#pattern-1-three-tier-architecture)
- [Pattern 2: Request Flow with Error Handling](#pattern-2-request-flow-with-error-handling)
- [Pattern 3: State Machine with Semantic Colors](#pattern-3-state-machine-with-semantic-colors)
- [Pattern 4: Data Flow Pipeline](#pattern-4-data-flow-pipeline)
- [Advanced Technique: Highlighting Critical Paths](#advanced-technique-highlighting-critical-paths)
- [Using Icons and Emojis](#using-icons-and-emojis)
- [Entity Relationship Diagram](#entity-relationship-diagram)

## Pattern 1: Three-Tier Architecture

```mermaid
flowchart LR
    subgraph frontend["Frontend Layer"]
        ui[Web UI]
        mobile[Mobile App]
    end

    subgraph backend["Backend Layer"]
        api[API Gateway]
        auth[Auth Service]
        business[Business Logic]
    end

    subgraph data["Data Layer"]
        db[(Database)]
        cache[(Cache)]
    end

    ui --> api
    mobile --> api
    api --> auth
    api --> business
    business --> db
    business --> cache

    style frontend fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
    style backend fill:#dcfce7,stroke:#10b981,stroke-width:2px
    style data fill:#fce7f3,stroke:#ec4899,stroke-width:2px
    style api fill:#3b82f6,color:#ffffff,stroke:#1e40af,stroke-width:2px
```

**Why this works:**

- Clear visual separation of layers with color
- Semantic colors (blue=frontend, green=backend, pink=data)
- Key component (API Gateway) highlighted with darker fill
- Clean left-to-right flow

## Pattern 2: Request Flow with Error Handling

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Auth
    participant DB

    User->>+API: POST /order
    API->>+Auth: Validate Token

    alt Valid Token
        Auth-->>-API: ✓ Valid
        API->>+DB: Create Order
        DB-->>-API: Order ID
        API-->>-User: 201 Created
    else Invalid Token
        Auth-->>API: ✗ Invalid
        API-->>User: 401 Unauthorized
    end

    Note over User,DB: Error responses return immediately
```

**Why this works:**

- Shows both success and error paths
- Uses alt block for clear branching
- Includes status codes for clarity
- Note provides additional context
- Clean, uncluttered layout

## Pattern 3: State Machine with Semantic Colors

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review: Submit
    Review --> Approved: Approve
    Review --> Draft: Request Changes
    Approved --> Published: Publish
    Published --> Archived: Archive
    Archived --> [*]

    Review --> Rejected: Reject
    Rejected --> [*]

    style Draft fill:#fef3c7,stroke:#f59e0b,stroke-width:2px
    style Review fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
    style Approved fill:#dcfce7,stroke:#10b981,stroke-width:2px
    style Published fill:#dcfce7,stroke:#10b981,stroke-width:3px
    style Rejected fill:#fee2e2,stroke:#ef4444,stroke-width:2px
    style Archived fill:#f3f4f6,stroke:#6b7280,stroke-width:2px
```

**Why this works:**

- Colors indicate state semantics (yellow=draft, blue=in-process, green=success, red=terminal-negative)
- Published state has thicker border (current/most common state)
- Clear state transition labels
- Both success and failure paths shown

## Pattern 4: Data Flow Pipeline

```mermaid
flowchart LR
    source[("Data Source")]

    subgraph ingestion["Ingestion Layer"]
        api[API Collector]
        queue[Message Queue]
    end

    subgraph processing["Processing Layer"]
        validate[Validate]
        transform[Transform]
        enrich[Enrich]
    end

    subgraph storage["Storage Layer"]
        warehouse[(Data Warehouse)]
        lake[(Data Lake)]
    end

    source --> api
    api --> queue
    queue --> validate
    validate --> transform
    transform --> enrich
    enrich --> warehouse
    enrich --> lake

    validate -.->|Invalid Data| dlq[("Dead Letter Queue")]

    style source fill:#fef3c7,stroke:#f59e0b,stroke-width:2px
    style ingestion fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
    style processing fill:#dcfce7,stroke:#10b981,stroke-width:2px
    style storage fill:#fce7f3,stroke:#ec4899,stroke-width:2px
    style queue fill:#f3e8ff,stroke:#a855f7,stroke-width:2px
    style dlq fill:#fee2e2,stroke:#ef4444,stroke-width:2px
```

**Why this works:**

- Pipeline flow is left-to-right (natural reading)
- Layers clearly separated by color
- Error path (dead letter queue) shown with dotted line and red
- Queue highlighted differently (purple) to show async boundary
- Database symbols for storage components

## Advanced Technique: Highlighting Critical Paths

```mermaid
flowchart TB
    start([User Login]) --> auth{Authenticated?}
    auth -->|Yes| dashboard[Dashboard]
    auth -->|No| login[Login Form]
    login --> auth

    dashboard --> action[Perform Action]

    style start fill:#dcfce7,stroke:#10b981,stroke-width:3px
    style auth fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
    style dashboard fill:#dcfce7,stroke:#10b981,stroke-width:3px
    style action fill:#dcfce7,stroke:#10b981,stroke-width:2px
    style login fill:#fef3c7,stroke:#f59e0b,stroke-width:2px
    linkStyle 0,1,4 stroke:#10b981,stroke-width:3px
    linkStyle 2,3 stroke:#f59e0b,stroke-width:2px
```

**Technique**: Main path uses green with thick strokes, alternate path uses amber with normal width.

## Using Icons and Emojis

```mermaid
flowchart LR
    user["👤 User"]
    web["🌐 Web App"]
    api["⚙️ API"]
    db[("💾 Database")]
    cache[("⚡ Cache")]

    user --> web
    web --> api
    api --> db
    api --> cache

    style user fill:#dbeafe,stroke:#3b82f6
    style web fill:#dbeafe,stroke:#3b82f6
    style api fill:#dcfce7,stroke:#10b981
    style db fill:#fce7f3,stroke:#ec4899
    style cache fill:#fef3c7,stroke:#f59e0b
```

**Use sparingly**: Icons can help but too many become noisy. Best for user types, external systems, and storage.

## Entity Relationship Diagram

```mermaid
erDiagram
    Customer ||--o{ Order : places
    Order ||--|{ LineItem : contains
    Product ||--o{ LineItem : "ordered in"

    Customer {
        string id PK
        string name
        string email
    }

    Order {
        string id PK
        string customer_id FK
        datetime created_at
    }

    LineItem {
        string id PK
        string order_id FK
        string product_id FK
        int quantity
    }

    Product {
        string id PK
        string name
        decimal price
    }
```

**ERD-specific tips:**

- Always show cardinality (one-to-many, many-to-many)
- Include primary keys (PK) and foreign keys (FK)
- Keep to essential fields - full schema belongs in docs
- Use relationship labels that read naturally
