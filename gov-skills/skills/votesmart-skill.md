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
