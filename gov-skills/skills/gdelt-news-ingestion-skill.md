# Skill: gdelt-news-ingestion

## Purpose
Use this skill when building or operating the GDELT Project news ingestion pipeline. GDELT monitors global news media and provides the primary "Words" feed for the Honesty Engine — extracting what politicians say in public from news articles, press releases, and broadcasts.

## Source facts to honor
- GDELT 2.0 provides near-real-time global news event and sentiment data.
- GDELT API queries use a SQL-like syntax via the GDELT Translingual API or the GDELT 2.0 API.
- The GDELT Global Knowledge Graph (GKG) contains themes, locations, organizations, persons, and counts.
- GDELT updates are published every 15 minutes.
- Free tier has rate limits; respect them with backoff.

## Recommended pipeline

### 1. Query construction
Target queries should be politician-specific. Examples:
```
# Find articles mentioning a specific politician near their state
SELECT * FROM gdeltv2 WHERE domainlang='eng' AND (title LIKE '%Nancy Pelosi%' OR content LIKE '%Pelosi%')

# Find articles about a specific topic + politician
SELECT * FROM gdeltv2 WHERE (themes LIKE '%TAX_REFORM%') AND (persons LIKE '%John Smith%')
```

### 2. Fetch and filter
- Fetch article metadata via GDELT 2.0 API or GDELT BigQuery export.
- Filter for relevance: politician's name in title/lead paragraph, topic alignment.
- Deduplicate by source URL — GDELT can return multiple entries for the same article.

### 3. Extract "Words"
For each relevant article:
1. Fetch the full article text (use newspaper3k, readability, or direct API).
2. Extract quotes attributed to the politician.
3. Classify the issue area (use LLM or keyword mapping).
4. Store with: `politician_id`, `source_url`, `publication_date`, `quote_text`, `issue_category`, `sentiment_score`, `source_bias_rating`.

### 4. Feed to Honesty Engine
Articles should be fed into `words_context` for the Honesty Engine:
```python
words_context = [
    f"[{article['publication_date']}] On {article['issue_category']}, {quote_text}",
    ...
]
```

## Storage concerns
- Deduplicate by `politician_id` + `source_url` + `quote_text`
- Store raw GDELT event records for reprocessing.
- Maintain a cursor by `last_seen_date` per politician.
- Re-ingest at most once per 24h per politician to avoid spamming sources.

## Quality warnings
- GDELT includes low-quality sources. Filter by `domainlang`, domain authority, and source type.
- Translated content may lose nuance. Flag auto-translated articles for human review.
- Opinion pieces are not news — consider filtering opinion domains unless specifically tracking public narrative.

## Prompting template
- "Set up a GDELT ingestion pipeline for all members of the House Financial Services Committee. Extract quotes about banking regulation and feed them into the Honesty Engine."
- "Backfill GDELT mentions for Senator X over the last 90 days. Group quotes by issue category."
- "Monitor GDELT in near-real-time for new mentions of the 10 most active senators this week."
- "Cross-reference GDELT extracted quotes with Congress.gov voting records for Representative Y."