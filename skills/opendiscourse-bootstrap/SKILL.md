---
name: opendiscourse-bootstrap
description: Bootstrap or extend the OpenDiscourse government-data platform using its architecture, ingestion contracts, configuration rules, and quality gates.
version: 0.1.0
license: MIT
compatibility:
  - codex
  - claude
  - cline
  - cursor
metadata:
  project: opendiscourse
  namespace: opendiscourse
  category: data-engineering
---

# OpenDiscourse Bootstrap

## Use this skill when

- creating the clean OpenDiscourse package foundation;
- adding or reviewing a government-data source adapter;
- implementing manifests, artifact storage, checkpoints, extraction, normalization, lineage, or reconciliation;
- adding CLI, API, MCP, PostgreSQL, PostGIS, full-text, or embedding capabilities;
- migrating useful behavior from a legacy or upstream repository.

## Read first

1. `AGENTS.md`
2. `docs/PROJECT_CHARTER.md`
3. `docs/ARCHITECTURE.md`
4. `docs/ROADMAP.md`
5. `docs/SOURCE_CATALOG.md`

## Required behavior

- Use the `opendiscourse` namespace for new Python code.
- Keep domain contracts independent of concrete frameworks and infrastructure.
- Prefer authoritative bulk acquisition for historical data.
- Create a durable manifest before claiming complete acquisition.
- Preserve source-native bytes and metadata before transformation.
- Make operations idempotent, resumable, rate-aware, and observable.
- Capture lineage from canonical entities and search chunks back to raw records and artifacts.
- Use durable external identifiers; never use display names as universal identity keys.
- Add tests and user-facing documentation with implementation changes.

## Source-adapter workflow

For a new source:

1. Verify current official documentation and terms.
2. Create a source descriptor documenting datasets, formats, capabilities, authentication, limits, identifiers, and update semantics.
3. Implement discovery separately from fetching.
4. Persist discovered items into a manifest.
5. Fetch to immutable content-addressed storage.
6. Verify length, media type, archive integrity, and checksum where possible.
7. Extract source-native records without lossy normalization.
8. Normalize only stable cross-source concepts.
9. preserve field and entity lineage.
10. Reconcile discovered, fetched, extracted, normalized, failed, and excluded counts.
11. Add fixture tests, integration tests, CLI examples, and an operational runbook.

## Configuration rules

Use typed settings and nested environment variables:

```text
OPENDISCOURSE_DATABASE__DSN
OPENDISCOURSE_STORAGE__BACKEND
OPENDISCOURSE_STORAGE__ROOT
OPENDISCOURSE_<SOURCE>__API_KEY
```

Commit safe defaults and `.env.example`. Never commit real keys, passwords, tokens, DSNs containing credentials, or private storage URLs.

## Legacy integration rules

Upstream repositories may be used as documentation, optional executables, source-schema references, or licensed code sources. Do not make the OpenDiscourse core depend on their repository layouts.

When adopting code, record origin and license, isolate it behind an OpenDiscourse interface, minimize the imported surface, and add tests.

## Completion checklist

- [ ] Correct namespace and module boundary
- [ ] Typed public contracts
- [ ] Validated settings
- [ ] Durable manifest/checkpoint state
- [ ] Immutable artifact and checksum handling
- [ ] Bounded concurrency and retry policy
- [ ] Structured logs without secrets
- [ ] Raw/source-native preservation
- [ ] Identity and lineage behavior
- [ ] Reconciliation report
- [ ] Unit/integration tests
- [ ] CLI or API documentation
- [ ] Operational limitations documented

## Avoid

- one-off downloader scripts with no state;
- hidden global configuration;
- arbitrary SQL exposed to agents;
- silent field loss;
- name-only entity joins;
- unbounded concurrency;
- embedding duplicate or unversioned text;
- describing scaffolds as complete implementations.
