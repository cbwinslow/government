# Ingestion Administration Prompts

## Prompt 1: GovInfo backfill pipeline
Build a Python ingestion scaffold for GovInfo that uses bulkdata JSON listings for historical discovery and the GovInfo collections lastModified endpoints for incrementals. Include retry/backoff, checksum-based idempotency, structured logging, env-based config, Postgres persistence, raw payload archival, and a CLI with commands for discover, fetch, parse, reconcile, and backfill.

## Prompt 2: Congress.gov v3 crawler
Build a rate-aware Python crawler for Congress.gov v3 with checkpointed pagination, limit=250 where valid, per-endpoint concurrency control, quota ledgering for the 5,000 requests/hour limit, and list/detail hydrators. Include env config, metrics, structured logs, and retry behavior for transient failures only.

## Prompt 3: Unified legislative warehouse
Create a unified warehouse design that combines GovInfo and Congress.gov data into a single legislative intelligence schema. Map package IDs, bill identities, statuses, actions, summaries, and related documents. Produce raw/core/mart schema SQL, lineage notes, and reconciliation queries.

## Prompt 4: Data quality and operations
Write SQL and Python checks for row-count reconciliation, duplicate keys, orphaned relationships, null-rate drift, stale collections, pagination gaps, and failed-manifest replays. Output should be suitable for cron, GitHub Actions, or Prefect.

## Prompt 5: OpenFEC ingestor
Build an OpenFEC ingestion framework that pulls candidates, committees, committee histories, cycle summaries, filings, contributions, expenditures, and independent expenditures into PostgreSQL. Include pagination, retries, cycle partitioning, source URL tracking, and CLI commands.

## Prompt 6: Financial disclosure ingestor
Build a financial disclosure and PTR ingestion framework for House and Senate sources. Preserve raw PDFs/HTML, extract structured holdings and transactions, store parser confidence, and normalize assets, liabilities, gifts, travel, and income.

## Prompt 7: RAG ingestion layer
Create a LlamaIndex-based ingestion and retrieval layer for politicians and disclosures using PostgreSQL as source of truth, pgvector for embeddings, and optional Qdrant mirroring. Include chunking strategy, metadata extraction, re-embedding jobs, and filtered retrieval examples.

## Prompt 8: Identity resolver
Create a Python identity-resolution pipeline that links Congress.gov members, Bioguide identifiers, FEC candidate IDs, House/Senate disclosure filers, and campaign committees into canonical master.person and master.organization tables. Include confidence scores, merge logs, and review queues.

## Prompt 9: GovInfo MCP server
Create a real MCP server for GovInfo that exposes tools for collection discovery, package summary fetch, granule listing, related-document lookup, and bulkdata enumeration. Include authentication via api.data.gov key, typed tool schemas, error handling, and VS Code/Cline config examples. The current stub in gov-skills/scripts/govinfo_mcp_server.py only prints a tool listing — replace it with actual HTTP calls to the GovInfo API.

## Prompt 10: Congress.gov MCP server
Build a functional MCP server for Congress.gov API v3 with tools for bill listing/detail, member lookup, amendment search, and committee listing. Implement rate-limit tracking, pagination, and retry logic. The current stub in gov-skills/scripts/congressgov_mcp_server.py only prints a tool listing — replace it with real API integration.