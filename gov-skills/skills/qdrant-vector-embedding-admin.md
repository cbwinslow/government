# Skill: qdrant-vector-embedding-admin

## Purpose
Use this skill when configuring Qdrant vector store, generating embeddings for legislative documents, bill text, politician profiles, or disclosure filings, and building semantic search across the government data corpus.

## Infrastructure facts to honor
- Qdrant runs at `http://localhost:6333` (configurable via `QDRANT_URL` in config/settings).
- The `scripts/qdrant_setup.py` script handles collection creation, embedding generation, and batch upload.
- Default embedding model is `all-MiniLM-L6-v2` (384 dimensions) for speed; production should use `BAAI/bge-large-en-v1.5` (1024 dimensions).
- `sentence-transformers` generates the embeddings; `qdrant-client` handles the store operations.
- Qdrant exposes REST API on 6333 and gRPC on 6334.
- Qdrant has a built-in dashboard at `http://localhost:6333/dashboard`.

## Core collections

| Collection | Purpose | Vector Size |
|-----------|---------|-------------|
| `congress_bills` | Bill text and metadata | 384 (default) |
| `politician_documents` | Profile descriptions, disclosures | 3072 (BGE-large) |

## Embedding pipeline

### 1. Collection setup
```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

client = QdrantClient(url="http://localhost:6333")
client.create_collection(
    collection_name="congress_bills",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)
```

### 2. Text preparation
Combine structured fields into searchable text. The existing pattern in `scripts/qdrant_setup.py` should be followed for each document type:

**Bills**: bill_id, official_title, bill_type, congress, status, summary text, subjects, sponsor name
**Politicians**: name, party, state, biography, committee assignments, issue positions
**Disclosures**: filing type, year, asset name, ticker, transaction type, amount range, filer name

### 3. Batch upload
Upload in batches of 100 points at a time. Each point must carry a rich payload so queries can return result details without a second lookup.

### 4. Query patterns
```python
# Semantic bill search
results = client.search(
    collection_name="congress_bills",
    query_vector=model.encode("climate change legislation carbon tax"),
    limit=20,
)

# Filtered search
results = client.search(
    collection_name="congress_bills",
    query_vector=model.encode("healthcare reform"),
    query_filter=Filter(must=[FieldCondition(key="congress", match=MatchValue(value=118))]),
    limit=10,
)
```

## Embedding model selection guide

| Use Case | Model | Dims | Speed | Quality |
|----------|-------|------|-------|---------|
| Dev/prototyping | `all-MiniLM-L6-v2` | 384 | Fast | Good |
| Production bills | `BAAI/bge-large-en-v1.5` | 1024 | Moderate | Excellent |
| Legal/financial docs | `BAAI/bge-base-en-v1.5` | 768 | Fast | Very Good |
| Multi-language | `intfloat/multilingual-e5-large` | 1024 | Slow | Best for mixed |

## Sync strategies
- **Full rebuild**: Drop collection, re-embed everything. Use when schema changes or model changes.
- **Incremental**: Query new/changed records by `updated_at`, embed only those, upsert by `id` in Qdrant.
- **Bulk data reset**: Use `scripts/qdrant_setup.py` when loading from `congress/congress-data/` bill data.

## Performance tuning
- Set `write_consistency_factor=1` during bulk loads, restore to `quorum` for production.
- Create payload indexes on filtered fields (congress, bill_type, status, sponsor_state).
- Use WAL for durability-critical collections.
- Monitor memory: Qdrant keeps vectors in memory for fast search.

## Prompting template
- "Rebuild the Qdrant `congress_bills` collection using the BGE-large embedding model instead of MiniLM."
- "Write an incremental sync job that finds new/changed bills and upserts their embeddings into Qdrant."
- "Create filtered semantic search queries for bills by congress number and topic."
- "Design a hybrid search over politician disclosures that combines Qdrant vector search with PostgreSQL metadata filtering."
- "Benchmark query latency between `all-MiniLM-L6-v2` and `BAAI/bge-large-en-v1.5` on 10,000 bills."