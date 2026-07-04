---
name: openstates-ingestion-skill
description: Pull state-level legislator data, bills, votes, and misconduct records from the openstates-monorepo. Use for ingesting state legislative data into the opendiscourse database with master identity mapping across federal and state systems.
category: integration-documentation
risk: low
source: community
tags: [openstates, state-legislature, bills, votes, legislators, misconduct, identity-mapping]
tools: [python, postgresql, sqlalchemy, openstates-scrapers, poetry, uv]
allowed-tools: Read Write Edit Bash Glob Grep
compatibility: claude-code
---

# OpenStates Monorepo Ingestion Skill

## Overview
This skill instructs agents on how to pull state-level legislator data and misconduct records from the `openstates-monorepo`.

## Repositories & Execution Steps

### 1. State Legislators (Master Identity Mapping)
- **Directory:** `openstates-monorepo/people/`
- **Action:** Agents must parse the CSV/JSON dumps of state legislators and insert them into the `opendiscourse` database's `Politician` table. Ensure you capture the `openstates_id` so we can track their progression if they move to federal office.

### 2. State Bills & Votes
- **Directory:** `openstates-monorepo/openstates-scrapers/`
- **Action:** Agents can run individual state scrapers (e.g., `uv run scraper_name`) to gather localized "Actions" (votes, sponsored bills).

### 3. Misconduct Database
- **Directory:** `openstates-monorepo/misconduct/`
- **Action:** Extract any ethics violations, arrests, or censures for legislators. Insert these into the database as highly negatively-weighted `Actions` for the Honesty Scoring engine to evaluate.

## When to Use
- Ingesting state legislator data for master identity mapping
- Scraping state bills and votes for Actions database
- Importing misconduct records for negative weighting in Honesty Engine
- Cross-referencing state and federal politician identities

## Limitations
- Requires openstates-monorepo cloned locally
- Scrapers use Poetry/uv for dependency management
- Rate limits vary by state website (SCRAPELIB_RPM setting)
- Historical sessions may be deprecated (check `active` flag)
- California requires MySQL for some data
