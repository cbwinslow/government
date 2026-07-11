# AGENTS.md

## Project

OpenDiscourse is a reusable, bulk-first government-data acquisition, preservation, normalization, search, and research platform.

The Python namespace is `opendiscourse`. All new first-party Python code belongs under `src/opendiscourse/`.

## Mission

Build a system that any user can clone, configure, and operate to:

1. Discover all publicly available records exposed by supported government sources.
2. Download complete bulk datasets and API collections with resumable manifests.
3. Preserve original artifacts without lossy transformation.
4. Normalize only genuinely shared concepts into stable canonical models.
5. Resolve identities across agencies and jurisdictions.
6. Support PostgreSQL/PostGIS analytics, full-text search, embeddings, and evidence-backed politician profiles.
7. Expose the platform through a CLI, Python API, optional TypeScript SDK, and MCP server.

## Non-negotiable engineering rules

- Prefer bulk data over APIs for historical backfills when an authoritative bulk source exists.
- Every ingestion must be idempotent, restartable, observable, and independently verifiable.
- Never mark a dataset complete unless discovery and reconciliation evidence supports that claim.
- Preserve raw bytes before parsing.
- Store provenance, source URLs, timestamps, checksums, media types, and ingestion-run identifiers.
- Never join people or organizations by display name alone.
- Do not force source-specific records into misleading canonical tables.
- Keep source adapters isolated from storage, orchestration, normalization, and serving layers.
- Secrets must never be committed.
- Avoid loading large downloaded datasets into Git; register them in the data catalog instead.
- Add or update tests whenever behavior changes.

## Architecture boundaries

New modules should follow this dependency direction:

```text
cli / api / mcp
        |
application services
        |
domain contracts
   /           \
source adapters storage adapters
        \     /
 infrastructure
```

Domain contracts must not import concrete HTTP clients, database drivers, CLI frameworks, or cloud SDKs.

## Source adapter contract

A source adapter is responsible for source-specific discovery and interpretation. It must not directly own global orchestration.

Expected lifecycle:

```text
describe -> discover -> plan -> fetch -> verify -> extract -> normalize -> reconcile
```

Each adapter must declare:

- source identifier
- datasets and supported formats
- bulk/API/feed/sitemap capabilities
- authentication requirements
- rate limits and retry policy
- durable source identifiers
- checkpoint strategy
- completeness/reconciliation strategy
- license or terms metadata

## Data safety

- Raw artifacts are immutable.
- Derived representations are versioned and reproducible.
- A content hash identifies bytes; a source identifier identifies the remote record.
- Deletions or corrections at the source become catalog events, not silent local destruction.
- Quarantine malformed or suspicious artifacts rather than discarding them.

## Configuration

Use validated settings with this precedence:

1. packaged safe defaults
2. project TOML/YAML configuration
3. environment variables
4. explicit CLI overrides

Use nested environment names such as:

```text
OPENDISCOURSE_DATABASE__DSN
OPENDISCOURSE_STORAGE__ROOT
OPENDISCOURSE_GOVINFO__API_KEY
```

Commit `.env.example`; never commit `.env`.

## Repository policy

The existing cloned repositories and datasets are legacy/reference assets. Do not couple new OpenDiscourse code to their internal layouts. When useful code is adopted:

1. document its origin and license;
2. extract the smallest reusable concept;
3. rewrite or wrap it behind an OpenDiscourse contract;
4. add tests;
5. avoid vendoring an entire upstream repository into the core package.

## Definition of done

A source implementation is not complete until it has:

- a source descriptor
- configuration schema
- discovery implementation
- resumable manifest support
- deterministic artifact paths
- checksums and metadata capture
- retry and rate-limit behavior
- extraction tests using fixtures
- normalization/lineage tests where applicable
- reconciliation report
- CLI documentation
- operational runbook

## Agent workflow

Before editing:

1. Read `docs/PROJECT_CHARTER.md`.
2. Read `docs/ARCHITECTURE.md`.
3. Read the relevant source catalog entry.
4. State assumptions in the PR or commit description.

While editing:

- Keep changes focused.
- Prefer typed interfaces and small composable components.
- Do not add placeholders presented as working implementations.
- Log structured context without leaking credentials.
- Fail safely and retain enough state to resume.

Before finishing:

- Run relevant tests and linters.
- Verify documentation and examples match actual commands.
- Record new architectural decisions in `docs/decisions/` when the change affects multiple modules.
- List remaining risks explicitly.
