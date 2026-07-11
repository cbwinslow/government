# OpenDiscourse Architecture

## System shape

OpenDiscourse is a modular ingestion and research platform built around stable domain contracts and replaceable adapters.

```text
CLI / API / MCP / SDK
         |
application services and orchestration
         |
domain models and ports
   /          |           \
source     persistence    storage
adapters     adapters     adapters
   \          |           /
 HTTP, PostgreSQL, filesystem, S3/R2/MinIO
```

## First-party namespace

All new Python code uses the `opendiscourse` namespace:

```text
src/opendiscourse/
├── cli/
├── config/
├── domain/
├── application/
├── catalog/
├── ingestion/
├── storage/
├── database/
├── extraction/
├── normalization/
├── identity/
├── lineage/
├── search/
├── observability/
└── sources/
```

## Core ingestion lifecycle

```text
describe
  -> discover
  -> create manifest
  -> plan
  -> fetch
  -> verify bytes
  -> extract
  -> normalize
  -> resolve identities
  -> load/index
  -> reconcile
```

Every phase must be independently restartable. Phase state belongs in PostgreSQL, not only in process memory.

## Source adapters

A source adapter translates an external system into OpenDiscourse domain records. It owns source-specific URL construction, discovery rules, pagination, authentication, rate-limit metadata, response interpretation, and source identifiers.

It does not own global scheduling, storage policy, database transaction policy, embedding policy, or CLI rendering.

Illustrative contract:

```python
class SourceAdapter(Protocol):
    source_id: str

    async def describe(self) -> SourceDescriptor: ...
    async def discover(self, request: DiscoveryRequest) -> AsyncIterator[RemoteAsset]: ...
    async def fetch(self, asset: RemoteAsset) -> FetchResult: ...
    async def extract(self, artifact: Artifact) -> AsyncIterator[RawRecord]: ...
    async def reconcile(self, run_id: UUID) -> ReconciliationReport: ...
```

Normalization should be implemented as separate source-aware transformers so raw extraction remains reusable.

## Artifact storage

Artifacts are immutable and content-addressed by SHA-256. Human-readable source paths are catalog metadata or links, not the canonical byte identity.

```text
data/
├── objects/sha256/ab/cd/<hash>
├── manifests/
├── extracted/
├── normalized/
├── quarantine/
├── exports/
└── indexes/
```

Required artifact metadata includes source, dataset, remote identifier, URL, retrieval time, source-modified time, media type, byte length, hash, ETag when present, license metadata, run ID, and derivation relationships.

Storage backends should implement a common interface supporting local filesystems first and S3-compatible object stores later.

## PostgreSQL schemas

```text
catalog   source, dataset, artifact, artifact relation, license
 ingest   run, task, manifest, checkpoint, request, error, dead letter
 raw      immutable source-native records and extraction metadata
 core     stable normalized entities and relationships
identity  external identifiers, aliases, match evidence, merge events
lineage   source links, transformations, field provenance
search    document versions, chunks, embeddings, full-text metadata
 graph    optional relationship projections
 mart     analytical and profile-oriented views
```

Source-native payloads remain available in `raw` or the artifact lake. Canonical tables must not be used as a substitute for preserving source fidelity.

## Configuration

Use `pydantic-settings` or an equivalent typed validation layer. Configuration precedence is defaults, project config, environment variables, then explicit CLI overrides.

Secrets belong in environment variables or a secret manager. Non-secret source metadata and operational defaults belong in TOML/YAML.

## Concurrency and reliability

- bounded concurrency per source and endpoint class;
- retry only transient network, 429, and selected 5xx failures;
- exponential backoff with jitter;
- durable checkpoints and attempt counters;
- checksum-based idempotency;
- dead-letter terminal state after configurable attempts;
- structured logs with run, task, source, dataset, and artifact identifiers;
- graceful shutdown that leaves work resumable.

## Identity resolution

External identifiers are authoritative evidence. Name, date, geography, office, and affiliation are matching signals rather than universal keys.

Automated matches require scores and evidence. Ambiguous matches remain unresolved. Merges are reversible and recorded as events.

## Search and embeddings

Search indexing begins only after extraction, versioning, and deduplication. Each chunk records document version, offsets or page references, chunking strategy, input checksum, embedding model, model revision, dimensions, and creation time.

PostgreSQL full-text search is the initial lexical search layer. `pgvector` may be used initially for embeddings, with a separate vector service optional at scale.

## MCP boundary

The OpenDiscourse MCP server is read-only by default. It exposes catalog, lineage, source status, artifact text, and research queries. Mutating tools such as starting a sync require explicit enablement and authorization. Arbitrary SQL and unrestricted filesystem tools are prohibited.

## Legacy repositories

Cloned upstream repositories are reference material and optional build/download dependencies. They are not imported directly by core modules. Useful behavior is wrapped behind adapters or extracted with license attribution and tests.
