# Politician Finance Pack Inventory

**Last Updated:** 2026-05-27
**Parent:** government/INVENTORY.md

---

## Skill Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `politician-masterdata-admin` | Member/person identity tracking | ⚠️ Needs setup |
| `campaign-finance-ingestion-admin` | Campaign finance data ingestion | ⚠️ Needs setup |
| `financial-disclosure-ingestion-admin` | Financial disclosure tracking | ⚠️ Needs setup |
| `member-tracking-rag-admin` | LlamaIndex RAG integration | ⚠️ Needs setup |

---

## Directory Structure

```
politician-finance-pack/
├── dbt/                  # Data transformation models
├── docs/                 # Documentation
├── prompts/              # VS Code prompt templates
├── scripts/              # Processing scripts
├── skills/               # Skill definitions
├── sql/                  # SQL templates
└── configs/              # Configuration files
```

---

## Key Data Sources

| Source | API/Data | Purpose |
|--------|----------|---------|
| OpenFEC | API | Campaign finance data |
| House Disclosures | fd.house.gov | Financial disclosures |
| Senate Disclosures | senate.gov | Financial disclosures |
| Congress.gov | API v3 | Legislator info |

---

## Strategic Objectives

| Objective | Description | Priority |
|-----------|-------------|----------|
| Politician Master DB | Unified legislator database | High |
| Finance Tracking | Campaign + personal finance | High |
| RAG Integration | Semantic search over disclosures | Medium |
| Investment Network | Track stock transactions | Medium |

---

## Action Items

- [ ] Review skill module definitions
- [ ] Set up OpenFEC API access
- [ ] Create legislator ID mapping table
- [ ] Build disclosure ingestion pipeline
- [ ] Integrate with epstein persons database
