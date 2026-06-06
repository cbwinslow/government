# Honesty Engine / OpenDiscourse Prompts

## Prompt 1: Score a single politician
Run the Honesty Engine on {politician_name}. First, gather their recent "Words" (from GDELT news mentions, floor speeches, and social media) and their "Actions" (voting record, sponsored legislation, campaign finance, and financial disclosures). Feed both into the Honesty Engine scorer with use_fusion=True for the most accurate analysis. Return the consistency score, top discrepancies, and an overall summary.

## Prompt 2: Batch score a committee
Score all members of the {committee_name} committee using the Honesty Engine. For each member, assemble words_context from GDELT articles mentioning them in the last 90 days, and actions_context from their voting record in the current Congress plus their top campaign contributors. Return a ranked list by consistency_score (lowest first) with the top 3 discrepancies per politician.

## Prompt 3: Score trend over time
Track Honesty Engine scores for {politician_name} across the last 3 Congresses. For each Congress, gather their public statements and voting record for that period. Run the scorer separately per Congress, then compare: is their consistency score improving or declining, and on which specific issues? Generate a time-series report.

## Prompt 4: Discrepancy deep dive
For {politician_name}, find the highest-severity discrepancies (severity 8+/10) across all issue areas. For each discrepancy, gather the exact quote or statement (the "Word"), the contradicting vote or action (the "Action"), and explain the gap in detail. Flag any discrepancies where the politician took money from an industry they claimed to regulate strictly.

## Prompt 5: Pipeline orchestration
Set up the full Honesty Engine data pipeline for fresh ingestion: (1) seed politician identities from OpenStates YAML data, (2) sync Congress.gov members and voting records, (3) pull OpenSecrets campaign finance data, (4) fetch GDELT news mentions for each politician, (5) run the Honesty Engine scorer on all active members, (6) store results and update the dashboard API. Schedule this as a weekly cron job.

## Prompt 6: GDELT + Congress cross-reference
For {politician_name}, extract all GDELT articles from the last 30 days that mention a specific policy area ({policy_area}). Extract the politician's stated position from the article. Then find their actual votes on related legislation in Congress.gov. Feed both into the Honesty Engine and determine if their actions match their stated position.

## Prompt 7: Network influence analysis
For {politician_name}, map their network: (1) top campaign contributors from OpenSecrets, (2) committee assignments and leadership roles, (3) co-sponsored bills and their co-sponsors, (4) financial disclosure assets and transactions. Use the Honesty Engine to identify conflicts of interest where a contributor's industry intersects with the politician's committee purview. Generate a network graph.

## Prompt 8: Entity resolution batch
Process all politicians from the OpenStates people data directory and upsert them into the Master Identity table. For each person, extract bioguide_id, fec_id, opensecrets_id, and votesmart_id from their YAML. Log any records where external IDs are missing or where the name suggests a possible duplicate (similar names, same state and party). Report the total upserted, missing IDs by type, and suspected duplicates.

## Prompt 9: Qdrant semantic bill search
Build a semantic search pipeline over congressional bills: (1) load all bill data.json files from congress/congress-data/, (2) prepare text by combining official_title, summary, and subjects, (3) generate embeddings using BAAI/bge-base-en-v1.5, (4) upsert into Qdrant congress_bills collection with rich payloads, (5) create a CLI tool that accepts a natural language query and returns the top 20 semantically similar bills with their metadata.

## Prompt 10: Full infrastructure bootstrap
Set up the complete OpenDiscourse infrastructure from scratch: (1) docker-compose up for PostgreSQL, Qdrant, Redis, (2) create the PostgreSQL database and all schemas (public, master, leg, finance, disclosure, rag, ingest, raw, core, mart), (3) run Politician table migrations, (4) seed identities from OpenStates YAML, (5) create Qdrant collections for congress_bills and politician_documents, (6) verify all services are connected and healthy, (7) output a table of service status, row counts, and collection sizes.