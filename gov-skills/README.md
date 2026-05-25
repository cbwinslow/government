# govinfo.gov + congress.gov ingestion skill pack

This pack contains two comprehensive reusable skills for VS Code/Cline/agent workflows focused on:

1. `govinfo-ingestion-admin`
2. `congressgov-ingestion-admin`

It also includes:
- VS Code prompt files
- MCP server configuration templates
- environment templates
- database bootstrap SQL
- Python ingestion scaffold
- operational runbooks

## Verified platform notes
- GovInfo provides a public developer hub, API, bulk data repository, link service, feeds, sitemaps, and a public-preview MCP server. GovInfo uses an `api.data.gov` key for API access.
- GovInfo bulk data can be accessed via `/bulkdata/xml/...` and `/bulkdata/json/...` endpoints, and bulk XML exists for collections including Congressional Bill Text, Bill Status, Bill Summaries, CFR, eCFR, and Federal Register.
- Congress.gov API v3 returns XML or JSON, requires an API key, has a 5,000 requests/hour rate limit, and supports up to 250 results per request.

See docs/source-notes.md for source-backed implementation notes.
