# OpenDiscourse Agent Architecture

> Visual representation of the agent system — tools, agents, data sources, and their interactions.
> These diagrams auto-render as interactive graphs on GitHub and VS Code (Mermaid Preview extension).

---

## 1. System Architecture Overview

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#1a1a2e', 'primaryTextColor': '#e0e0e0', 'primaryBorderColor': '#3b82f6', 'lineColor': '#6b7280', 'secondaryColor': '#16213e', 'tertiaryColor': '#0f3460'}}}%%
graph TB
    subgraph Dashboard["📊 Dashboard (React)"]
        UI["Web UI"]
        API["API Client"]
    end

    subgraph FastAPI["🚀 FastAPI Layer"]
        REST["REST Endpoints<br/>/api/agents/*"]
        Health["Health / Monitoring"]
    end

    subgraph Orchestrator["🧠 Agent Orchestrator"]
        direction TB
        Sys["OpenDiscourseAgentSystem"]
        RA["ResearchAgent"]
        CA["ConsistencyAnalyzer"]
        AG["AlertGenerator"]
    end

    subgraph Tools["🔧 LangChain Tools (8)"]
        direction TB
        CT["CongressSearchTool<br/>Congress.gov API"]
        OT["OpenSecretsTool<br/>Campaign Finance"]
        VT["VoteSmartTool<br/>Interest Groups"]
        VST["VectorSearchTool<br/>Qdrant Semantic Search"]
        PAT["PoliticianAnalysisTool<br/>Multi-source Analysis"]
        HST["HonestyScorerTool<br/>Words vs Actions"]
        DQT["DatabaseQueryTool<br/>PostgreSQL"]
        GT["GDELTSearchTool<br/>Global News"]
    end

    subgraph OpenRouter["🌐 OpenRouter SDK (200+ Models)"]
        direction TB
        ORC["OpenRouterClient"]
        CC["chat_completion()"]
        SO["chat_completion_structured()"]
        SC["stream_completion()"]
        MD["list_models()"]
        MC["compare_models()"]
    end

    subgraph DataSources["🗄️ Data Sources"]
        direction TB
        CG["Congress.gov"]
        OS["OpenSecrets.org"]
        VS["Vote Smart"]
        QD["Qdrant Vector DB"]
        PG["PostgreSQL<br/>(OpenDiscourse DB)"]
        GD["GDELT Global News"]
    end

    subgraph ExistingEngine["⚙️ Existing Engine"]
        HE["HonestyEngine<br/>(scorer.py)"]
        DB["database.py<br/>(SQLAlchemy models)"]
    end

    subgraph Models["📦 Pydantic Models"]
        RR["ResearchReport"]
        DR["DiscrepancyReport"]
        Alert["Alert"]
        ARR["AgentRunResult"]
        MR["ModelComparisonResult"]
    end

    %% Connections
    Dashboard -->|HTTP| REST
    REST --> Sys
    Sys --> RA
    Sys --> CA
    Sys --> AG
    Sys --> ORC
    
    RA --> CT
    RA --> OT
    RA --> VT
    RA --> DQT
    RA --> GT
    
    CA --> HST
    CA --> GT
    
    AG --> ORC
    
    PAT --> CT
    PAT --> OT
    PAT --> ORC
    
    HST --> HE
    HST --> ORC
    
    CT --> CG
    OT --> OS
    VT --> VS
    VST --> QD
    DQT --> PG
    GT --> GD
    
    ORC --> CC
    ORC --> SO
    ORC --> SC
    ORC --> MD
    ORC --> MC
    
    HE -->|uses| ORC
    HE --> PG
    DB --> PG

    %% Styling
    classDef dashboard fill:#1e3a5f,stroke:#3b82f6,color:#fff
    classDef api fill:#1a4731,stroke:#10b981,color:#fff
    classDef orchestrator fill:#4a1942,stroke:#a855f7,color:#fff
    classDef tools fill:#3b1f3b,stroke:#ec4899,color:#fff
    classDef openrouter fill:#1e2a4a,stroke:#60a5fa,color:#fff
    classDef datasource fill:#1a3a3a,stroke:#14b8a6,color:#fff
    classDef engine fill:#3a2a1a,stroke:#f59e0b,color:#fff
    classDef models fill:#2a1a3a,stroke:#a855f7,color:#fff

    class Dashboard,UI,API dashboard
    class FastAPI,REST,Health api
    class Orchestrator,Sys,RA,CA,AG orchestrator
    class Tools,CT,OT,VT,VST,PAT,HST,DQT,GT tools
    class OpenRouter,ORC,CC,SO,SC,MD,MC openrouter
    class DataSources,CG,OS,VS,QD,PG,GD datasource
    class ExistingEngine,HE,DB engine
    class Models,RR,DR,Alert,ARR,MR models
