# Data Pipelines, Models, and Haystack Strategy

## Goal Description
You raised excellent questions about how to structure our ingestion pipelines, how to track historical changes to bills, what orchestration frameworks to use for portability, and crucially, what 2026 state-of-the-art embedding models we should use for legal/political data.

This plan addresses all of your questions, establishes the blueprint for the Congress data model, and outlines our path forward for building out the remaining data scrapers.

## Open Questions & Framework Recommendations

> [!IMPORTANT] 
> Please review the three major architectural recommendations below (Embedding Models, Pipeline Framework, and Haystack AI). Do you approve of adopting Voyage AI for embeddings, `dlt` for pipeline orchestration, and Haystack for our RAG layer?

### 1. State-of-the-Art Embedding Models (2026)
You are completely right—general-purpose `all-MiniLM` is wildly outdated for complex legal dimensions. In 2026, the **Massive Legal Embedding Benchmark (MLEB)** is the gold standard for evaluating models on caselaw, bills, and regulations. 

**My Recommendations:**
- **Voyage 3 Large (or `voyage-law-2`)**: Voyage AI has dominated the legal embedding space. Their models support 32k context windows (crucial for long bills) and capture the exact nuance of political/legal text.
- **Kanon 2 Embedder**: Currently #1 on the 2026 MLEB leaderboard. 
- **Qwen3-Embedding-8B**: The best open-weights model available if you want to run embeddings entirely locally without API costs.

### 2. Portable Python Data Pipelines
You asked for a framework to encode Python ingestion pipelines and make them reusable and portable.
**My Recommendation:** **`dlt` (Data Load Tool)**
`dlt` is an open-source library that turns any Python script into a robust, portable data pipeline. It automatically handles schema inference, typing, chunking, and loading directly into Postgres or Qdrant. It is completely portable and can be run inside Docker, Airflow, or triggered by our LangGraph agents.

### 3. Haystack AI
You asked if we should use Haystack AI. 
**My Recommendation:** **Yes, absolutely.**
While LangGraph is perfect for our *Agent Routing* (deciding *when* to scrape data), **Haystack 2.0** is the industry standard for *Document Retrieval (RAG)*. It has native, highly-optimized integrations for Qdrant, Pgvector, and reranking models. We should use Haystack to build the retrieval pipelines that our agents will use to query the bills and financial data.

---

## Proposed Data Models (Congress)

Based on the `congress/INVENTORY.md` and standard GovInfo data structures, we will extract and ingest the following relational and semantic models:

### 1. Legislators (`congress/congress-legislators/`)
- **Format:** YAML -> Postgres
- **Data:** Bioguide ID, Name, Party, State, Social Media, Term History.
- **Goal:** This is the "Primary Key" table. All bills, votes, and financial trades will link back to a `Bioguide ID`.

### 2. Bills & Changes (`congress/bulk-data/BILLSTATUS`)
- **Format:** XML -> `dlt` -> Qdrant / Postgres
- **Data:** Bill ID, Official Title, Cosponsors, Committees.
- **Tracking Changes:** GovInfo XML includes `<actions>` and `<amendments>`. We will extract these as a time-series ledger in Postgres, while embedding the *full text* of the bill versions into Qdrant using Voyage AI.

### 3. Votes (`congress/congress-data/`)
- **Format:** JSON -> Postgres
- **Data:** Roll call votes mapped to the Bill ID and the Legislator's Bioguide ID.

---

## Verification Plan & Next Steps

If you approve of the recommendations above, I will execute the following:
1. **Update `qdrant_search.py` and `db_client.py`** to implement the new Voyage AI or Qwen3 embedding model.
2. **Install `dlt` and `haystack-ai`** into your `pyproject.toml`.
3. **Build the `legislators` ingestion pipeline** using `dlt` to parse the YAML files in `congress/congress-legislators/` and cleanly dump them into your local Postgres database.
