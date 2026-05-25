# Skill: congressgov-ingestion-admin

## Purpose
Use this skill when building or maintaining pipelines for Congress.gov API ingestion, legislative entity normalization, database administration, and downstream analytical/search workloads.

## Platform facts you should honor
- Congress.gov API current version is v3.
- It returns XML or JSON.
- It requires an API key.
- Rate limit is 5,000 requests per hour.
- Default page size is 20 and max page size is 250.
- Coverage dates and estimated update times are published separately on Congress.gov.

## Primary goals
1. Pull legislative entities in a rate-aware and restartable way.
2. Model bills, amendments, members, committees, nominations, treaties, hearings, reports, and actions consistently.
3. Separate current snapshot tables from append-only event history.
4. Track pagination progress, endpoint lineage, and per-entity freshness.

## Recommended architecture
- Discovery/pull layer:
  - endpoint-specific crawlers with persisted offsets.
  - entity hydration jobs for detail endpoints.
  - change-monitor jobs aligned to endpoint coverage/update expectations.
- Landing layer:
  - raw JSON/XML payload store.
  - request audit tables.
- Normalize layer:
  - entity tables for bills, bill actions, sponsors, cosponsors, members, committees, nominations, amendments, treaties.
  - bridge tables for many-to-many relationships.
  - reference tables for congress sessions, chambers, bill types, action codes.
- Serving layer:
  - denormalized legislative activity marts.
  - search views for subject, sponsor, committee, and status.

## Data modeling guidance
Suggested schemas:
- `ingest` for runs, cursors, quotas, failures.
- `raw` for immutable response bodies.
- `leg` for normalized legislative entities.
- `mart` for analytics/search views.

Core patterns:
- use natural composite keys where Congress number + type + number are meaningful.
- model bill actions as append-only events.
- keep sponsor/cosponsor relationships versionable if source can change.
- attach source API URL and retrieved timestamp to every entity record.

## Rate-aware ingestion strategy
1. Maintain a shared quota ledger for the hour.
2. Use endpoint-level concurrency caps.
3. Pull list endpoints with `limit=250` where appropriate.
4. Persist `offset` checkpoints per endpoint and parameter set.
5. Fan out detail hydration jobs only after list records are durably stored.
6. Reconcile entity counts between list and detail jobs.

## Database admin tasks this skill should perform well
- create schema for legislative entities and bridge tables.
- tune indexes for sponsor/member/bill lookups.
- partition large action/event tables by congress or action date.
- generate upsert SQL and merge procedures.
- create monitoring queries for freshness, duplicates, and orphaned bridges.

## Recommended table families
- `leg.bill`
- `leg.bill_title`
- `leg.bill_action`
- `leg.bill_subject`
- `leg.bill_sponsor`
- `leg.bill_cosponsor`
- `leg.amendment`
- `leg.committee`
- `leg.member`
- `leg.nomination`
- `leg.treaty`
- `ingest.api_cursor`
- `ingest.api_request_log`
- `raw.congress_payload`

## Quality checks
Always run:
- pagination gap checks
- duplicate bill identity checks
- orphaned sponsors/cosponsors
- event chronology checks for bill actions
- freshness lag by entity family
- null rates on congress/chamber/type/number

## Prompting template for this skill
Use requests like:
- "Build a Congress.gov v3 ingestion pipeline into PostgreSQL with list/detail crawlers, offset checkpoints, and hourly quota controls."
- "Generate DDL and ingestion code for bills, bill actions, sponsors, and committees with append-only history and latest snapshots."
- "Create admin SQL to audit pagination gaps, duplicate bill keys, and stale entity families."
