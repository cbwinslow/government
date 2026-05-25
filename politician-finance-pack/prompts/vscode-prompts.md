# VS Code prompts

## Prompt 1: Politician master DB
Design a production-ready PostgreSQL database for tracking politicians, members of Congress, candidates, committees, disclosures, transactions, campaign finance, and legislative activity. Use schemas `master`, `leg`, `finance`, `disclosure`, `rag`, `raw`, and `ingest`. Include canonical person and organization identity models, bridge tables, indexes, and data quality SQL.

## Prompt 2: Member identity resolver
Create a Python identity-resolution pipeline that links Congress.gov members, Bioguide identifiers, FEC candidate IDs, House/Senate disclosure filers, and campaign committees into canonical `master.person` and `master.organization` tables. Include confidence scores, merge logs, and review queues.

## Prompt 3: Campaign finance ingestor
Build an OpenFEC ingestion framework that pulls candidates, committees, committee histories, cycle summaries, filings, contributions, expenditures, and independent expenditures into PostgreSQL. Include pagination, retries, cycle partitioning, source URL tracking, and CLI commands.

## Prompt 4: Disclosure ingestor
Build a financial disclosure and PTR ingestion framework for House and Senate sources. Preserve raw PDFs/HTML, extract structured holdings and transactions, store parser confidence, and normalize assets, liabilities, gifts, travel, and income.

## Prompt 5: RAG layer
Create a LlamaIndex-based ingestion and retrieval layer for politicians and disclosures using PostgreSQL as source of truth, pgvector for embeddings, and optional Qdrant mirroring. Include chunking strategy, metadata extraction, re-embedding jobs, and filtered retrieval examples.

## Prompt 6: VS Code + MCP
Generate VS Code tasks, launch configs, `.env.example`, Docker Compose, and MCP server configs for politician tracking, OpenFEC ingestion, disclosure ingestion, and vector indexing.

## Prompt 7: Conflict analytics
Write SQL models and Python jobs that identify suspicious overlaps between trades, committee assignments, campaign donors, issuer relationships, and legislative activity. Include heuristic flags and feature tables for downstream ML/RAG.
