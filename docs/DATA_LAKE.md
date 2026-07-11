# OpenDiscourse Data Lake

## Purpose

The data lake preserves source artifacts before any lossy transformation and provides deterministic storage for reproducible extraction, normalization, search, and research.

## Initial local layout

```text
data/
├── objects/sha256/ab/cd/<sha256>
├── manifests/
├── extracted/
├── normalized/
├── quarantine/
├── exports/
└── indexes/
```

`objects/sha256` is the canonical byte store. Human-readable source paths belong in catalog metadata rather than determining byte identity.

## Required artifact metadata

Each cataloged artifact should eventually include:

- source and dataset identifiers;
- remote identifier and source URL;
- retrieval and source-modified timestamps;
- media type, byte length, SHA-256, ETag, and upstream checksum when available;
- ingestion run and manifest identifiers;
- license and attribution metadata;
- parent, child, representation, and derivation relationships;
- extraction, quarantine, and verification status.

## Storage rules

- Writes are streamed to temporary files and finalized atomically.
- Identical bytes are stored once and may have many source references.
- Raw bytes are immutable.
- Derived content receives its own checksum and lineage edge.
- Runtime data is not committed to Git.
- Filesystem storage is the first backend; S3-compatible backends will implement the same artifact-store contract.
