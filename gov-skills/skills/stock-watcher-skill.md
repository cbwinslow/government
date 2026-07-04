---
name: stock-watcher-skill
description: Ingest pre-compiled structured JSON data containing stock trades from House, Senate, and Executive branch members. Use for loading Senate (2012-2020) and Congress/Executive (2023-2026) trade data, mapping to Master Identities, and inserting as financial Actions.
category: integration-documentation
risk: low
source: community
tags: [stock-trades, financial-disclosures, senate, congress, json, master-identity, actions]
tools: [python, json, postgresql, sqlalchemy, vector-index]
allowed-tools: Read Write Edit Bash Glob Grep
compatibility: claude-code
---

# Stock Watcher Ingestion Skill

## Overview
This skill instructs agents on how to ingest the pre-compiled, structured JSON data containing thousands of stock trades from House, Senate, and Executive branch members. 

## Sources
1. **Senate Data (2012-2020):** `/home/cbwinslow/workspace/government/financial-disclosures/senate-stock-watcher-data/aggregate/all_transactions.json`
2. **Congress/Executive Data (2023-2026):** `/home/cbwinslow/workspace/government/financial-disclosures/congress-trading-monitor/public/data/trades.json`

## Execution Steps

### 1. Load the JSON Data
Parse both JSON files. They contain arrays of objects mapping individual stock transactions.

### 2. Map to Master Identities
For each trade, identify the politician:
- Use the `first_name` and `last_name` from the Senate data, or `filer_name` from the Congress data.
- Query the `opendiscourse` database or the vector index to resolve this name to the Master Identity UUID (derived from `congress-legislators`).

### 3. Insert as Financial Actions
Transform each trade into an `Action` object for the database:
- `type`: "financial_trade"
- `amount`: Parse the dollar range (e.g., "$1,001 - $15,000")
- `ticker`: Extract the stock ticker
- `transaction_date`: Normalize to ISO-8601 (YYYY-MM-DD).

### 4. Note on Gaps
Be aware that there is a gap in these datasets between 2021-2023. This gap is specifically filled by the `financial-disclosures-skill.md` which utilizes direct PDF OCR scraping for the missing years.

## When to Use
- Loading pre-compiled Senate stock trade data (2012-2020)
- Loading Congress/Executive trade data (2023-2026)
- Mapping trade filers to Master Identity UUIDs
- Filling financial Actions for Honesty Engine

## Limitations
- Data gap between 2021-2023 (use financial-disclosures-skill for PDF OCR)
- Requires opendiscourse database for identity resolution
- JSON structure may vary between sources
- Name matching requires fuzzy matching
