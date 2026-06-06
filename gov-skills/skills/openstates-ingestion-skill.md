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