```

---

## 2. Agent Workflow / Orchestration

```mermaid
%%{init: {'theme': 'dark'}}%%
stateDiagram-v2
    [*] --> RequestReceived
    
    RequestReceived --> Router
    Router --> ResearchAgent: /api/agents/research
    Router --> ConsistencyAnalyzer: /api/agents/score-consistency
    Router --> RunTool: /api/agents/run-tool
    Router --> Chat: /api/agents/chat
    Router --> DiscoverModels: /api/agents/discover-models
    
    ResearchAgent --> DBLookup: Step 1
    DBLookup --> CampaignFinance: Step 2
    CampaignFinance --> InterestGroups: Step 3
    InterestGroups --> NewsSearch: Step 4
    NewsSearch --> LLMSynthesis: Step 5
    LLMSynthesis --> Respond
    
    ConsistencyAnalyzer --> GatherNews: Step 1
    GatherNews --> RunHonestyEngine: Step 2
    RunHonestyEngine --> ParseResults: Step 3
    ParseResults --> Respond
    
    RunTool --> ExecuteTool
    ExecuteTool --> Respond
    
    Chat --> OpenRouterCall
    OpenRouterCall --> Respond
    
    DiscoverModels --> QueryOpenRouter
    QueryOpenRouter --> Respond
    
    Respond --> [*]
```

---

## 3. Tool Dependency / Chaining Graph

This shows how tools call **each other** (not just agents calling tools):

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#1a1a2e'}}}%%
graph LR
    subgraph ChainTools["Tool Chaining (How tools call each other)"]
        direction TB
        PAT2["PoliticianAnalysisTool"] -->|"calls"| CT2["CongressSearchTool"]
        PAT2 -->|"calls"| OT2["OpenSecretsTool"]
        PAT2 -->|"calls"| ORC2["OpenRouter LLM"]
        
        CA2["ConsistencyAnalyzer"] -->|"calls"| GT2["GDELTSearchTool"]
        CA2 -->|"calls"| HST2["HonestyScorerTool"]
        HST2 -->|"wraps"| HE2["HonestyEngine (scorer.py)"]
    end
    
    subgraph AgentFlows["Sequential Agent Flow"]
        direction TB
        R["ResearchAgent: DB Lookup"]
        R2["ResearchAgent: Campaign Finance"]
        R3["ResearchAgent: Interest Groups"]
        R4["ResearchAgent: News Search"]
        R5["ResearchAgent: LLM Synthesis"]
        
        R --> R2 --> R3 --> R4 --> R5
    end
```

---

## 4. Data Flow: Research Agent (Sequence)

```mermaid
sequenceDiagram
    participant U as User / Dashboard
    participant A as Agent API
    participant RA as ResearchAgent
    participant DB as PostgreSQL
    participant OS as OpenSecrets
    participant VS as VoteSmart
    participant GD as GDELT
    participant LLM as OpenRouter LLM
    
    U->>A: POST /api/agents/research
    A->>RA: research("Nancy Pelosi")
    
    par Parallel Data Gathering
        RA->>DB: DatabaseQueryTool
        DB-->>RA: Profile data
        
        RA->>OS: OpenSecretsTool (cid)
        OS-->>RA: Campaign finance
        
        RA->>VS: VoteSmartTool (candidate_id)
        VS-->>RA: Interest group ratings
        
        RA->>GD: GDELTSearchTool
        GD-->>RA: News mentions
    end
    
    RA->>LLM: Synthesize all data
    LLM-->>RA: Comprehensive analysis
    
    RA-->>A: ResearchReport
    A-->>U: JSON response
```

---

## 5. Data Flow: Consistency Scoring (Sequence)

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent API
    participant CA as ConsistencyAnalyzer
    participant GD as GDELT News
    participant HE as HonestyEngine
    participant LLM as OpenRouter LLM
    
    U->>A: POST /api/agents/score-consistency
    A->>CA: analyze(name, words, actions)
    
    opt Gather Context
        CA->>GD: Fetch recent news
        GD-->>CA: News articles
    end
    
    CA->>HE: evaluate_consistency()
    HE->>LLM: Structured output (JSON Schema)
    Note over HE,LLM: Models: Lagura M1 Free → Llama 70B Free (fallback)
    LLM-->>HE: HonestyScore (0-100)
    
    HE-->>CA: Score + discrepancies
    CA-->>A: DiscrepancyReport
    A-->>U: JSON response
```

---

## 6. OpenRouter Model Routing

```mermaid
flowchart LR
    subgraph Request["API Request"]
        M["Model: 'google/gemini-3.0-pro'"]
        FB["Fallback Models"]
        F["Fusion Mode"]
    end
    
    subgraph OpenRouter["OpenRouter Gateway"]
        OR["API Gateway"]
        R1["Route to Provider A"]
        R2["Route to Provider B"]
        R3["Route to Provider C"]
    end
    
    subgraph Models2["Available Models (200+)"]
        G3["Gemini 3.0 Pro"]
        L405["Llama 405B Free"]
        L70["Llama 70B Free"]
        H3["Hermes 3 405B Free"]
        C4["Claude 4 Sonnet"]
        G4["GPT-4o"]
    end
    
    M --> OR
    FB --> OR
    F --> OR
    
    OR --> R1 --> G3
    OR --> R2 --> G4
    OR --> R3 --> L405
    
    L405 -.->|fallback| L70
    H3 -.->|fallback| L70
    
    style Request fill:#1e3a5f,stroke:#3b82f6,color:#fff
    style OpenRouter fill:#1a4731,stroke:#10b981,color:#fff
    style Models2 fill:#3b1f3b,stroke:#ec4899,color:#fff
