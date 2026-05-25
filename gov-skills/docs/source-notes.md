# Source-backed notes

These notes reflect the current public documentation reviewed for this pack.

## GovInfo
- Developer hub: https://www.govinfo.gov/developers
- API docs: https://api.govinfo.gov/docs/
- GovInfo uses an api.data.gov API key.
- GovInfo Developer Hub states that GPO has a GovInfo MCP server in public preview.
- GovInfo bulk data supports XML and JSON listings by adding `/xml` or `/json` after `bulkdata` paths.
- Bulk XML availability includes Congressional Bill Text, Congressional Bill Status, Congressional Bill Summaries, CFR, eCFR, Federal Register, U.S. Government Manual, Privacy Act Issuances, and House Rules and Manual.

## Congress.gov
- API repo: https://github.com/LibraryOfCongress/api.congress.gov/
- API docs landing: https://api.congress.gov/
- Congress.gov API current version is v3.
- Responses are available in XML or JSON.
- API key is required.
- Rate limit is 5,000 requests per hour.
- Default page size is 20 and max limit is 250.
