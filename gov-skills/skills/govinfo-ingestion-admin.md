# Skill: govinfo-ingestion-admin

## Purpose
Use this skill when building or maintaining pipelines for govinfo.gov content discovery, bulk download, normalization, database ingestion, metadata refreshes, and operational admin workflows.

This skill assumes you are working in a codebase with Python, PostgreSQL, and optionally object storage.

## Platform facts you should honor
- GovInfo exposes an API for content and metadata access and requires an `api.data.gov` key.
- GovInfo supports search, collections, packages, granules, published, and related-document API patterns.
- GovInfo provides bulk data listings and downloadable XML for selected collections.
- GovInfo bulk data listings can be enumerated through `/bulkdata/xml/...` and `/bulkdata/json/...` paths.
- GovInfo also publishes feeds and sitemaps that are useful for incremental discovery.
- GovInfo has a public-preview MCP server documented by GPO.

## Primary goals
1. Discover source data reliably.
2. Ingest package metadata, granule metadata, and content artifacts into raw landing tables.
3. Normalize entities for analytics and downstream retrieval.
4. Preserve provenance, source URLs, checksums when available, and ingestion timestamps.
5. Support idempotent reruns and backfills.
6. Keep raw payloads and parsed relational models side by side.

## Recommended architecture
- Discovery layer:
  - GovInfo collections API for incremental lastModified polling.
  - GovInfo published endpoints for publication-date windows.
  - GovInfo search POST endpoint for targeted topical pulls.
  - GovInfo bulkdata JSON/XML listings for large historical backfills.
  - GovInfo feeds/sitemaps for monitoring completeness and drift.
- Landing layer:
  - object storage or filesystem for raw JSON/XML/HTML/TXT/PDF references.
  - `raw_govinfo_events`, `raw_govinfo_packages`, `raw_govinfo_granules` tables.
- Normalize layer:
  - package dimension.
  - granule dimension.
  - collection dimension.
  - related document edges.
  - content asset inventory table.
- Serving layer:
  - materialized views for latest package snapshots.
  - FTS / pg_trgm indexes for text retrieval.
  - optional vector index if embeddings are later added.

## Data modeling guidance
Prefer these PostgreSQL schemas:
- `ingest.*` for job runs, cursors, errors, and manifests.
- `raw.*` for immutable raw payloads.
- `core.*` for cleaned relational entities.
- `mart.*` for reporting views.

Suggested keys:
- `package_id` as durable natural key where available.
- `granule_id` as durable natural key where available.
- synthetic bigint identities only for internal joins.

Suggested operational columns on every raw table:
- `source_system`
- `endpoint`
- `request_url`
- `http_status`
- `fetched_at`
- `content_sha256`
- `payload_json` or `payload_xml`
- `ingest_run_id`

## Incremental ingestion strategy
1. Seed historical data via bulkdata listings.
2. Record every discovered item in a manifest table with source URL and expected type.
3. Fetch raw payloads concurrently with retry and backoff.
4. Parse into canonical package/granule tables.
5. Maintain a cursor by collection and lastModified timestamp.
6. Reconcile with sitemaps or feeds to detect gaps.
7. Re-run failed manifests until terminal disposition is reached.

## Retry and throttling rules
- Respect API quotas and implement token-bucket or leaky-bucket throttling.
- Use request-level retry only for transient 429/5xx/network errors.
- Do not reparse unchanged payloads if checksum and source modified time are identical.
- Keep dead-letter queues for repeatedly failing records.

## Database admin tasks this skill should perform well
- bootstrap schemas, indexes, roles, partitions.
- inspect bloat and vacuum/analyze needs on landing tables.
- compare row counts between manifests, raw, and normalized tables.
- detect duplicate natural keys.
- verify referential integrity between packages and granules.
- produce SQL for refresh windows and backfills.
- generate copy-paste-ready migration scripts.

## Parsing guidance
- Persist original JSON/XML before transformation.
- Parse lightly first; enrich later.
- Keep lossy transformations out of `raw`.
- When XML namespaces are involved, preserve namespace maps explicitly in parser utilities.

## Quality checks
Always run:
- manifest count vs fetched count
- fetched count vs parsed count
- duplicate `package_id` / `granule_id`
- null rate on key fields
- asset mime-type distribution
- lag by collection and publication date

## Deliverables this skill should create on request
- SQL DDL
- dbt or SQL transformation models
- Python ingestion clients
- Airflow/Prefect jobs
- MCP server wiring
- VS Code tasks and launch configs
- operational runbooks

## Prompting template for this skill
When executing work, frame requests like:
- "Design a resilient GovInfo ingestion pipeline for BILLSTATUS and BILLS into PostgreSQL with raw/core schemas, partitioning, and idempotent upserts."
- "Generate a backfill job from GovInfo bulkdata JSON listings plus an incremental poller using collections lastModified endpoints."
- "Create SQL checks for GovInfo package/granule completeness, duplicate keys, and stale collections."