```

---

## 7. Module Dependency / Import Graph

```mermaid
graph TD
    subgraph Agents["src/opendiscourse/agents/"]
        AP["__init__.py"]
        ORS["openrouter_sdk.py<br/>OpenRouterClient"]
        LCT["langchain_tools.py<br/>8 BaseAgentTool classes"]
        ORC["orchestrator.py<br/>ResearchAgent, ConsistencyAnalyzer,<br/>OpenDiscourseAgentSystem"]
    end
    
    subgraph API["src/opendiscourse/api/"]
        AE["agents_endpoints.py<br/>FastAPI routes"]
        MAIN["main.py<br/>FastAPI app"]
    end
    
    subgraph Core["src/opendiscourse/core/"]
        CFG["config.py<br/>Settings (API keys)"]
    end
    
    subgraph Engine["src/opendiscourse/engine/"]
        SC["scorer.py<br/>HonestyEngine"]
    end
    
    subgraph Models["src/opendiscourse/models/"]
        DB["database.py<br/>Politician SQLAlchemy model"]
    end
    
    subgraph Ingestion["src/opendiscourse/ingestion/"]
        CG["congress.py<br/>CongressClient"]
        OS2["opensecrets.py<br/>OpenSecretsClient"]
        VS2["votesmart.py<br/>VoteSmartClient"]
    end
    
    AP --> ORS
    AP --> LCT
    AP --> ORC
    
    LCT --> ORS
    LCT --> SC
    
    ORC --> ORS
    ORC --> LCT
    
    AE --> ORC
    MAIN --> AE
    MAIN --> CFG
    
    ORS --> CFG
    LCT --> CFG
    LCT --> SC
    
    SC --> CFG
    
    LCT --> CG
    LCT --> OS2
    LCT --> VS2
    
    classDef agents fill:#4a1942,stroke:#a855f7,color:#fff
    classDef api fill:#1a4731,stroke:#10b981,color:#fff
    classDef core fill:#3a2a1a,stroke:#f59e0b,color:#fff
    classDef engine fill:#2a1a3a,stroke:#a855f7,color:#fff
    classDef models fill:#1a3a3a,stroke:#14b8a6,color:#fff
    classDef ingestion fill:#3b1f3b,stroke:#ec4899,color:#fff

    class Agents,AP,ORS,LCT,ORC agents
    class API,AE,MAIN api
    class Core,CFG core
    class Engine,SC engine
    class Models,DB models
    class Ingestion,CG,OS2,VS2 ingestion
```

---

## 8. Available Tools Reference

| Tool | Name | Data Source | Cost | Calls Other Tools |
|------|------|-------------|------|-------------------|
| 🔍 **CongressSearchTool** | `congress_search` | Congress.gov API | Free* | — |
| 💰 **OpenSecretsTool** | `opensecrets_finance` | OpenSecrets.org | Free (200 calls/day) | — |
| 📊 **VoteSmartTool** | `votesmart_ratings` | Vote Smart API | Free | — |
| 🔎 **VectorSearchTool** | `vector_search` | Qdrant (local) | Free | — |
| 👤 **PoliticianAnalysisTool** | `analyze_politician` | Multi-source + LLM | LLM cost | CongressSearchTool, OpenSecretsTool, OpenRouter |
| ⚖️ **HonestyScorerTool** | `honesty_score` | OpenRouter LLM | LLM cost (free models avail.) | HonestyEngine (internal) |
| 🗄️ **DatabaseQueryTool** | `database_query` | PostgreSQL (local) | Free | — |
| 📰 **GDELTSearchTool** | `gdelt_news_search` | GDELT Project | Free | — |

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **OpenRouter** | Unified API gateway providing access to 200+ LLMs (free + paid) |
| **LangChain Tool** | A callable function with a name, description, and typed input schema |
| **Agent** | An autonomous workflow that chains multiple tool calls with LLM reasoning |
| **Orchestrator** | Top-level coordinator that routes requests to the right agent |
| **Honesty Engine** | The core LLM evaluation that scores a politician's Words vs Actions |
| **Fusion Mode** | OpenRouter panel routing — multiple models evaluate and synthesize a judge response |
| **Fallback Chain** | Ordered list of models; if primary fails (rate limit, etc.), next model is tried |
| **Structured Output** | JSON Schema-constrained LLM output — forces the model to return valid typed data |