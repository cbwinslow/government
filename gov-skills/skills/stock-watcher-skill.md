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
