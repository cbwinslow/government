# OpenDiscourse Project Charter

## Vision

OpenDiscourse will make public government data easier to acquire, preserve, connect, search, audit, and understand.

The project will provide reusable tooling that lets researchers, journalists, developers, civic organizations, and individual citizens bootstrap a complete local or self-hosted government-data lake and PostgreSQL/PostGIS research database without writing a custom downloader for every agency.

## Primary outcomes

OpenDiscourse should enable a user to:

- discover every public record covered by a supported source adapter;
- download full historical bulk datasets and continue with incremental updates;
- retain source-native JSON, XML, CSV, PDF, text, geospatial, archive, and database artifacts;
- inspect exactly where every normalized fact originated;
- connect politicians, offices, bills, votes, committees, campaign-finance records, disclosures, geography, demographics, crime, housing, and economic indicators;
- perform SQL, GIS, full-text, semantic, and graph-assisted research;
- produce evidence-backed politician and policy profiles;
- expose catalog and research capabilities safely to AI agents through MCP and portable skills.

## Guiding principles

### Bulk first, API second

Historical acquisition should use authoritative bulk downloads, database dumps, feeds, sitemaps, and archives whenever possible. APIs are best used for hydration, incremental updates, reconciliation, and records not included in bulk distributions.

### Preserve before transforming

Original bytes are the legal and evidentiary foundation of the platform. Raw artifacts are immutable. Parsing, OCR, text extraction, normalization, and embedding are versioned derived processes.

### Completeness is measurable

"Download all" must mean that OpenDiscourse creates an explicit discovery manifest, processes every eligible item, records terminal failures, and produces a reconciliation report. It must never be an unbounded loop with no proof of coverage.

### Source fidelity over forced uniformity

OpenDiscourse will normalize stable cross-source concepts, but it will not erase source-specific fields or invent misleading universal schemas. Raw and canonical representations coexist.

### Provenance everywhere

Every fact, relationship, extracted passage, embedding, and derived metric must be traceable to source records and artifacts.

### Identity resolution is foundational

People, committees, offices, organizations, districts, and measures frequently use different identifiers across systems. OpenDiscourse will model identifiers, aliases, match evidence, and merge history as first-class data.

### Public-interest analysis must remain auditable

Derived conclusions about political behavior or policy impact must expose methodology, time windows, evidence, uncertainty, and known limitations.

## Initial scope

The first major source families are:

1. OpenStates / Plural Policy bulk legislative data.
2. GovInfo bulk collections and metadata.
3. Congress.gov API records for reconciliation and hydration.
4. Federal Election Commission bulk files and API data.
5. House and Senate financial disclosures and periodic transaction reports.
6. Census, ACS, TIGER/Line, and district geography.
7. FRED and related public economic series.

Later adapters may include DOJ, federal courts, agency enforcement data, lobbying disclosures, procurement, grants, crime statistics, state campaign finance, and other public-interest collections.

## Non-goals for the initial platform

- A polished consumer web application before acquisition and provenance are reliable.
- A single universal table for all government records.
- Blindly embedding every byte before extraction and deduplication are mature.
- Treating copied upstream repositories as the OpenDiscourse architecture.
- Claiming causal policy impact from simple temporal correlation.
- Providing unrestricted agent access to arbitrary SQL, credentials, or the host filesystem.

## Product surfaces

OpenDiscourse will eventually provide:

- `opendiscourse` Python package;
- `opendiscourse` command-line interface;
- PostgreSQL/PostGIS schemas and migrations;
- filesystem and object-storage backends;
- optional REST/GraphQL research API;
- optional TypeScript SDK;
- MCP server with safe catalog and research tools;
- reusable `SKILL.md` packages for Codex, Claude, and compatible agents.

## Success criteria

The first production milestone is achieved when a new user can clone the repository, configure storage and PostgreSQL, run documented commands, acquire one complete source through a resumable bulk workflow, verify coverage, and query normalized records with full lineage back to immutable artifacts.

## Governance of legacy material

The current repository contains cloned upstream repositories, experiments, datasets, and skill packs. These are valuable references, but they are not the new application core.

They will be:

- preserved on the existing history and an archival tag;
- cataloged with origin, purpose, and license notes;
- moved outside the first-party package boundary when practical;
- consulted for endpoint behavior and reusable ideas;
- integrated only through explicit OpenDiscourse contracts.
