# Politician Finance Pack Inventory

**Last Updated:** 2026-06-04
**Parent:** government/INVENTORY.md

---

## Skill Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `politician-masterdata-admin` | Member/person identity tracking | ✅ Ready |
| `campaign-finance-ingestion-admin` | Campaign finance data ingestion | ✅ Ready |
| `financial-disclosure-ingestion-admin` | Financial disclosure tracking | ✅ Ready |
| `member-tracking-rag-admin` | LlamaIndex RAG integration | ✅ Ready |

---

## Prompts

| File | Topics | Status |
|------|--------|--------|
| `vscode-prompts.md` | Master DB, identity, FEC ingestion, disclosure, RAG, MCP, analytics | ✅ Existing |
| `conflict-analytics-prompts.md` | Trade vs committee, donor alignment, temporal analysis, sector concentration, PTR audit, lobbying overlap, divestment monitoring, insider trading heuristics, ethics portal | ✅ New |

---

## Directory Structure

```
politician-finance-pack/
├── dbt/                  # Data transformation models
├── docs/                 # Documentation
├── prompts/              # 2 prompt files
│   ├── vscode-prompts.md
│   └── conflict-analytics-prompts.md
├── scripts/              # Processing scripts
├── skills/               # 4 skill definitions
│   ├── politician-masterdata-admin.md
│   ├── campaign-finance-ingestion-admin.md
│   ├── financial-disclosure-ingestion-admin.md
│   └── member-tracking-rag-admin.md
├── sql/                  # SQL templates
└── configs/              # Configuration files
```

---

## Key Data Sources

| Source | API/Data | Skill Module |
|--------|----------|--------------|
| OpenFEC | API | `campaign-finance-ingestion-admin` |
| House Disclosures | fd.house.gov | `financial-disclosure-ingestion-admin` |
| Senate Disclosures | senate.gov | `financial-disclosure-ingestion-admin` |
| Congress.gov | API v3 | `politician-masterdata-admin` |

---

## Strategic Objectives

| Objective | Description | Priority |
|-----------|-------------|----------|
| Politician Master DB | Unified legislator database | High |
| Finance Tracking | Campaign + personal finance | High |
| RAG Integration | Semantic search over disclosures | Medium |
| Investment Network | Track stock transactions | Medium |
| Conflict Analytics | Trade/committee/donor cross-reference | Medium |

---

## Action Items

- [x] Create 10 conflict analytics prompts
- [x] Review skill module definitions
- [ ] Set up OpenFEC API access
- [ ] Create legislator ID mapping table
- [ ] Build disclosure ingestion pipeline
- [ ] Integrate with epstein persons database