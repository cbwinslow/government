# Data Sources

The canonical OpenDiscourse source registry and acquisition priorities are maintained in [`SOURCE_CATALOG.md`](SOURCE_CATALOG.md).

This compatibility document exists because early project documentation referenced `DATA_SOURCES.md`. New source-specific design notes should be added under `docs/sources/` and linked from the canonical source catalog.

Every source entry must eventually record:

- authoritative owner and source URLs;
- available bulk, API, feed, sitemap, archive, and database-dump interfaces;
- authentication and rate limits;
- formats, identifiers, update cadence, and expected coverage;
- license, attribution, and redistribution constraints;
- discovery, checkpoint, and reconciliation strategies;
- upstream reference repositories and the exact revisions reviewed.
