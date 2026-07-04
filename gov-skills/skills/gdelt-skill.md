---
name: gdelt-skill
description: Ingest global news events from the GDELT Project to track politician statements ("Words") and controversies ("Actions"). Use for running the GDELT ingestion pipeline, entity extraction via LLM, and inserting results into the opendiscourse database.
category: integration-documentation
risk: low
source: community
tags: [gdelt, news, ingestion, entity-extraction, llm, ner, opendiscourse, sentiment]
tools: [python, openrouter, postgresql, sqlalchemy, requests, csv]
allowed-tools: Read Write Edit Bash Glob Grep
compatibility: claude-code
---

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

## When to Use
- Running the GDELT ingestion pipeline
- Extracting politician entities from news text
- Inserting news events into opendiscourse database

## Limitations
- Requires gdelt_ingestion_pipeline.py script
- LLM-based NER via OpenRouter
- Depends on congress-legislators for identity mapping
- GDELT 2.0 API/CSV access needed
