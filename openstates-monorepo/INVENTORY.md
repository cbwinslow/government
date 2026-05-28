# OpenStates Monorepo Inventory

**Last Updated:** 2026-05-27
**Parent:** government/INVENTORY.md

---

## Repository Overview

| Repo | Purpose | Status |
|------|---------|--------|
| `api-v3/` | REST API v3 | ⚠️ Needs analysis |
| `bobsled/` | Data import pipeline | ⚠️ Needs analysis |
| `jurisdictions/` | State jurisdiction config | ⚠️ Needs analysis |
| `openstates-core/` | Core data models | ⚠️ Needs analysis |
| `openstates-geo/` | Geographic data | ⚠️ Needs analysis |
| `openstates.org/` | Website | ⚠️ Needs analysis |
| `openstates-scrapers/` | State legislature scrapers | ✅ Active |
| `openstates-realtime/` | Real-time update system | ⚠️ Needs analysis |
| `pyopenstates/` | Python client | ⚠️ Needs analysis |
| `people/` | Person tracking | ⚠️ Needs analysis |
| `misconduct/` | Legislator misconduct data | ✅ Active |
| `documentation/` | Docs site | ⚠️ Needs analysis |

---

## Key Components

### openstates-scrapers/

**Purpose:** Scrapers for all 50 state legislatures.

**Structure:**
```
openstates-scrapers/
├── openstates/
│   ├── [state]/           # Individual state scrapers
│   ├── bill.py            # Bill models
│   ├── vote.py            # Vote models
│   └── events.py          # Event models
```

**Status:** ✅ Code present, needs import strategy

### people/

**Purpose:** Track legislators across sessions and jurisdictions.

**Status:** ⚠️ Needs integration with congress-legislators

### misconduct/

**Purpose:** Track legislator misconduct and ethics violations.

**Status:** ✅ Active project

---

## Strategic Objectives

| Objective | Description | Priority |
|-----------|-------------|----------|
| State Legislator Database | Build complete state legislator DB | High |
| Cross-walk IDs | Map legislators across state/federal | High |
| Bill Tracking | Track state bills with federal impact | Medium |
| Misconduct Integration | Import misconduct data | Medium |

---

## Action Items

- [ ] Audit all scrapers for current functionality
- [ ] Identify states with Epstein-connected legislators
- [ ] Map OpenStates legislator IDs to bioguide IDs
- [ ] Import misconduct data to main database
- [ ] Create state+federal legislator unified view
