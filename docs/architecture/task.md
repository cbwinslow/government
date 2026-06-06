# Execution Tasks: Pipelines, Haystack & Congress Data

- `[x]` **Phase 1: Environment & Dependencies**
  - `[x]` Install `dlt` and `haystack-ai` via `uv`
  - `[x]` Configure `dlt` secrets for Postgres (`secrets.toml`)

- `[x]` **Phase 2: Congress Legislator Pipeline (`dlt`)**
  - `[x]` Write `scripts/ingest_legislators.py` using `dlt`
  - `[x]` Parse `legislators-current.yaml` and `legislators-historical.yaml`
  - `[x]` Execute the pipeline to load into Postgres

- `[x]` **Phase 3: Haystack AI Integration (Preparation)**
  - `[x]` Set up the base Haystack DocumentStore script for Qdrant/Postgres
  - `[x]` Validate the pipeline's data in the database
