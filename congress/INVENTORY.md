# Congress Directory Inventory

**Last Updated:** 2026-05-27
**Parent:** government/INVENTORY.md

---

## Repositories Overview

| Repo | Purpose | Status | Stars | Local Path |
|------|---------|--------|-------|------------|
| `api/` | Congress.gov API client | ⚠️ Unknown | - | congress/api |
| `BillMap/` | Bill tracking and mapping | ⚠️ Unknown | - | congress/BillMap |
| `bill-status/` | Bill status XML processing | ⚠️ Unknown | - | congress/bill-status |
| `bulk-data/` | Bulk congressional data access | ⚠️ Unknown | - | congress/bulk-data |
| `collections/` | Congressional document collections | ⚠️ Unknown | - | congress/collections |
| `congress/` | Core congress data library | ⚠️ Unknown | - | congress/congress |
| `congress-data/` | Congressional data by session | ✅ Data present | - | congress/congress-data |
| `congressional-record/` | Congressional record processing | ⚠️ Unknown | - | congress/congressional-record |
| `congress-legislators/` | Legislator database | ✅ Active | 850+ | congress/congress-legislators |
| `congressxml/` | XML processing for congress docs | ⚠️ Unknown | - | congress/congressxml |
| `python-us/` | US geography/state utilities | ⚠️ Unknown | - | congress/python-us |
| `uslm/` | USLM document model | ⚠️ Unknown | - | congress/uslm |

---

## Key Repositories Detail

### congress/congress-legislators

**Purpose:** Complete legislator database with biographical info, social media, and terms of service.

**Data Available:**
- `legislators-current.yaml` - Current legislators
- `legislators-historical.yaml` - Historical legislators
- `committees-current.yaml` - Current committee assignments
- `committees-historical.yaml` - Historical committee assignments
- `executive.yaml` - Executive branch officials

**Status:** ✅ Data present, needs processing
**Next Steps:** Integrate with financial disclosure data

---

### congress/congress-data

**Purpose:** Congress data organized by session numbers (100-119+).

**Structure:**
```
congress-data/
├── 100/, 101/, 102/ ... 119/
│   └── [session data files]
```

**Status:** ✅ Data downloaded
**Next Steps:** Map to legislator identifiers

---

### congress/api

**Purpose:** Python client for Congress.gov API v3.

**Integration Points:**
- API key required (5,000 requests/hour limit)
- XML/JSON support
- Bill tracking, amendments, cosponsors

**Status:** ⚠️ Needs analysis
**Next Steps:** Generate API key, test connectivity

---

## Action Items

- [ ] Audit all congress repositories for READMEs and documentation
- [ ] Inventory data files in congress-data/ by session
- [ ] Create mapping between legislator IDs and financial disclosure data
- [ ] Set up Congress.gov API access
