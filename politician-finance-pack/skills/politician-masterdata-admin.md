# Skill: politician-masterdata-admin

## Purpose
Use this skill to design and maintain the canonical politician/person/member database across House, Senate, Congress.gov, GovInfo, FEC, disclosure systems, and downstream enrichment layers.

## Goals
1. Build a durable person identity model.
2. Track office service, candidacies, committees, party affiliation, geography, and external identifiers.
3. Link politicians to campaign finance, disclosures, transactions, assets, liabilities, gifts, travel, and legislative activity.
4. Support both relational analytics and RAG-style retrieval.

## Core entity model
- `person`: canonical individual.
- `person_name_variant`: alternate names and filing aliases.
- `member_term`: office service periods by chamber/congress/district/state.
- `candidate_cycle`: election-cycle candidacy view.
- `committee_affiliation`: official committees/subcommittees.
- `person_identifier`: bioguide, fec candidate id, opensecrets id, wikidata id, govinfo package links, clerk disclosure ids, senate efd ids where available.
- `organization`: campaign committees, leadership PACs, outside groups, employers, issuers.
- `relationship_edge`: spouse, dependent, employer, committee role, beneficial ownership, board membership.

## Identity resolution rules
- Prefer explicit upstream identifiers over fuzzy matching.
- Maintain source-scoped identity bridges.
- Store confidence scores and merge rationale for fuzzy candidate/person matches.
- Never overwrite raw source names; map them to canonical identities.

## Database guidance
Use schemas:
- `master` for person and org identity.
- `leg` for legislative service and actions.
- `finance` for campaign finance.
- `disclosure` for personal financial disclosures and transactions.
- `rag` for chunks, embeddings, retrieval metadata.
- `ingest` and `raw` for operational ingestion.

## Deliverables
- canonical DDL
- merge/audit SQL
- identity resolution jobs
- materialized views for politician profiles
- API and MCP tool definitions for profile lookup
