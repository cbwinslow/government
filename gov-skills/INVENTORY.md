# Gov Skills Pack Inventory

**Last Updated:** 2026-05-27
**Parent:** government/INVENTORY.md

---

## Skill Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `govinfo-ingestion-admin` | GovInfo data ingestion | ⚠️ Needs setup |
| `congressgov-ingestion-admin` | Congress.gov API integration | ⚠️ Needs setup |

---

## Directory Structure

```
gov-skills/
├── skills/               # Skill definitions
├── docs/                 # Documentation
├── prompts/              # VS Code prompt templates
├── scripts/              # Processing scripts
├── configs/              # Configuration files
└── pyproject.toml
```

---

## Data Sources

| Source | Access Method | Coverage |
|--------|---------------|----------|
| GovInfo | API + bulk data | Congressional documents |
| Congress.gov | API v3 | Bills, amendments, votes |

---

## Strategic Objectives

| Objective | Description | Priority |
|-----------|-------------|----------|
| API Integration | Set up GovInfo + Congress.gov API access | High |
| Bill Ingestion | Import bills to searchable database | Medium |
| Document Pipeline | Process legislative documents | Medium |

---

## Action Items

- [ ] Review skill module implementations
- [ ] Set up GovInfo API key (api.data.gov)
- [ ] Configure Congress.gov API key
- [ ] Create bill tracking pipeline
