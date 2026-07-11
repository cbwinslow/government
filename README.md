# OpenDiscourse

OpenDiscourse is an open, reproducible government-data ingestion and research platform.

The project is designed to discover, download, verify, preserve, normalize, index, and search public government data at scale. Its long-term goal is to make legislative activity, campaign finance, financial disclosures, public records, economic indicators, demographic data, crime statistics, geographic boundaries, and related source documents easier to investigate together without losing provenance.

> **Project status:** architecture and foundation phase. The previous repository contents are retained as legacy references while a clean `opendiscourse` package and data platform are built.

## Goals

OpenDiscourse will provide:

- A reusable Python package under the `opendiscourse` namespace.
- A command-line interface for complete, resumable source synchronization.
- Source adapters for bulk downloads, APIs, feeds, sitemaps, archives, and database dumps.
- A deterministic data lake for JSON, XML, CSV, Parquet, PDF, text, Markdown, GIS, and database artifacts.
- PostgreSQL/PostGIS schemas for cataloging, ingestion state, canonical entities, identity resolution, lineage, search, and analytics.
- Full-text and vector search over versioned, source-linked documents.
- Evidence-backed politician, policy, vote, finance, geography, and impact research.
- Portable `SKILL.md` files for Codex, Claude, and compatible agents.
- A secure MCP server that exposes catalog, retrieval, lineage, and research capabilities.

## Core principles

1. **Preserve before transforming.** Store the original source artifact before any parsing or normalization.
2. **Bulk first.** Prefer complete bulk datasets and database dumps when available; use APIs for hydration, reconciliation, and incremental updates.
3. **Manifest driven.** Every discoverable remote object is represented in a durable manifest before download.
4. **Idempotent and resumable.** Every phase can be rerun safely and resumed after interruption.
5. **Source fidelity.** Raw data remains source-native; canonical schemas contain only genuinely shared concepts.
6. **Provenance everywhere.** Every claim, field, relationship, chunk, and embedding can be traced to its source artifact and transformation.
7. **Identity is explicit.** People and organizations are linked through source identifiers and evidence, never display-name matching alone.
8. **Configuration is validated.** Safe defaults live in version control; secrets remain in environment variables or a secret manager.
9. **Agents use bounded tools.** MCP and skills expose intentional operations instead of arbitrary SQL or unrestricted filesystem access.
10. **Research must be reproducible.** Derived metrics record methodology, versions, time ranges, assumptions, and limitations.

## Initial source priorities

1. Open States / Plural Policy bulk PostgreSQL, JSON, CSV, people, votes, bills, and district data.
2. GovInfo bulk collections, API, feeds, and sitemaps.
3. Congress.gov API reconciliation and detail hydration.
4. Federal Election Commission bulk campaign-finance files and API.
5. House and Senate financial disclosures and transaction reports.
6. Census, ACS, TIGER/Line, geographic, and voting-district datasets.
7. FRED and other economic and labor datasets.
8. DOJ, federal courts, regulatory, enforcement, and public-record collections.

See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for the source registry and acquisition strategy.

## Planned repository layout

```text
.
├── src/opendiscourse/       # Python package
├── tests/                    # unit, contract, integration, and end-to-end tests
├── config/                   # non-secret defaults and source descriptors
├── migrations/               # PostgreSQL migrations
├── docs/                     # architecture, operations, and contributor documentation
├── skills/                   # portable agent skills
├── services/mcp/             # MCP server
├── services/api/             # optional research/catalog API
├── packages/typescript-sdk/  # generated or thin TypeScript client
├── docker/                   # local infrastructure definitions
└── legacy/                   # retained references from the original workspace
```

## Proposed CLI

```bash
opendiscourse init
opendiscourse doctor
opendiscourse source list
opendiscourse source describe govinfo
opendiscourse sync openstates --all
opendiscourse sync govinfo --dataset billstatus --all
opendiscourse run list
opendiscourse run resume <run-id>
opendiscourse verify govinfo
opendiscourse catalog search "BILLSTATUS-119"
opendiscourse artifact show <sha256>
opendiscourse extract pending
opendiscourse normalize pending
opendiscourse identity resolve
opendiscourse embed pending
opendiscourse mcp serve
```

## Configuration model

Configuration is layered in this order:

1. Typed application defaults.
2. `config/default.toml`.
3. Optional environment-specific TOML.
4. Environment variables using the `OPENDISCOURSE_` prefix.
5. Explicit CLI overrides.

Secrets such as API keys, passwords, and DSNs must never be committed. A safe `.env.example` will document supported variables.

## Documentation

- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/DATA_LAKE.md`](docs/DATA_LAKE.md)
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md)
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`docs/LEGACY_MIGRATION.md`](docs/LEGACY_MIGRATION.md)
- [`AGENTS.md`](AGENTS.md)

## Current rebuild policy

The original cloned repositories, datasets, scripts, and experiments are not considered the new application architecture. They are upstream references and possible acquisition components. During migration they will be inventoried, licensed, documented, and moved behind clear boundaries rather than imported into the `opendiscourse` package wholesale.

No large dataset should be committed to ordinary Git history. Raw and processed data belong in the configured data lake or external object storage.

## License and data terms

The OpenDiscourse software license and source-specific data terms will be documented separately. Each adapter must record the source URL, access terms, attribution requirements, and any redistribution limitations for the data it acquires.
