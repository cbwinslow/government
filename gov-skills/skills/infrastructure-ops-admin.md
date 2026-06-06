# Skill: infrastructure-ops-admin

## Purpose
Use this skill when managing the OpenDiscourse infrastructure: Docker Compose services, PostgreSQL setup and maintenance, Qdrant operations, Redis configuration, environment configuration, and CI/CD workflows.

## Infrastructure services
All services are defined in `docker-compose.yml` at the workspace root:

| Service | Image | Purpose | Ports |
|---------|-------|---------|-------|
| PostgreSQL | `ankane/pgvector` | Relational database + vector extension | 5432 |
| Qdrant | `qdrant/qdrant` | Vector search engine | 6333, 6334 |
| Redis | `redis:7-alpine` | Task queue / Celery broker | 6379 |

## PostgreSQL management

### Bootstrap
```bash
docker-compose up -d postgres
# Run seed script to create schemas and tables
python -m opendiscourse.models.database
# Seed politician identities from OpenStates YAML data
python src/opendiscourse/ingestion/seed_identities.py
```

### Schema patterns
The project uses these PostgreSQL schemas (documented across skills):

| Schema | Purpose | Owned By |
|--------|---------|----------|
| `public` | Core politician identity | `opendiscourse` |
| `master` | Person/org canonical identity | `politician-finance-pack` |
| `leg` | Legislative entities | `congressgov-ingestion-admin` |
| `finance` | Campaign finance | `campaign-finance-ingestion-admin` |
| `disclosure` | Personal financial disclosures | `financial-disclosure-ingestion-admin` |
| `rag` | Embeddings and retrieval | `member-tracking-rag-admin` |
| `ingest` | Ingestion job tracking | shared |
| `raw` | Immutable raw payloads | shared |
| `core` | Cleaned relational entities | shared |
| `mart` | Analytics/reporting views | shared |

### Maintenance checks
- Monitor bloat on landing tables: `SELECT schemaname, tablename, n_dead_tup FROM pg_stat_user_tables`
- Check long-running queries: `SELECT pid, now() - pg_stat_activity.query_start, query FROM pg_stat_activity WHERE state = 'active'`
- Verify pgvector extension: `SELECT * FROM pg_extension WHERE extname = 'vector'`
- Run VACUUM ANALYZE after large bulk inserts.

## Qdrant operations

### Health check
```bash
curl http://localhost:6333/healthz
```

### Collection management
```bash
# List collections
curl http://localhost:6333/collections

# Delete and recreate
python -c "from qdrant_client import QdrantClient; QdrantClient('http://localhost:6333').delete_collection('congress_bills')"
```

### Backup
Qdrant data is stored in the `qdrant_data` Docker volume. To backup:
```bash
docker run --rm -v gov_qdrant:/source -v $(pwd)/backups:/dest alpine tar czf /dest/qdrant-$(date +%Y%m%d).tar.gz -C /source .
```

## Redis operations
- Used for Celery task queue and caching.
- Monitor: `redis-cli INFO stats` or `docker exec gov_redis redis-cli INFO stats`.
- Flush cache: `docker exec gov_redis redis-cli FLUSHDB` (only flush the cache DB, not the queue).

## Environment configuration
The `.env` file at the workspace root controls all service configuration:

```bash
# Database
POSTGRES_USER=govadmin
POSTGRES_PASSWORD=govpassword
POSTGRES_DB=govdata

# Qdrant
QDRANT_URL=http://localhost:6333

# API Keys
CONGRESS_API_KEY=your_key_here
OPENSTATES_API_KEY=your_key_here
OPENSECRETS_API_KEY=your_key_here
VOTESMART_API_KEY=your_key_here

# LLM
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

## Celery task management
```bash
# Start Celery worker
celery -A src.opendiscourse worker -l info

# Monitor Celery queues
celery -A src.opendiscourse inspect active
celery -A src.opendiscourse inspect scheduled

# Purge all tasks
celery -A src.opendiscourse purge -f
```

## Prompts
- "Check all infrastructure services are healthy and report any issues."
- "Set up the PostgreSQL database with all schemas from the fintech and gov-skills packs."
- "Rebuild the Qdrant collections from scratch with the BGE-large embedding model."
- "Create a Docker Compose override for production with resource limits and healthchecks."
- "Monitor the Celery task queue and report any stuck or failed tasks."
- "Backup both PostgreSQL and Qdrant data and verify the backups."