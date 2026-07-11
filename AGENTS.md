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

- Prefer authoritative bulk data over APIs for historical backfills.
- Every ingestion must be idempotent, restartable, observable, and independently verifiable.
- Never mark a dataset complete without discovery and reconciliation evidence.
- Preserve raw bytes before parsing or normalization.
- Capture provenance, source URLs, timestamps, checksums, media types, and run identifiers.
- Never join people or organizations by display name alone.
- Do not force source-specific records into misleading canonical tables.
- Keep source adapters isolated from storage, orchestration, normalization, and serving layers.
- Never commit secrets or large downloaded datasets.
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

A source adapter owns source-specific discovery and interpretation. It must not own global orchestration, storage policy, database transaction policy, or embedding policy.

Expected lifecycle:

```text
describe -> discover -> plan -> download -> verify -> extract -> normalize -> reconcile
```

Each adapter must declare:

- source identifier;
- datasets and formats;
- bulk, API, feed, sitemap, archive, or database-dump capabilities;
- authentication requirements;
- rate limits and retry policy;
- durable source identifiers;
- checkpoint strategy;
- completeness and reconciliation strategy;
- license, terms, and attribution metadata.

## Data safety

- Raw artifacts are immutable.
- Derived representations are versioned and reproducible.
- A content hash identifies bytes; a source identifier identifies the remote record.
- Source deletions or corrections become catalog events, not silent local destruction.
- Malformed or suspicious artifacts are quarantined rather than discarded.
- Temporary files must be finalized atomically or removed after failure.

## Configuration

Use validated settings with this precedence:

1. packaged safe defaults;
2. project TOML or YAML configuration;
3. environment variables;
4. explicit CLI overrides.

Use nested environment names such as:

```text
OPENDISCOURSE_DATABASE__DSN
OPENDISCOURSE_STORAGE__ROOT
OPENDISCOURSE_SOURCES__GOVINFO_API_KEY
```

Commit `.env.example`; never commit `.env`. Commands that display configuration must redact credentials, DSNs, tokens, and API keys.

## Repository policy

The cloned repositories and datasets in the original workspace are legacy or upstream reference assets. Do not couple new OpenDiscourse code to their internal layouts.

When adopting useful upstream behavior:

1. record the repository URL, revision, license, and relevant paths;
2. extract the smallest reusable concept;
3. rewrite or wrap it behind an OpenDiscourse contract;
4. add fixtures and tests;
5. avoid vendoring an entire upstream repository into the core package;
6. retain attribution and comply with license terms.

## Definition of done for a source

A source implementation is not complete until it has:

- a source descriptor and configuration schema;
- complete discovery for its declared scope;
- durable manifest and checkpoint support;
- deterministic artifact storage with checksums;
- bounded concurrency, retries, and rate-limit behavior;
- extraction tests using committed fixtures;
- normalization and lineage tests where applicable;
- a reconciliation report;
- CLI documentation and an operational runbook;
- explicit license and data-terms notes.

## Agent workflow

Before editing:

1. Read `docs/PROJECT_CHARTER.md`.
2. Read `docs/ARCHITECTURE.md`.
3. Read `docs/SOURCE_CATALOG.md` and the relevant source entry.
4. Check for a relevant `skills/*/SKILL.md`.
5. State assumptions in the PR or commit description.

While editing:

- Keep changes focused and independently reviewable.
- Prefer typed interfaces and small composable components.
- Do not present scaffolds or placeholders as complete implementations.
- Validate inputs and fail safely.
- Log structured context without leaking credentials.
- Retain enough durable state to resume after interruption.
- Preserve backward compatibility unless an intentional breaking change is documented.

Before finishing:

- Run Ruff, formatting, strict type checking, and relevant tests.
- Verify documentation and command examples match actual behavior.
- Record cross-cutting decisions under `docs/decisions/`.
- List remaining risks, unsupported scopes, and data-completeness limits explicitly.
