# OpenDiscourse Roadmap

## Phase 0 — Preserve and reset

- Tag the current repository state as the legacy workspace.
- Inventory cloned upstream repositories, datasets, licenses, and useful scripts.
- Keep legacy code outside the `src/opendiscourse` namespace.
- Establish contribution, agent, architecture, and decision-record conventions.

## Phase 1 — Foundation

Deliver a runnable but source-neutral platform:

- Python package and CLI named `opendiscourse`.
- Typed configuration and `.env.example`.
- PostgreSQL/PostGIS development stack.
- Alembic migrations for catalog and ingestion schemas.
- Artifact storage interface and local filesystem backend.
- Source-adapter protocol and source registry.
- Run, task, manifest, checkpoint, request-log, error, and dead-letter models.
- Structured logging, metrics hooks, retry policy, and graceful shutdown.
- Unit and integration test scaffolding.

Exit criterion: a fixture source can be fully discovered, downloaded, resumed, verified, and cataloged.

## Phase 2 — OpenStates vertical slice

- Download and verify the official bulk PostgreSQL artifact or available session archives.
- Restore dumps into a source-specific staging database.
- Snapshot selected source tables to Parquet.
- Register source-native records and artifacts.
- Normalize people, organizations, jurisdictions, sessions, bills, actions, votes, and memberships.
- Preserve OpenStates identifiers and source lineage.
- Produce completeness and reconciliation reports.

Exit criterion: a clean installation can acquire the supported OpenStates bulk corpus and query normalized legislative records with lineage.

## Phase 3 — GovInfo and Congress.gov

- Implement GovInfo bulk listing and sitemap/feed discovery.
- Download selected collections beginning with BILLSTATUS and BILLS.
- Preserve XML, JSON, text, PDF, and package relationships.
- Add XML extraction with namespace preservation.
- Use Congress.gov for hydration, API-only entities, and reconciliation.
- Normalize bills, amendments, members, committees, actions, votes, nominations, and treaties incrementally.

Exit criterion: federal legislative records can be reconciled across GovInfo and Congress.gov.

## Phase 4 — Political finance and disclosures

- FEC bulk files and API incrementals.
- Candidate and committee identity mapping.
- Receipts, disbursements, independent expenditures, and summary tables.
- House and Senate financial disclosures and periodic transaction reports.
- Asset, owner, transaction range, filing, and document lineage models.

Exit criterion: politician profiles can connect legislative identity to campaign and personal financial records without name-only joins.

## Phase 5 — Geography, demographics, and economics

- Census and ACS metadata-driven acquisition.
- TIGER/Line and legislative/voting district geometry.
- PostGIS transformations and crosswalks.
- Housing, population, income, employment, and demographic observations.
- FRED series metadata and observations.
- Time-aware district and office relationships.

Exit criterion: users can map political activity and join it to geographic and statistical observations with documented vintages.

## Phase 6 — Search and politician research engine

- Versioned text extraction and OCR workflows.
- PostgreSQL full-text indexing.
- Deduplicated chunking and embeddings.
- Evidence-backed person, bill, vote, finance, geography, and policy queries.
- Materialized research views and profile-generation service.
- Methodology records for derived metrics.

Exit criterion: every generated profile statement links to underlying source records or artifacts.

## Phase 7 — Agent interfaces

- Read-only OpenDiscourse MCP server.
- Portable `SKILL.md` packages.
- Safe tools for catalog search, artifact retrieval, lineage, profiles, bills, votes, and finances.
- Explicitly authorized administrative sync tools.
- Optional TypeScript SDK and web research interface.

## Near-term implementation backlog

1. Archive/tag legacy state and write `docs/LEGACY_INVENTORY.md`.
2. Replace the root package metadata with OpenDiscourse packaging.
3. Create `src/opendiscourse` module boundaries.
4. Add typed settings and safe `.env.example`.
5. Bootstrap PostgreSQL/PostGIS with Docker Compose.
6. Implement catalog and ingestion migrations.
7. Implement a fixture source adapter and end-to-end test.
8. Implement OpenStates acquisition as the first real adapter.

## Quality gates for every phase

- tests for changed behavior;
- documented configuration and commands;
- no committed credentials or large downloaded artifacts;
- deterministic and resumable operations;
- reconciliation evidence;
- source license and terms notes;
- lineage from normalized output to raw input;
- explicit limitations and unfinished work.
