# Financial Disclosures Inventory

**Last Updated:** 2026-05-27
**Parent:** government/INVENTORY.md

---

## Data Overview

| Year | File Size | Status |
|------|-----------|--------|
| 2008FD | 19 MB | ✅ Downloaded |
| 2009FD | 22 MB | ✅ Downloaded |
| 2010FD | 21 MB | ✅ Downloaded |
| 2011FD | 39 MB | ✅ Downloaded |
| 2012FD | 161 MB | ✅ Downloaded |
| 2013FD | 209 MB | ✅ Downloaded |
| 2014FD | 1 MB | ✅ Downloaded |
| 2015FD | 76 MB | ✅ Downloaded |
| 2016FD | 121 MB | ✅ Downloaded |
| 2017FD | 119 MB | ✅ Downloaded |
| 2018FD | 127 MB | ✅ Downloaded |
| 2019FD | 98 MB | ✅ Downloaded |
| 2020FD | 95 MB | ✅ Downloaded |
| 2021FD | 95 MB | ✅ Downloaded |
| 2022FD | 95 MB | ✅ Downloaded |
| 2023FD | 84 MB | ✅ Downloaded |
| 2024FD | 80 MB | ✅ Downloaded |
| **Total** | **~1.3 GB** | |

---

## Strategic Objectives

| Objective | Description | Status |
|-----------|-------------|--------|
| Data Extraction | Parse PDF/ZIP files into structured data | ⏳ Pending |
| Politician Linking | Map disclosures to legislator database | ⏳ Pending |
| Transaction Tracking | Extract investment transactions | ⏳ Pending |
| Timeline Analysis | Track disclosure timing patterns | ⏳ Pending |
| Cross-Reference Epstein | Identify Epstein-connected assets | ⏳ Pending |

---

## Data Sources

- **House Disclosures**: fd.house.gov, disclosures-clerk.house.gov
- **Senate Disclosures**: senate.gov
- **OGE Guidance**: Public disclosure timing rules (45-day filing)

---

## Known Challenges

1. **PDF Format** - Disclosures are PDF forms, not structured data
2. **Member Identification** - Need mapping from names to bioguide IDs
3. **Missing Data** - Some years have incomplete disclosures
4. **Parsing Complexity** - Forms vary by year and chamber

---

## Action Items

- [ ] Audit ZIP file contents (XML? PDF? HTML?)
- [ ] Create extraction pipeline for all years
- [ ] Build legislator name → bioguide ID mapping
- [ ] Parse transaction tables from disclosure forms
- [ ] Create unified disclosure database schema
- [ ] Cross-reference with Epstein person database
