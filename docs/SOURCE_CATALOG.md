# OpenDiscourse Source Catalog

This document tracks acquisition strategy and integration priority. Endpoint details must be verified against current official documentation when implementing an adapter.

| Source | Initial datasets | Preferred historical path | Incremental path | Priority |
|---|---|---|---|---|
| OpenStates / Plural Policy | people, jurisdictions, sessions, bills, actions, votes, organizations | PostgreSQL dump and session archives | API / refreshed bulk snapshots | 1 |
| GovInfo | BILLSTATUS, BILLS, bill text, Congressional Record, Federal Register, CFR/eCFR | bulk data listings, sitemaps, archives | collections/published APIs, feeds, sitemaps | 1 |
| Congress.gov | members, bills, amendments, committees, votes, nominations, treaties | API backfill where bulk coverage is absent | API modified-date pagination | 1 |
| FEC | candidates, committees, filings, receipts, disbursements, independent expenditures | official bulk files | OpenFEC API and refreshed bulk files | 2 |
| House financial disclosures | annual filings and periodic transaction reports | annual ZIP/index archives | periodic index polling | 2 |
| Senate financial disclosures | annual filings and periodic transaction reports | bulk/index acquisition subject to access rules | index polling | 2 |
| Census / ACS | variables, geographies, estimates, margins of error | API-driven complete table/geography plans and bulk products | annual vintage refresh | 3 |
| TIGER/Line | congressional, state legislative, census, county, tract, block-group geometry | annual shapefile/geodatabase archives | annual refresh | 3 |
| FRED | series metadata and observations | API enumeration or curated authoritative catalogs | API observation updates | 3 |
| DOJ and agency documents | releases, reports, enforcement, case-related public records | source-specific archives and sitemaps | feeds/APIs/site reconciliation | later |
| Federal courts / CourtListener | opinions, dockets, parties, citations | official or partner bulk data where licensed | APIs and webhooks | later |

## Adapter catalog requirements

Each implemented source receives `config/sources/<source>.yaml` and `docs/sources/<source>.md` containing:

- official owner and documentation links;
- datasets and durable identifiers;
- authentication and rate limits;
- formats and expected sizes;
- historical and incremental discovery methods;
- pagination/cursor behavior;
- update and deletion semantics;
- license, terms, robots, and redistribution notes;
- manifest and checkpoint strategy;
- reconciliation method;
- canonical mappings and known ambiguities;
- fixture and integration-test strategy.

## Initial OpenStates approach

Treat the upstream PostgreSQL dump as a source-native snapshot, not the OpenDiscourse canonical database.

```text
download -> checksum -> restore isolated staging DB -> inspect version/schema
-> export source snapshots -> catalog raw records -> normalize -> reconcile
```

OpenStates IDs must be preserved in the identity schema. Internal upstream table names must not leak into public OpenDiscourse contracts.

## Initial GovInfo approach

Use bulk discovery for historical collection coverage and APIs/feeds/sitemaps for incrementals and reconciliation. Preserve package/granule identifiers, source relationships, all available representations, checksums, and modified timestamps.

Start with BILLSTATUS and BILLS before adding broader collections.

## Initial Congress.gov approach

Use Congress.gov primarily to hydrate and reconcile federal legislative entities and to acquire datasets not fully represented in the first GovInfo collections. Pagination, quotas, and modified-date checkpoints must be durable.

## Initial finance approach

Prefer FEC bulk files for complete historical transaction acquisition. Use APIs for metadata enrichment, targeted hydration, and incremental changes. Keep candidate, committee, filing, transaction, and person identities separate until evidence supports linkage.

## Initial Census/GIS approach

Model statistical observations with dataset, vintage, variable, geography, time period, estimate, margin of error, and unit. Geometry must be versioned by vintage and geographic definition. Never join observations to current boundaries without recording a crosswalk or compatibility decision.
