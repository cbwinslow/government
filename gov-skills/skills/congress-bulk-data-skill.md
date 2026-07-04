---
name: congress-bulk-data-skill
description: Synchronize bulk data from unitedstates/congress community scrapers including bills, amendments, roll-call votes, and legislator demographics. Use for keeping local congress-data directory current with federal legislative data.
category: integration-documentation
risk: low
source: community
tags: [congress, bulk-data, bills, votes, legislators, govinfo, sync, unitedstates]
tools: [python, uv, dlt, llamaindex, postgresql, sqlalchemy, yaml, xml]
allowed-tools: Read Write Edit Bash Glob Grep
compatibility: claude-code
---

# Congress & GovInfo Bulk Data Sync

## Overview
This skill instructs agents on how to synchronize bulk data from the `unitedstates/congress` community scrapers. It ensures we have the latest bills, amendments, and roll-call votes loaded into our local `congress-data` directory.

## Constants
- **Target Congresses:** `[106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119]`
- **Workspace Directory:** `/home/cbwinslow/workspace/government/congress/congress`

## Execution Steps

### 1. Configuration & Pipelines
The execution logic is entirely config-driven via `config/pipelines.yaml`. 
Agents should **not** hardcode commands or variables. You must:
1. Parse `config/pipelines.yaml` to verify the ingestion is enabled.
2. Rely on the specified framework (`dlt` for YAML/JSON data, `llamaindex` for complex hierarchical XML/PDF parsing) to execute the sync.

```bash
cd /home/cbwinslow/workspace/government
# If Congress pipelines are enabled in config/pipelines.yaml, you may trigger the scripts directly:
uv run python scripts/ingest_legislators.py
uv run python scripts/ingest_bills_llamaindex.py
```

### 2. Sync GovInfo Bill Status
Run the following command to fetch the latest bulk XML updates from GovInfo.

```bash
uv run ./run govinfo --bulkdata=BILLSTATUS
```

### 3. Sync Bills
Iterate through the target congresses (from 106 to 119) and run the bill parser:

```bash
uv run ./run bills --congress=119
```

### 4. Sync Roll Call Votes
Iterate through the target congresses and run the votes scraper:

```bash
uv run ./run votes --congress=119
```

### 5. Update Legislators Data
Switch to the `congress-legislators` directory to keep demographic data fresh:

```bash
cd /home/cbwinslow/workspace/government/congress/congress-legislators
# Update contact information and demographics
uv run python scripts/house_contacts.py
uv run python scripts/senate_contacts.py
```

## When to Use
- Syncing bulk congressional data from unitedstates/congress
- Updating local congress-data directory with latest bills/votes
- Refreshing legislator contact information and demographics
- Running config-driven ingestion pipelines

## Limitations
- Requires config/pipelines.yaml with enabled pipelines
- Target congresses hardcoded (106-119)
- GovInfo bulk data requires API key
- Uses uv for Python execution
- Separate scripts for bills, votes, legislators
