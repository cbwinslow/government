# Gov Skills Pack Inventory

**Last Updated:** 2026-06-04
**Parent:** government/INVENTORY.md

---

## Skill Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `govinfo-ingestion-admin` | GovInfo data ingestion | ✅ Ready |
| `congressgov-ingestion-admin` | Congress.gov API integration | ✅ Ready |
| `courtlistener-skill` | Courtlistener legal history extraction | ✅ Ready |
| `financial-disclosures-skill` | Financial disclosure PDF processing | ✅ Ready |
| `database-population-agent` | Entity resolution and DB population | ✅ Ready |
| `gdelt-news-ingestion` | GDELT news monitoring and quote extraction | ✅ New |
| `honesty-engine-scorer` | LLM-based consistency scoring engine | ✅ New |
| `qdrant-vector-embedding-admin` | Qdrant vector store and embeddings | ✅ New |
| `fastapi-dashboard-admin` | FastAPI backend and React dashboard | ✅ New |
| `infrastructure-ops-admin` | Docker, PostgreSQL, Redis, Celery ops | ✅ New |

---

## Prompts

| File | Topics | Status |
|------|--------|--------|
| `vscode-prompts.md` | GovInfo/Congress DB bootstrap, crawl, warehouse | ✅ Existing |
| `honesty-engine-prompts.md` | Scoring, pipeline orchestration, GDELT cross-ref, Qdrant search | ✅ New |
| `ingestion-admin-prompts.md` | GovInfo, Congress, OpenFEC, disclosures, identity, MCP | ✅ New |

---

## Directory Structure

```
gov-skills/
├── skills/                 # 10 skill definitions
│   ├── govinfo-ingestion-admin.md
│   ├── congressgov-ingestion-admin.md
│   ├── courtlistener-skill.md
│   ├── financial-disclosures-skill.md
│   ├── database-population-agent.md
│   ├── gdelt-news-ingestion.md
│   ├── honesty-engine-scorer.md
│   ├── qdrant-vector-embedding-admin.md
│   ├── fastapi-dashboard-admin.md
│   └── infrastructure-ops-admin.md
├── docs/                   # Documentation
├── prompts/                # 3 prompt files
│   ├── vscode-prompts.md
│   ├── honesty-engine-prompts.md
│   └── ingestion-admin-prompts.md
├── scripts/                # Processing scripts
├── configs/                # Configuration files
└── INVENTORY.md
```

---

## Data Sources Coverage

| Source | Access Method | Skill Module |
|--------|---------------|--------------|
| GovInfo | API + bulk data | `govinfo-ingestion-admin` |
| Congress.gov | API v3 | `congressgov-ingestion-admin` |
| Courtlistener/RECAP | REST API | `courtlistener-skill` |
| House/Senate FD | ZIP/PDF | `financial-disclosures-skill` |
| OpenStates | v3 API | `database-population-agent` (identity) |
| GDELT Project | 2.0 API | `gdelt-news-ingestion` |
| OpenRouter LLM | API | `honesty-engine-scorer` |
| Qdrant | REST/gRPC | `qdrant-vector-embedding-admin` |
| FastAPI / React | REST + SPA | `fastapi-dashboard-admin` |

---

## Action Items

- [x] Create Honesty Engine scorer skill
- [x] Create GDELT news ingestion skill
- [x] Create Qdrant/vector embedding admin skill
- [x] Create FastAPI/dashboard admin skill
- [x] Create infrastructure ops admin skill
- [x] Create 10 Honesty Engine / OpenDiscourse prompts
- [x] Create 10 ingestion admin prompts
- [ ] Review all skill module implementations for completeness
- [ ] Set up GovInfo API key (api.data.gov)
- [ ] Configure Congress.gov API key
- [ ] Configure OpenFEC API access
- [ ] Replace stub MCP servers with real implementations