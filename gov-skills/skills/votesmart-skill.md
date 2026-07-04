---
name: votesmart-skill
description: Ingest Interest Group Ratings (NRA, ACLU, Planned Parenthood) from Vote Smart API to build quantitative ideological baselines for politicians. Use for fetching candidate ratings, mapping Vote Smart IDs to Master Identity, and inserting as Words/ideological priors for Honesty Engine.
category: integration-documentation
risk: low
source: community
tags: [votesmart, interest-group-ratings, ideology, nra, aclu, planned-parenthood, candidate-ratings]
tools: [python, requests, postgresql, sqlalchemy, yaml]
allowed-tools: Read Write Edit Bash Glob Grep
compatibility: claude-code
---

# Vote Smart API Ingestion Skill

## Overview
This skill instructs agents on how to ingest Interest Group Ratings (NRA, ACLU, Planned Parenthood) from Vote Smart to build a quantitative ideological baseline for politicians.

## Setup
- **API Endpoint:** `http://api.votesmart.org/`
- **Authentication:** Obtain the API key from `.env` under `VOTESMART_API_KEY`.

## Execution Steps

### 1. Map Candidate ID
Vote Smart uses a unique `candidateId`. This is listed as `votesmart` in our Master Identity YAML (`congress-legislators/legislators-current.yaml`).

### 2. Fetch Interest Group Ratings
Use the `Rating.getCandidateRating` method.
- **Endpoint:** `Rating.getCandidateRating?candidateId=[ID]&key=[KEY]`
- **Goal:** Extract ratings (0-100%) from various Special Interest Groups (SIGs) across categories like Environment, Gun Control, and Reproductive Rights.

### 3. Insert as Ideological Baselines
Transform the ratings into the database as "Words" or ideological priors. A 100% rating from the NRA implies a stated position in favor of gun rights. This provides the baseline for the LLM to score actual legislative "Actions" against.

## When to Use
- Fetching interest group ratings for politicians
- Building ideological baselines for Honesty Engine
- Mapping Vote Smart candidateId to Master Identity
- Quantifying stated positions from SIG endorsements

## Limitations
- Requires VOTESMART_API_KEY in .env
- Vote Smart API may have rate limits
- candidateId must be mapped from congress-legislators
- Ratings are 0-100% scale; interpretation needed
- Not all politicians have comprehensive ratings
