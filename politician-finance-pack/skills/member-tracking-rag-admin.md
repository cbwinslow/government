# Skill: member-tracking-rag-admin

## Purpose
Use this skill when building a retrieval layer for politician profiles, disclosure documents, campaign finance records, and legislative activity using LlamaIndex plus pgvector and/or Qdrant.

## Retrieval architecture
- PostgreSQL remains source of truth.
- `pgvector` is preferred for embedding storage tightly coupled to relational joins.
- Qdrant is optional as a high-performance external vector store for hybrid search, filtered retrieval, and experimentation.
- LlamaIndex orchestrates ingestion pipelines, chunking, metadata extraction, and retrieval workflows.

## Recommended document families
- politician profile summaries
- annual disclosure filings
- PTR filings
- campaign finance filings and summaries
- legislative documents from GovInfo/Congress.gov
- committee reports and hearing records

## Chunk metadata requirements
Every chunk should carry:
- `source_system`
- `document_type`
- `person_id`
- `organization_id`
- `report_id`
- `filing_year`
- `congress`
- `cycle`
- `ticker`
- `date_start`
- `date_end`
- `url`
- `checksum`

## Embedding guidance
- use a single baseline embedding model first.
- keep chunk text and structured metadata separate.
- support deterministic re-embedding when parser version changes.
- write embeddings to `rag.embedding_chunk` in pgvector and optionally mirror into Qdrant collections.
