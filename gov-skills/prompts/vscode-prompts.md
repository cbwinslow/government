# VS Code prompts

## Prompt 1: GovInfo database bootstrap
Create a production-minded PostgreSQL schema for GovInfo ingestion. I need `ingest`, `raw`, `core`, and `mart` schemas; tables for job runs, cursors, request logs, manifests, raw packages, raw granules, normalized packages, normalized granules, related-document edges, and asset inventory; strong indexes; copy-paste-ready SQL migrations; and admin queries for duplicates, lag, and referential integrity.

## Prompt 2: GovInfo backfill pipeline
Build a Python ingestion scaffold for GovInfo that uses bulkdata JSON listings for historical discovery and the GovInfo collections lastModified endpoints for incrementals. Include retry/backoff, checksum-based idempotency, structured logging, env-based config, Postgres persistence, raw payload archival, and a CLI with commands for `discover`, `fetch`, `parse`, `reconcile`, and `backfill`.

## Prompt 3: GovInfo MCP integration
Create a small MCP server wrapper or MCP client integration plan for GovInfo that exposes tools for collection discovery, package summary fetch, granule listing, related-document lookup, and bulkdata enumeration. Include authentication via `api.data.gov` key, typed tool schemas, error handling, and VS Code/Cline config examples.

## Prompt 4: Congress.gov database bootstrap
Design a PostgreSQL schema for Congress.gov API v3 ingestion. Include landing tables for raw responses and request logs, normalized tables for bills, bill actions, sponsors, cosponsors, committees, members, amendments, nominations, and treaties, plus bridge tables, partitioning guidance, and admin SQL for freshness and duplicate audits.

## Prompt 5: Congress.gov crawler
Build a rate-aware Python crawler for Congress.gov v3 with checkpointed pagination, `limit=250` where valid, per-endpoint concurrency control, quota ledgering for the 5,000 requests/hour limit, and list/detail hydrators. Include env config, metrics, structured logs, and retry behavior for transient failures only.

## Prompt 6: Joint legislative warehouse
Create a unified warehouse design that combines GovInfo and Congress.gov data into a single legislative intelligence schema. Map package IDs, bill identities, statuses, actions, summaries, and related documents. Produce raw/core/mart schema SQL, lineage notes, and reconciliation queries.

## Prompt 7: VS Code tasks
Generate `.vscode/tasks.json`, `.vscode/launch.json`, and `.env.example` for local development of the ingestion stack. I want tasks for bootstrap DB, run GovInfo backfill, run GovInfo incremental poller, run Congress.gov bills sync, run tests, and run data quality audits.

## Prompt 8: Data quality and operations
Write SQL and Python checks for row-count reconciliation, duplicate keys, orphaned relationships, null-rate drift, stale collections, pagination gaps, and failed-manifest replays. Output should be suitable for cron, GitHub Actions, or Prefect.
