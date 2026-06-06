# OpenSecrets API Ingestion Skill

## Overview
This skill instructs agents on how to pull Campaign Finance, PACs, and Donor data from the OpenSecrets API to track political financial dependencies.

## Setup
- **API Endpoint:** `https://www.opensecrets.org/api/`
- **Authentication:** Obtain the API key from the `.env` file under `OPENSECRETS_API_KEY`. Do not hardcode this key.

## Execution Steps

### 1. Map CID (Center for Responsive Politics ID)
OpenSecrets uses a `CID` to identify politicians. This CID maps exactly to the `opensecrets` field in our Master Identity YAML (`congress-legislators/legislators-current.yaml`).

### 2. Fetch Top Donors
Use the `candContrib` method.
- **Endpoint:** `/?method=candContrib&cid=[CID]&cycle=[YEAR]&apikey=[KEY]`
- **Goal:** Extract the top 10 contributing organizations to this politician per election cycle.
- **Database Action:** Insert as financial "Actions" linked to the politician's identity.

### 3. Fetch Industry Contributions
Use the `candSector` or `candIndustry` method to understand which broad industries (e.g., "Defense", "Pharmaceuticals") are funding them. This is critical for context when evaluating "Honesty" on related bills.

### 4. Rate Limiting
Respect the OpenSecrets API limits (typically 200 calls per day for free tiers). Implement caching (e.g., Redis) so we don't query the same CID repeatedly on the same day.
