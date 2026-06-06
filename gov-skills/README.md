# OpenDiscourse Skill & Prompt Packs

Two complementary packs for government data ingestion, political intelligence, and honesty scoring.

---

## Pack 1: gov-skills (Legislative + Analysis)

Core legislative data ingestion and Honesty Engine analysis.

### Skills (10)
| Skill | Purpose |
|-------|---------|
| `govinfo-ingestion-admin` | GovInfo API and bulk data ingestion |
| `congressgov-ingestion-admin` | Congress.gov API v3 integration |
| `courtlistener-skill` | Courtlistener legal history extraction |
| `financial-disclosures-skill` | Financial disclosure PDF processing |
| `database-population-agent` | Entity resolution and DB population |
| `gdelt-news-ingestion` | GDELT news monitoring and quote extraction |
| `honesty-engine-scorer` | LLM-based consistency scoring engine |
| `qdrant-vector-embedding-admin` | Qdrant vector store and embeddings |
| `fastapi-dashboard-admin` | FastAPI backend and React dashboard |
| `infrastructure-ops-admin` | Docker, PostgreSQL, Redis, Celery ops |

### Prompts (3 files, 28 prompts)
- `vscode-prompts.md` — 8 original GovInfo/Congress prompts
- `honesty-engine-prompts.md` — 10 new scoring/pipeline prompts
- `ingestion-admin-prompts.md` — 10 new ingestion/admin prompts

---

## Pack 2: politician-finance-pack (Financial + Ethics)

Campaign finance, personal financial disclosure, and conflict-of-interest tracking.

### Skills (4)
| Skill | Purpose |
|-------|---------|
| `politician-masterdata-admin` | Member/person identity tracking |
| `campaign-finance-ingestion-admin` | Campaign finance data ingestion |
| `financial-disclosure-ingestion-admin` | Financial disclosure tracking |
| `member-tracking-rag-admin` | LlamaIndex RAG integration |

### Prompts (2 files, 17 prompts)
- `vscode-prompts.md` — 7 original prompts
- `conflict-analytics-prompts.md` — 10 new conflict/ethics prompts

---

## Verified platform notes
- GovInfo provides a public developer hub, API, bulk data repository, link service, feeds, sitemaps, and a public-preview MCP server. GovInfo uses an `api.data.gov` key for API access.
- GovInfo bulk data can be accessed via `/bulkdata/xml/...` and `/bulkdata/json/...` endpoints.
- Congress.gov API v3 returns XML or JSON, requires an API key, has a 5,000 requests/hour rate limit, and supports up to 250 results per request.
- OpenFEC provides a RESTful API for FEC campaign finance data.
- House financial disclosures and PTRs are filed through fd.house.gov and made available through the Clerk/House disclosure systems.
- PTRs are required within 45 days after qualifying transactions.
- OpenRouter provides access to LLMs for the Honesty Engine (free 405B + paid fallbacks).

## Quick start
```bash
# Infrastructure
docker-compose up -d

# Seed database
python -m opendiscourse.models.database
python src/opendiscourse/ingestion/seed_identities.py

# Configure API keys in .env
cp .env.example .env

# Install dependencies
uv sync
```

See docs/source-notes.md for source-backed implementation notes.