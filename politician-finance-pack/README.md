# politician finance + legislative intelligence pack

This pack expands the earlier GovInfo/Congress.gov work into a broader politician-tracking platform with:

- member/person identity tracking
- politician master database design
- campaign finance ingestion
- financial disclosure ingestion
- transaction/investment tracking
- LlamaIndex ingestion + retrieval scaffolding
- Qdrant and pgvector integration assets
- MCP server config templates
- VS Code prompts, tasks, and launch configs

## Included skill modules
- `politician-masterdata-admin`
- `campaign-finance-ingestion-admin`
- `financial-disclosure-ingestion-admin`
- `member-tracking-rag-admin`

## Verified source notes
- OpenFEC provides a RESTful API for FEC campaign finance data. See https://api.open.fec.gov/developers/
- House financial disclosures and PTRs are filed through fd.house.gov and are made available through the Clerk/House disclosure systems. See https://ethics.house.gov/financial-disclosure/ and https://disclosures-clerk.house.gov
- Public financial disclosure PTR timing requirements are described by OGE, including the 45-day filing rule. See https://www.doi.gov/ethics/public-financial-disclosures-frequently-asked-questions
- Congress.gov API v3 requires an API key, supports XML/JSON, rate limit 5,000/hour, and up to 250 results per request. See api.congress.gov documentation/repository.
- GovInfo provides API, bulk data, and developer services for legislative and government documents. See GovInfo developer documentation.
