# GDELT Global News Ingestion Skill

## Overview
This skill instructs agents on how to ingest global news events from the GDELT Project. It allows us to track what politicians are saying in the news ("Words") and what controversies they are involved in ("Actions").

## Execution Steps

### 1. Execute the Pipeline
Run the salvaged `gdelt_ingestion_pipeline.py` script (originally from the `epstein-pipeline` directory). This script connects to the GDELT 2.0 API/CSV dumps.

### 2. Entity Extraction
The raw GDELT text contains unstructured names. Pass the relevant news snippets to the LLM engine via OpenRouter to perform Named Entity Recognition (NER).

### 3. Match and Insert
- Map the extracted entities to our Master Identity UUIDs (derived from the `congress-legislators` database).
- Insert the article URL, sentiment score (using GDELT Tone), and LLM context summary into the `opendiscourse` database.
